# plot map parts
import folium
import branca.colormap as cms
import pandas as pd
import copy


def get_poscode_df(path_to_csv= ".//src//utils//map_data//postcode_to_region.csv",
                    usecols=['Postcode','mapArea']):
    """
    loads poscode data and returns that as a dataframe
    
    Args:   path_to_csv (path) csv file of postcode data
            usecols (list[str]) what columns to load, also includes latitude,longitude
    Returns: 
        postcodes_df (pd.DataFrame) pandas dataframe of the postcode data
    
    """
    postcodes_df = pd.read_csv(path_to_csv,
                                usecols=usecols)
    return postcodes_df

def _getpc(postcodes_df_temp, colname):
    """
    Helper function to identify the region when a postcode is across multiple regions
    Does this by selecting region that has most postcodes
    e.g. BH1 8L is in two areas (A and B), area A is in 3 times and B in 5 times, 
        so B is selected as the area

    Args:   postcodes_df_temp (pd.DataFrame) dataframe of postcode data
            colname (str) what column to process some variant of postcode
    Returns: 
        postcode_short (pd.DataFrame) modified dataframe with new variable mapArea
    """
    postcodes_df_temp = postcodes_df_temp.groupby(by=[colname,'mapArea'], as_index=False).count()

    postcode_short = postcodes_df_temp.sort_values('Postcode', ascending=False).drop_duplicates([colname])
    
    postcode_short = postcode_short.loc[:,[colname,'mapArea']].reset_index(drop=True)
    return postcode_short

def get_postcode_list(path_to_csv= "..//src//utils//map_data//postcode_to_region.csv",
                    usecols=['Postcode','mapArea'],
                    reduce_p_max=4
                    ):
    """
    loads poscode data and returns that as a list of dataframes
    where postcode has has been reduced by 1:reduce_p_max-1 in length
    
    Args:   path_to_csv (path) csv file of postcode data
            usecols (list[str]) what columns to load, also includes latitude,longitude
            reduce_p_max (int) number of chars to take off end of potscode -1
    Returns: 
        list_postcodes_df (list[pd.DataFrame]) list of pandas dataframe of the postcode data
    
    """   

    postcodes_df = get_poscode_df(path_to_csv, usecols)

    postcodes_df_temp = postcodes_df.copy()
    
    list_postcodes_df = []
    list_postcodes_df.append( postcodes_df_temp.copy() )
    
    for i in range(1,reduce_p_max):
        colname = f"Postcode_m{i}"
        postcodes_df_temp[colname] = postcodes_df_temp['Postcode'].str[:-i]    
        
        df = _getpc(postcodes_df_temp, colname)
        df = df.rename(columns={colname:'Postcode'})
        list_postcodes_df.append( df )
    
    
    return list_postcodes_df

def postcode_to_area(df_,
                    postcodes_df, 
                    postcode_column='Postcode',
                    removeChar=0):

    df=copy.deepcopy(df_)
    """
    loads poscode data and returns that as a list of dataframes
    where postcode has has been reduced by 1:reduce_p_max-1 in length
    
    Args:   path_to_csv (path) csv file of postcode data
            usecols (list[str]) what columns to load, also includes latitude,longitude
            reduce_p_max (int) number of chars to take off end of potscode -1
    Returns: 
        list_postcodes_df (list[pd.DataFrame]) list of pandas dataframe of the postcode data
    
    """      
    postcode_dict = dict(postcodes_df.values)

    if removeChar>0:
        df[postcode_column] = df[postcode_column].str[:-removeChar]
    
    df['area_to_plot'] = df.loc[:,postcode_column].map(postcode_dict)

    return df



def plot_map(df, 
             what_to_plot='amount_pc',region_to_plot='Name',
             json_path='./_data/region.json',
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

