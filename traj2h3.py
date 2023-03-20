import os
import sys
import ast
import zipfile
import pandas as pd
from typing import Iterator

import h3
from shapely.geometry import LineString

from viz import Seqviz

class Points2h3(object):
    def __init__(self, df_traj, hex_resolution, plot_heatmap:bool, output_fname:str) -> None:
        self.df_traj = df_traj
        self.hex_resolution = hex_resolution
        self.plot_heatmap = plot_heatmap #whether plot heatmap or plot one seq
        self.output_fname = output_fname #whether output to a csv file
        
    # Evaluate the format of list of points, and convert str to list
    def eval_points(self, route_points):
        if isinstance(route_points, list): return route_points
        else:
            points = ast.literal_eval(route_points)
            if isinstance(points, list): return points
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
                a = h3.geo_to_h3(*i[::-1], resolution)
                b = h3.geo_to_h3(*j[::-1], resolution)
                yield from h3.h3_line(a, b) # inclusive of a and b


        self.df_traj['trajectory'] =  self.df_traj['geometry'].apply(lambda x: ' '.join(h3polyline(x, self.hex_resolution)))
        print("hex sequence generated")

        if self.output_fname:
            if not os.path.exists("./output/"):
                os.makedirs('./output/') 
            df_output = self.df_traj.drop(["points", "route_points", "geometry"], axis=1)
            df_output.to_csv('./output/' + self.output_fname, index=False)
            print("sequence csv file successfully saved")
    
       if self.plot_heatmap:
            viz_seq = Seqviz(self.df_traj['trajectory'].tolist(), True)
        else:
            viz_seq = Seqviz(self.df_traj['trajectory'][0], False)
        
        viz_seq.plot()

        return self.df_traj


if __name__ == '__main__':
    zip_file = zipfile.ZipFile('./data/porto/test.csv.zip')
    df = pd.read_csv(zip_file.open("test.csv"))
    myhex_seq = Points2h3(df, 9, False, "babytest.csv")
    myhex_seq.get_hexseq()
    
