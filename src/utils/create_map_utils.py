import os
# geometry data
import fiona
import geopandas as gpd
import json

# general - working with dataframes and numbers
import pandas as pd
import numpy as np

import os

# plot map parts
import folium
import branca.colormap as cm

wales_region_dict={ 
     'Wrexham':'North Wales', 
     'Conwy':'North Wales', 
     'Gwynedd':'North Wales', 
     'Isle of Anglesey':'North Wales',
     'Flintshire':'North Wales', 
     'Denbighshire':'North Wales', 
     'Powys':'Mid Wales',
     'Ceredigion':'Mid Wales',
     'Carmarthenshire':'South West Wales',
     'Swansea':'South West Wales',
     'Neath Port Talbot':'South West Wales',
     'Pembrokeshire':'South West Wales',
     'Bridgend':'South Wales',
     'Vale of Glamorgan':'South Wales',
     'Cardiff':'South Wales',
     'Rhondda Cynon Taf':'South Wales',
     'Merthyr Tydfil':'South Wales',
     'Caerphilly':'South East Wales',
     'Newport':'South East Wales',  
     'Torfaen':'South East Wales', 
     'Monmouthshire':'South East Wales',    
     'Blaenau Gwent':'South East Wales',
     
    }
    
    
def main(save_dir='./map_data'):
    """
    Creates files:
    - json file of UK areas and polygons
    - a postcode mapper dataframe to convert postcode to area for plotting
    These are saved locally
    
    """    
    
    # the kml polygon files to use to convert to json
    url_data_paths = ['https://www.doogal.co.uk/kml/counties/Counties.kml',
                  '.\\_data\\scotland_preg_2011.KML',
                  '.\\_data\\WalesDistrict.kml',
                  'https://www.doogal.co.uk/kml/UkPostcodes.kml']
                  
    country=['England', 'Scotland', 'Wales', 'Northern Ireland']
    save_dir
    # below the data above is used to create a json file and saved locally
    url_KML_map(url_data_paths, 'combined_json', 
                doScotWales=country,
                save_dir = save_dir)

    # a mapper dataframe of postcode -> area is created anf then saved
    postcode_df = load_pcode_csvs()
    
    postcode_df.to_csv(os.path.join(save_dir,"postcode_to_region.csv"))
    
    
def load_kml(url_data):
    """
    loads a KML location file (from local file or url) 
    and then returns a geopandas dataframe
    
    Args: url_data (file path) the path to the kml file,
          
    Returns: 
        the geopandas dataframe
    
    """
    # so can use kml files
    fiona.drvsupport.supported_drivers['KML'] = 'rw'

    # load the kl file to a gpd df
    gdf = gpd.read_file(url_data, driver=fiona.drvsupport.supported_drivers['KML'])

    return gdf
    
def gdf_create_json(gdf, loc_save='./_data', fname='region.json'):
    """
    loads a KML location file (from local file or url) 
    and then saves this as a json file locally
    
    Args: 
          loc_save (directory path) the location to save the data
          fname (file name string) the file name of the json file
    Returns: 
        Names the regions in the json file
        file path to the json file
    """
        
    # Save as a json file to load in plot_map
    file_path = os.path.join(loc_save, fname)
    gdf.to_file( file_path, driver="GeoJSON")

    
    return gdf.Name, file_path




def url_KML_map(url_data_paths, json_fname, 
                doScotWales=[False],
                save_dir='./map_data'):
    """
    The main function used to take a KML file and plot it 
        Calls kml_create_json to create json file
        and plot_map to plot the map
    
    Args: url_data (file path) the path to the kml file
          doScotWales (string) whether need to call split_islands on Scottish data
            or join on Wales data
    Returns: 
        The folium map
    
    """
    gdfAll = gpd.GeoDataFrame()
    
    for i, url_data in enumerate(url_data_paths):
        gdf = load_kml(url_data)
        
        if doScotWales[i] == 'Scotland':
            gdf = _split_islands(gdf)
        elif doScotWales[i] == 'Wales':
            gdf = _joinWalesRegions(gdf)
        elif doScotWales[i] == 'Northern Ireland':
            gdf = gdf.loc[gdf.Name=='BT']
            gdf.Name = gdf.Name.replace({'BT':'Northern Ireland'})
        gdfAll = pd.concat([gdfAll, gdf], ignore_index=True)
    
    # create a json file for plotting and gives back names of regions
    fname= json_fname +'.json'
    map_names, json_path = gdf_create_json(gdfAll, loc_save=save_dir, fname=fname)


def _split_islands(df):
    """
    Takes a gpd dataframe of Scotland which needs reducing in size as too big to plot
        Highlands and Islands multi-polygon is split (or exploded) from a  multi-polygon to set of polygons, the first few are selected and then merged (dissolve) and combined with rest of df
    
    Args: df (geopandas dataframe) of Scottish data
    Returns: 
        df (geopandas dataframe) reduced in size
    
    """
    from shapely.geometry.polygon import Polygon
    from shapely.geometry.multipolygon import MultiPolygon
    
    # the islands is the 7th component
    gdf = df.iloc[7:8].copy()

    # slight mods to help change things
    gdf["geometry"] = [MultiPolygon([feature]) if isinstance(feature, Polygon)
                       else feature for feature in gdf["geometry"]]

    # explode th eislands into a number of polygons from one multipolygon
    gdf_parts = gdf.explode(column='geometry', ignore_index=True, index_parts=False)

    # take the first 3 elements only and dissolve back to one multi polygon
    df7new = gdf_parts.iloc[0:3].dissolve()

    # create the new geopanda with the new islands and the previous rest
    dfnew = pd.concat([df.loc[:6], df7new]).reset_index(drop=True)
    
    return dfnew

