import argparse
import os
import pandas as pd
from lib.viz import Seqviz

parser = argparse.ArgumentParser(
    description='Generate hexagon heatmap from trajectory data')

parser.add_argument('input_file', help='Input file path')
parser.add_argument('-z', '--zoom', type=float, default=12,
                    help='The zoom level of the map')
args = parser.parse_args()


#create the plot directly from the hex sequence
os.makedirs('out/plots', exist_ok=True)

traj_seq = pd.read_csv(args.input_file)
viz_seq = Seqviz(traj_seq['higher_order_trajectory'].tolist(), 'heatmap')
# viz_seq = Seqviz(traj_seq['higher_order_trajectory'][1], 'seq')
viz_seq.show_map(args.zoom)
