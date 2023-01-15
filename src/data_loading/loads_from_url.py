import pandas as pd
import ezodf
import re

import streamlit as st
import os

import src.data_cleaning.modify_dfs as md
   
def save_dfs(folder_path='/data/' , file_folder='/data/combined_df.csv'):

    dfBIG = import_all_ods(folder_path)
    dfBIG.to_csv(file_folder)

# create a function to import all ods files and return a df
def import_all_ods(folder_path):
    """
    Imports all ods files in a folder and returns a pd df
    
    Args:
        folder_path (string): a string to location of the ods file
    
    Returns:
        pd.Dataframe (mod_df): a dataframe of all ods files combined,
            with modifcations applied
    """
    
    dict_column_names = {'Sampling Point':'Retail Outlet',
                     'Packer / Manufacturer':'Packer / Manufacturer / Importer'}
    
    
    file_path = []
    for file_ in os.listdir(folder_path):
        if file_.endswith('.ods') and not re.search(r'^_',file_):
            file_path.append(os.path.join(folder_path, file_) )
    
    all_df_lst = []
    for file_ in file_path:
        fname_ = file_.split('\\')[-1].split('.')[0]
        print(f"Importing {fname_}")
        df = import_ods(file_)
        df = df.rename(columns=dict_column_names)
        
        # put each modified df into a list
        all_df_lst.append(df)

    # concat all the modified dfs   
    df_all = pd.concat(all_df_lst)

    # modify the concatenated dfs
    mod_df = md.modify_df(df_all)

    return mod_df
    
def import_ods(fname):
    """
    imports ods files given a filename and returns a pd dataframe
    used with function import_ods_inner which does the importing for each sheet != 0
    
    Args:
        fname (string): a string to location of the ods file
    
    Returns:
        a dataframe of the ods file
    
    """
    
    df = pd.DataFrame()
    
    doc = ezodf.opendoc(fname)
    
    for i, sheet in enumerate(doc.sheets):
        product = sheet.name

        if product != 'Introduction' and product != 'Summary' and not re.search(r"SUM",product): #ignore 1st sheet
            
            # main call
            df_new, bool_sheet = _import_ods_inner(sheet)
            
            # if sheet is not a bad sheet
            if bool_sheet == True:
                df_new['product'] = product
                df_new.columns = df_new.columns.str.strip()
                try:
                    if len(df_new.columns)>3:
                        df = pd.concat([df,df_new])
                    else:
                        print(f"{product} not enough columns")
                except:
                    df = df_new

                df.reset_index(inplace=True,drop=True)    
                
        else:
            fname_ = fname.split('\\')[-1].split('.')[0]
#             print(f'Failed to load {fname_}: {product}')
            

    return df
            

def _import_ods_inner(sheet):
    """
    inner function of import_ods
    takes individual sheets and returns a pd df
    
    Args:
        sheet (sheet from ezodf): a sheet of the ods file
    
    Returns:
        a dataframe of the sheet 
        and a boolean of if the sheet is not correct 
    """
    
    data_sheet = []
    got_colname =False
    for i,row in enumerate(sheet.rows()):

        if got_colname == False:
            column_names = [cell.value for cell in row]

            if column_names[0] == 'Sample ID':
                got_colname = True
                     
        else:
            data_sheet.append( [cell.value for cell in row] )
            
    
    if got_colname:
        ddf = pd.DataFrame(data_sheet)

        ddf.columns = column_names

        # delete none column
        try:
            del ddf[None]
        except:
            pass


        # fill based on previous values    
        ddf.fillna(method='ffill', inplace=True)

        return ddf,True
    else:
        return [],False

    return mod_df


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

