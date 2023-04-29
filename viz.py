import json
import pandas as pd 
from collections import Counter
import matplotlib as mpl
import matplotlib.pyplot as plt

import h3
import plotly.express as px
from shapely.geometry import Polygon
from geojson import Feature, FeatureCollection

class Seqviz(object):
    def __init__(self, hex_seq:list, plot_type:str) -> None:
        self.hex_seq = hex_seq
        self.plot_type = plot_type

    #create a GeoJSON-formatted dictionary using Dataframe, in order to use Plotly express choropleth_mapbox to build map
    def hexagons_dataframe_to_geojson(self, df_hex, hex_id_field, geometry_field, value_field, file_output = None):

        list_features = []

        for _, row in df_hex.iterrows():
            feature = Feature(geometry = row[geometry_field],
                            id = row[hex_id_field],
                            properties = {"value": row[value_field]})
            list_features.append(feature)

        feat_collection = FeatureCollection(list_features)

        if file_output is not None:
            with open(file_output, "w") as f:
                json.dump(feat_collection, f)

        else :
            return feat_collection

    #generate hexagon geometry for each hex
    def add_geometry(self, row):
        points = h3.cell_to_boundary(row['hex_id'], True)
        return Polygon(points)

    def show_map(self):
        #construct a df
        if self.plot_type == 'heatmap':
            candidates = [i for sublist in self.hex_seq for i in sublist.split()] 
            df_hex_plot = pd.DataFrame(Counter(candidates).items(), columns=['hex_id', 'count'])
            df_hex_plot['geometry'] = df_hex_plot.apply(self.add_geometry, axis=1)
        else:
            df_hex_plot = pd.DataFrame(self.hex_seq.split(), columns=['hex_id'])
            df_hex_plot['geometry'] = df_hex_plot.apply(self.add_geometry, axis=1)
            df_hex_plot['sequence'] = range(1, 1+len(df_hex_plot))

        #get the lat and lon for the map center
        xx, yy = (df_hex_plot['geometry'][0]).exterior.coords.xy
        lon = xx[0]
        lat = yy[0]

        #create geojson
        geojson_obj = (self.hexagons_dataframe_to_geojson
                        (df_hex_plot,
                        hex_id_field='hex_id',
                        value_field='count' if self.plot_type == 'heatmap' else 'sequence',
                        geometry_field='geometry'))

        #plot
        fig = (px.choropleth_mapbox(
                            df_hex_plot, 
                            geojson=geojson_obj, 
                            locations='hex_id', 
                            color='count' if self.plot_type == 'heatmap' else 'sequence',
                            # color_continuous_scale="Viridis",
                            # range_color=(0,df_traj_plot['queue'].mean() ),                  
                            mapbox_style='carto-positron',
                            zoom=12,
                            center = {"lat": lat, "lon": lon},
                            opacity=0.7,
                            labels={'seq of hex'})
            )
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig.show()


class Distviz(object):
    def plot_dist(self, count_dict, store_dir=None, filename=""):
        total = sum(count_dict.values())
        count_tuple = sorted(count_dict.items(), key=lambda item: item[1], reverse=True)
        # distribution_tuple = [(item[0], item[1]/total) for item in count_tuple]
            
        mpl.rcParams.update({'font.size': 16})

        x_axis = range(len(count_tuple))
        plt.bar(x_axis, [i[1] for i in count_tuple] ) 
        plt.title("")
        plt.xlabel("hexagons (size: " + str(x_axis) + ")")
        plt.ylabel("counts")
        # plt.legend()
        plt.xticks([])
        plt.gca().xaxis.set_tick_params(length=0)
        plt.gcf().tight_layout()

        filename += "_hex_dist.png"
        if store_dir is not None:
            filename = store_dir.rstrip("/") + "/" + filename
        plt.savefig(filename)
        # plt.show()        


if __name__ == '__main__':
    sample = ['892a1008b27ffff', '892a100d6cbffff', '892a100d6cfffff', '892a100d6c7ffff', '892a100d613ffff', '892a100d68bffff', '892a100d683ffff']
    viz_seq = Seqviz(sample, "seq")
    viz_seq.show_map()