def _joinWalesRegions(df):
    wales_region_dict={ 
         'Wrexham':'North Wales', 
         'Conwy':'North Wales', 
         'Gwynedd':'North Wales', 
         'Isle of Anglesey':'North Wales',
         'Flintshire':'North Wales', 
         'Denbighshire':'North Wales', 
         'Powys':'Mid Wales',
         'Ceredigion':'Mid Wales',
         'Carmarthenshire':'South West Wales',
         'Swansea':'South West Wales',
         'Neath Port Talbot':'South West Wales',
         'Pembrokeshire':'South West Wales',
         'Bridgend':'South Wales',
         'Vale of Glamorgan':'South Wales',
         'Cardiff':'South Wales',
         'Rhondda Cynon Taf':'South Wales',
         'Merthyr Tydfil':'South Wales',
         'Caerphilly':'South East Wales',
         'Newport':'South East Wales',  
         'Torfaen':'South East Wales', 
         'Monmouthshire':'South East Wales',    
         'Blaenau Gwent':'South East Wales',
        }
    
    df.Name = df.Name.str.replace(' Council','')
    df.Name = df.Name.replace(wales_region_dict)
    
    df = df.dissolve(by='Name',as_index=False)
    
    return df


def load_pcode_csvs():
    """
    Loads the csv files for poscodes in different countries in UK
    Runs _postcodeDF_additionalProcessing for additional processing
    The main goal is to have a file with all postcodes each having a region name 
        that can be plotted
        
    Args: None (could add column to load instead of Population?)
    Returns: 
        A pandas dataframe with values for each postcode and an area name to plot to
    
    """

    import re

    file_paths=[".\\_data\\England1 postcodes.csv",
                ".\\_data\\England2 postcodes.csv",
                ".\\_data\\Wales postcodes.csv",
                ".\\_data\\NRScotland-SmallUser.csv", #has column for maps
    #             ".\\_data\\Scotland postcodes.csv",
                ".\\_data\\BT postcodes.csv",]

    postcode_df = pd.DataFrame()
    for file in file_paths:
        print(file)
        if re.search(r"NRScotland-SmallUser",file):
            df_temp = pd.read_csv(file, 
                     usecols=['Postcode','ScottishParliamentaryRegion2021Code','CensusPopulationCount2011'])
            df_temp.rename(columns={'ScottishParliamentaryRegion2021Code':'District Code',
                                   'CensusPopulationCount2011':'Population'},inplace=True)
            df_temp['Country'] = 'Scotland'

        else:
            df_temp = pd.read_csv(file, 
                     usecols=['Postcode','Country','District','District Code','County','Population'])

        postcode_df = pd.concat([postcode_df, df_temp])
        
        # call function for additional procs
    postcode_df = _postcodeDF_additionalProcessing(postcode_df)
        
    return postcode_df

def _postcodeDF_additionalProcessing(postcode_df):

    cols_to_use = ['Postcode','Country','mapArea','Population']
    
    # For England counties match maps
    postcode_df['mapArea']=postcode_df['County']

    # For Northern Ireland group together
    country = 'Northern Ireland'
    postcode_df.loc[postcode_df['Country']==country,'mapArea'] = country

    # For Wales use the dict defined before
    country = 'Wales'
    postcode_df.loc[postcode_df['Country']==country,'mapArea'] = postcode_df.loc[postcode_df['Country']==country,'District']
    postcode_df.mapArea = postcode_df.mapArea.replace(wales_region_dict)

    # For Scotland uses ScottishParliamentaryRegion2021Code from https://www.nrscotland.gov.uk/statistics-and-data/geography/nrs-postcode-extract
    # and Scottish (Holyrood) Parliamentary Regions, 2011 from https://borders.ukdataservice.ac.uk/easy_download_data.html?data=Scotland_preg_2011
    # slight difference in code numbers but checked location of areas in Kaggle and seems correct
    country = 'Scotland'
    dict_scotDistr = {
         'S17000020':'Glasgow',
         'S17000019' : 'Central Scotland',
         'S17000018' : 'West Scotland', 
         'S17000015' : 'South Scotland', 
         'S17000014' : 'North East Scotland', 
         'S17000013' : 'Mid Scotland and Fife', 
         'S17000012' : 'Lothian', 
         'S17000011' : 'Highlands and Islands', 
        }

    postcode_df.loc[postcode_df['Country']==country,'mapArea'] = postcode_df.loc[postcode_df['Country']==country,'District Code']
    postcode_df.mapArea = postcode_df.mapArea.replace(dict_scotDistr)

    # Select some columns only
    postcode_df = postcode_df[cols_to_use]
    
    return postcode_df

