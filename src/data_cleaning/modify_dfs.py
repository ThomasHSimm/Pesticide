import pandas as pd
import re

def modify_df(df):
    """ Makes modifications to a pesticide dataframe
    Calls extract_pcode, extract_pesticide, rename_cols to extract information from df and rename cols
    
    Args:
        df (pandas dataframe) : the dataframe
        
    Returns:
        df after modifications
        
    """
    # rename cols
    df = rename_cols(df)
    
    # remove rows that are just headers i.e. 1st column not of form 898908/809809 here just checks if 1st value is numeric
    df = df.loc[df.iloc[:,0].apply(lambda x: x if x[0].isnumeric() else 0)!=0]
    
    # get postcodes
    df['address_postcode']=df['address'].apply(extract_pcode)
    
    try:
        df['packer__postcode']=df['packer_/_manufacturer_/_importer'].apply(extract_pcode)
    except:
        pass
    try:
        df['packer__postcode']=df['packer_/_manufacturer'].apply(extract_pcode)
    except:
        pass
                       
    # get pesticide residue    
    df2 = extract_pesticide(df)
    df2.reset_index(inplace=True,drop=True)
    df = df.join(df2)
    
    # modify product name
    df['product']  = df['product'].apply(lambda x: re.sub(r'_BNA','',x) )
    
    # modify date
    # df2['date_of_sampling'].dt.day

    # change data type of columns
    df['date_of_sampling'] = pd.to_datetime(df['date_of_sampling'])
    
    df['amount_detected'] = df['amount_detected'].astype('float64')
    df['mrl'] = df['mrl'].astype('float64')

    # The sampling point column seems to be the same as the retail outlet column
    # if the sampling point column is empty the retail outlet column is not
    # both are a string of the retail outlet name
    
    # Move the data from the sampling_point column to retail outlet if applicable
    if 'sampling_point' in df.columns:
        df['retail_outlet'] = (
            df['retail_outlet']
            .apply(lambda x: x 
            if not pd.isna(x)
            else df['sampling_point']))
        # delete the sampling point column
        df.drop('sampling_point', axis=1, inplace=True)         
    
    # drop the pesticide_residues_found_in_mg/kg_(mrl) column
    df.drop('pesticide_residues_found_in_mg/kg_(mrl)', axis=1, inplace=True)

    return df
     
def extract_pcode(x):    
    regexp = r'([A-Za-z]+[0-9]+\s[0-9]+[A-Za-z]+$)'
    try:
        return re.findall(regexp,x)[0]
    except:
        return 0
    
def extract_pesticide(df):
    
    df.replace({'None were detected above the set RL': 'n/a'}, regex=True, inplace=True)
    
    df2=df['pesticide_residues_found_in_mg/kg_(mrl)'].str.extract(r'(.*)\s(\d[\d.]*)\s+\(MRL\s*=\s*(\d[\d.]*)\)')

    df2.fillna(0, inplace=True)
    
    df2.rename(columns={0:'chem_name',1:'amount_detected',2:'mrl'},inplace=True)
   
    
    return df2
    
    
def rename_cols(df):
    renaming_dict = {
    old_name : new_name 
        for old_name,new_name 
        in zip(list(df),[new_name.lower().replace(' ','_') 
                         for new_name in list(df)])
    }

    df = df.rename(columns=renaming_dict)
    
    df = df.loc[df['sample_id'].str.contains(r'^[0-9]')]
    df.reset_index(inplace=True,drop=True) 
    return df