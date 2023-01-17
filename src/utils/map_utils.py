# plot map parts
import folium
import branca.colormap as cms
import pandas as pd
import copy



def plot_map(df, 
             what_to_plot='amount_pc',region_to_plot='Name',
             json_path='.src/utils/map_data/combined_json.json',
             longitude=-3.1, latitude=54.1):
    """
    loads a KML location file (from local file or url) 
    and then saves this as a json file locally
    
    Args: df (pandas dataframe) dataframe with location (region_to_plot) related to json file
                in one column and data to plot (what_to_plot) in another
          what_to_plot/region_to_plot (string) columns in df
          json_path (file path) the path to the json file
          longitude/latitude (float) for the centre of the map
    Returns: 
        The folium map
    
    """
    # create a basic map
    # This sets the basic look of the map
    # things like the zoom, color scheme, where the map is centred etc

    m = folium.Map(location=[latitude,longitude], 
                   zoom_start=5,
                   control_scale=True,
                   tiles="Stamen Toner")
    
    folium.TileLayer('CartoDB positron',name="Light Map",control=False).add_to(m)
    
    """
    Create the Choropleth part:

    - This creates the Choropleth map (i.e. regions on a map of different color based on their value)
    - json_path this is the path to a json file with the location data
        - key_on= "feature.properties.Name" refers to the json file
        - and needs to match region_to_plot in columns=[region_to_plot,what_to_plot]
    - data the data normally a pandas dataframe
        - the columns are region_to_plot and what_to_plot
        - what_to_plot are the values to plot
        - region_to_plot should match the json file
    """

    choropleth = folium.Choropleth(
        geo_data=json_path,
        name='choropleth',
        legend_name= what_to_plot,
        data= df,
        columns=[region_to_plot,what_to_plot],
        key_on= "feature.properties.Name",
        fill_color='YlGn',
    ).add_to(m)
    
    # adds ability to see names of regions on mouseove
    choropleth.geojson.add_child(
    folium.features.GeoJsonTooltip(['Name'],labels=False)
    )
    
    return m

