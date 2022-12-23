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
    
    # add a new column
    df['amount_pc']=df['amount_detected']/df['mrl']

    df.loc[df['amount_pc'].isna(),['amount_pc']]=0
                       
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

def groupby_id_and_q(df2: pd.DataFrame,
                     col_groupby: str = 'country_of_origin') -> pd.DataFrame:
    """
    Groups a Pandas DataFrame based on the sample_id and country_of_origin
        the new dataframe has a new column number_of_tests
        - this is the number of unique sample_ids
        the other 2 numerical columns are means of previous values

    Args:
        df2 (pd.DataFrame): DataFrame of Pesticide data after 1st clean
        col_groupby (str): Column to do 1st groupby

    Raises:
        ValueError: ??

    Returns:
        df2_grouped (pd.DataFrame): Pandas DataFrame grouped by id and country- note the mean is taken twice
                                        1. When grouping by id
                                        2. When grouping by col_groupby
                                    the new dataframe has a new column number_of_tests
                                        - this is the number of unique sample_ids
                                    in addition to the previous numeric columns
        df2_grouped_sample (pd.DataFrame): Pandas DataFrame grouped by id only
    """
    
    
    # group by id
    df2_grouped_sample = df2.groupby(['sample_id','date_of_sampling', col_groupby],as_index=False).mean(numeric_only =True).sort_values('amount_detected', ascending=False)
    
    # group by col_groupby-> mean
    df2_grouped = df2_grouped_sample.groupby(col_groupby,as_index=False).mean(numeric_only =True)
    
    # group by col_groupby-> count
    df2_grouped_b = df2_grouped_sample.groupby(col_groupby, as_index=False).count().iloc[:,0:2]
    
    # merge the 2 new dfs and rename count column
    df2_grouped= df2_grouped.merge(df2_grouped_b, left_on=col_groupby, right_on=col_groupby)
    df2_grouped.rename(columns ={'sample_id':'number_of_tests'},inplace=True)
    
    # sort dataframe by counts
    df2_grouped= df2_grouped.sort_values('number_of_tests', ascending=False)

    # reset index
    df2_grouped.reset_index(inplace=True, drop=True)
    df2_grouped_sample.reset_index(inplace=True, drop=True)

    return df2_grouped, df2_grouped_sample