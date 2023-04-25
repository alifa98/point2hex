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
    def __init__(self, df_traj, hex_resolution, hirachical:bool, output_fname:str) -> None:
        self.df_traj = df_traj
        self.hex_resolution = hex_resolution
        self.hirachical = hirachical #whether to have hirachical tessellation
        self.output_fname = output_fname #whether output to a csv file
        
    # Evaluate the format of list of points, and convert str to list
    def eval_points(self, route_points):
        points = ast.literal_eval(route_points)
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

        # Get hirachical tessellation
        if self.hirachical:
            coarse_traj = self.hirachical_tessellation(count_dict)
            self.df_traj['coarse_trajectory'] = coarse_traj
            coarse_candidates = [i for sublist in coarse_traj for i in sublist.split()] 
            coarse_count_dict = Counter(coarse_candidates)
            print(f'Coarse vocab size: {len(coarse_count_dict)}')
            distution.plot_dist(coarse_count_dict, "output/figs/", "coarse")

        # Save sequence to csv file
        if self.output_fname:
            if not os.path.exists("./output/"):
                os.makedirs('./output/') 
            df_output = self.df_traj.drop(["points", "route_points", "geometry"], axis=1)
            df_output.to_csv('./output/' + self.output_fname, index=False)
            print("Sequence csv file successfully saved")
        
        return self.df_traj
        
        
    # TODO: hirachical hex seq, starting from 7, recursively make the distribution uniform
    # Need to reimplement
    def hirachical_tessellation(self, count_dict) -> list:
        count_count = Counter(count_dict.values())
        print(f'count occurence of occurence: {count_count}')
        
        coarse_hex = dict()
        for hex,c in count_dict.items():  
            if c == 1:   
                parent = h3.cell_to_parent(hex, self.hex_resolution-3)
                coarse_hex[hex] = parent
            elif c == 2:
                parent = h3.cell_to_parent(hex, self.hex_resolution-2)
                coarse_hex[hex] = parent
            elif c == 3:
                parent = h3.cell_to_parent(hex, self.hex_resolution-1)
                coarse_hex[hex] = parent
            
        coarse_traj = []
        keys = coarse_hex.keys()
        for _, val in self.df_traj['trajectory'].items():
            new_seq = []
            for j, hex in enumerate(val.split()):
                if hex in keys:
                    parent = coarse_hex[hex]
                    if j==0 or parent != new_seq[-1]:
                        new_seq.append(parent)
                else:
                    new_seq.append(hex)
        
            coarse_traj.append(" ".join(new_seq))

        assert len(coarse_traj) == len(self.df_traj)
        return coarse_traj


if __name__ == '__main__':
    zip_file = zipfile.ZipFile('./data/test.csv.zip')
    df = pd.read_csv(zip_file.open("test.csv"))
    myhex_seq = Points2h3(df, 9, True, "test.csv")
    myhex_seq.get_hexseq()
    
