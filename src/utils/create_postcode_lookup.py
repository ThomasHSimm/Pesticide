import os
import pandas as pd
import copy



def main():
    
    # load data-file
    
    # load postcode mapper
    
    


def addto_pcode_mapper(df, MAIN_PATH, shorter_pc_list,postcode_column = 'address_postcode'):

    # load postcode to area df
    map_data_file = os.path.join(MAIN_PATH, "src", "utils", "map_data", "postcode_to_region.csv")
    postcodes_to_area_df = mpu.get_poscode_df(path_to_csv = map_data_file)
    postcodes_to_area_df['removeChar']=0
    
    
    df_pc= copy.deepcopy(df)

    # get the unique post-codes and ignore ones that don't exist ='0'
    df_pc =pd.DataFrame(data=df[postcode_column].unique(),columns=['Postcode'])
    df_pc = df_pc.loc[df_pc.Postcode!='0']

    postcode_column = 'Postcode'

    # check if already in the postcode to area df
    # just use the ones that are not
    df_pc['mapArea'] = _create_area_col(df_pc, postcodes_to_area_df, 'Postcode')
    df_pc = df_pc.loc[df_pc['mapArea'].isna()]

    print(f"After initial mapping\n \
The length of postcode mapper is {len(postcodes_to_area_df)} \n \
and {len(df_pc)} still unknonwn\n")
    
    for removeChar in range(1,4):
        print('>> Post-code length reduced by ',removeChar)
        # remove 1 char from the postcode
        df_pc[postcode_column]=df_pc[postcode_column].str[:-1]

        df_pc['mapArea'] = _create_area_col(df_pc, 
                         shorter_pc_list[removeChar], postcode_column)

           
        # add new values to the dictionary
        df_add = copy.deepcopy(df_pc[['Postcode','mapArea']].loc[df_pc['mapArea'].notna()])
        df_add['removeChar'] = removeChar
        
        
        postcodes_to_area_df = pd.concat([ postcodes_to_area_df, df_add ])      
        print(f"Number of new postcodes added {len(df_add)}")

        # just use postcodes not found in next iteration 
        df_pc = copy.deepcopy(df_pc.loc[df_pc['mapArea'].isna()])
        print(f"The length of postcode mapper is {len(postcodes_to_area_df)} \n\
and {len(df_pc)} still unknonwn")
        
        print()
        
    return postcodes_to_area_df, df_add, df_pc
        
newPC, df_add, df_pc = dothis(df, MAIN_PATH, shorter_pc_list)

def _postcode_to_area(df_,
                    postcodes_df, 
                    postcode_column='Postcode'):
    """
    loads poscode data and returns an array of the area the postcode corresponds to
         by mapping to postcodes_df
    
    Args:   path_to_csv (path) csv file of postcode data
            usecols (list[str]) what columns to load, also includes latitude,longitude
            reduce_p_max (int) number of chars to take off end of potscode -1
    Returns: 
        df_['mapArea'] (column of pd.DataFrame) 
    
    """  
    
    df_ = copy.deepcopy(df)
    postcode_dict = dict(postcodes_df[['Postcode','mapArea']].values)
    
    df_['mapArea'] = df_.loc[:,postcode_column].map(postcode_dict)

    return df_['mapArea']



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
