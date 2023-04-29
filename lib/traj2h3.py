import os
import sys
import ast
import zipfile
import pandas as pd
from typing import Iterator
from collections import Counter

import h3
from shapely.geometry import LineString

from viz import Distviz

class Points2h3(object):
    def __init__(self, df_traj, hex_resolution, output_fname:str) -> None:
        self.df_traj = df_traj
        self.hex_resolution = hex_resolution
        self.output_fname = output_fname #whether output to a csv file
        
    # Evaluate the format of list of points, and convert str to list
    def eval_points(self, route_points):
        points = ast.literal_eval(str(route_points))
        if isinstance(points, list):
            return points
        else:
            print("Please check if the input df has route_points column, which should be list of tuples")
            sys.exit()
        
    # Get hex sequence
    def get_hexseq(self):
        # Drop rows with no data in the brackets
        self.df_traj = self.df_traj[self.df_traj['route_points'].apply(lambda x: len(x) > 2)]

        self.df_traj['points'] = self.df_traj['route_points'].apply(lambda x: self.eval_points(x))

        # Drop rows with only one pair of points
        self.df_traj = self.df_traj[self.df_traj['points'].apply(lambda x: len(x) > 2)].reset_index(drop=True) 

        self.df_traj['geometry'] = self.df_traj['points'].apply(lambda x: LineString(x))
        print("lineString generated")


        # Generate hex sequence from linestring
        def sequential_deduplication(func: Iterator[str]) -> Iterator[str]:
            '''
            Decorator that doesn't permit two consecutive items to be the same
            '''
            def inner(*args):
                iterable = func(*args)
                last = None
                while (cell := next(iterable, None)) is not None:
                    if cell != last:
                        yield cell
                    last = cell
            return inner

        @sequential_deduplication # prevent consecutive repetition, esp. at low res
        def h3polyline(line: LineString, resolution: int) -> Iterator[str]:
            '''
            Iterator yielding H3 cells representing a line,
            retaining order and any self-intersections
            '''
            coords = zip(line.coords, line.coords[1:])
            while (vertex_pair := next(coords, None)) is not None:
                i, j = vertex_pair
                a = h3.latlng_to_cell(i[1], i[0], resolution)
                b = h3.latlng_to_cell(j[1], j[0], resolution)
                yield from h3.grid_path_cells(a, b) # inclusive of a and b


        self.df_traj['trajectory'] =  self.df_traj['geometry'].apply(lambda x: ' '.join(h3polyline(x, self.hex_resolution)))
        print("Initial hex sequence generated")

        candidates = [i for sublist in self.df_traj['trajectory'].tolist() for i in sublist.split()] 
        count_dict = Counter(candidates)
        print(f'Initial vocab size: {len(count_dict)}')
        distution = Distviz()
        if not os.path.exists("./output/figs/"):
            os.makedirs("./output/figs/")
        distution.plot_dist(count_dict, "output/figs/", str(self.hex_resolution))


        # Save sequence to csv file
        if self.output_fname:
            if not os.path.exists("./output/"):
                os.makedirs('./output/') 
            df_output = self.df_traj.drop(["points", "route_points", "geometry"], axis=1)
            df_output.to_csv('./output/' + self.output_fname, index=False)
            print("Sequence csv file successfully saved")
        
        return self.df_traj


if __name__ == '__main__':
    zip_file = zipfile.ZipFile('./data/test.csv.zip')
    df = pd.read_csv(zip_file.open("test.csv"))
    myhex_seq = Points2h3(df, 9, "test.csv")
    myhex_seq.get_hexseq()
    
