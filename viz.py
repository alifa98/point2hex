import json
import pandas as pd 
import h3

from shapely.geometry import Polygon
import plotly.express as px
from geojson import Feature, FeatureCollection

class Seqviz(object):
    def __init__(self, hex_seq:list) -> None:
        self.hex_seq = hex_seq


    #create a GeoJSON-formatted dictionary using Dataframe, in order to use Plotly express choropleth_mapbox to build map
    def hexagons_dataframe_to_geojson(self, df_hex, hex_id_field, geometry_field, value_field, file_output = None):

        list_features = []

        for i, row in df_hex.iterrows():
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
        points = h3.h3_to_geo_boundary(row['hex_id'], True)
        return Polygon(points)
    

    def plot(self):
        #construct a df
        df_hex_plot = pd.DataFrame(self.hex_seq, columns=['hex_id'])
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
                        value_field='sequence',
                        geometry_field='geometry'))

        #plot
        fig = (px.choropleth_mapbox(
                            df_hex_plot, 
                            geojson=geojson_obj, 
                            locations='hex_id', 
                            color='sequence',
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



if __name__ == '__main__':
    sample = ['892a1008b27ffff', '892a100d6cbffff', '892a100d6cfffff', '892a100d6c7ffff', '892a100d613ffff', '892a100d68bffff', '892a100d683ffff']
    viz_seq = Seqviz(sample)
    viz_seq.plot()

