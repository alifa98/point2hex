import ast
from typing import Iterator
import h3
from shapely.geometry import LineString


class Points2h3(object):
    def __init__(self, df_traj, hex_resolution, output_fname, column_name) -> None:
        self.df_traj = df_traj
        self.hex_resolution = hex_resolution
        self.output_fname = output_fname  # whether output to a csv file
        self.column_name = column_name

    # Evaluate the format of list of points, and convert str to list
    def eval_points(self, route_points):
        points_list = ast.literal_eval(str(route_points))
        if isinstance(points_list, list):
            return points_list
        else:
            raise Exception(
                "Please check if the input df has route_points column, which should be list of tuples")

    # Get hex sequence
    def get_hexseq(self):
        # Drop rows with no data in the brackets
        self.df_traj = self.df_traj[self.df_traj[self.column_name].apply(
            lambda x: len(eval(x)) > 1)]

        self.df_traj['points#tempHex2Rand'] = self.df_traj[self.column_name].apply(
            lambda x: self.eval_points(x))

        # Drop rows with only one pair of points
        # self.df_traj = self.df_traj[self.df_traj['points'].apply(lambda x: len(x) > 2)].reset_index(drop=True)

        self.df_traj['geometry#tempHexRand'] = self.df_traj['points#tempHex2Rand'].apply(
            lambda x: LineString(x))
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

        self.df_traj['higher_order_trajectory'] = self.df_traj['geometry#tempHexRand'].apply(
            lambda x: ' '.join(h3polyline(x, self.hex_resolution)))
        print("Initial hex sequence generated")

        # Save sequence to csv file
        df_output = self.df_traj.drop(
            ["points#tempHex2Rand", self.column_name, "geometry#tempHexRand"], axis=1)
        df_output.to_csv(self.output_fname, index=False)
        print("Sequence csv file successfully saved")

        return self.df_traj


# if __name__ == '__main__':
#     zip_file = zipfile.ZipFile('./data/test.csv.zip')
#     df = pd.read_csv(zip_file.open("test.csv"))
#     myhex_seq = Points2h3(df, 9, "test.csv")
#     myhex_seq.get_hexseq()
