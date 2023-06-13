import os
from typing import Iterator
import h3
import swifter
from shapely.geometry import LineString
import pickle

class Points2h3(object):
    def __init__(self, df_traj, output_dir, column_name) -> None:
        self.df_traj = df_traj
        self.output_dir = output_dir
        self.column_name = column_name

    def pre_process(self):
        print("dropping rows which cannot create a LineString...")
        self.df_traj = self.df_traj[self.df_traj[self.column_name].swifter.apply(
            lambda x: len(eval(x)) > 1)]
        
        self.df_traj.reset_index()
        print("single-point rows are dropped. size of data frame: ", self.df_traj.shape)

    def get_hexseq(self, res):
        
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

        @sequential_deduplication  # prevent consecutive repetition, esp. at low res
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
                yield from h3.grid_path_cells(a, b)  # inclusive of a and b

        print("Generating hex sequence...")
        new_hexagon_column = self.df_traj[self.column_name].swifter.apply(
            lambda x: ' '.join(h3polyline(LineString(eval(x)), res)))

        #making a deep copy to be saved:
        df_copy = pickle.loads(pickle.dumps(self.df_traj)) 
        df_copy['higher_order_trajectory'] = new_hexagon_column
        df_copy = df_copy.drop([self.column_name], axis=1)
        df_copy.to_csv(os.path.join(self.output_dir,f"output-res{res}.csv"), index=False)
        print("Sequence csv file successfully saved:", os.path.join(self.output_dir,f"output-res{res}.csv"))