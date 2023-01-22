import pandas as pd
import copy

def _get_count_col(df_chem, minVal=1.):
    col=[]
    for val in minVal:
        col.append( (df_chem.values>val).sum(axis=1) )
    return col
    
def _group_ID_chem(df):
    df_chem = pd.get_dummies(df['chem_name'])
    df_chem = df['amount_pc'].values[:,None] * df_chem

    return df_chem


def groupby_id_chem(df: pd.DataFrame):
    """
    Want df with output like: 
        - sample_id - num_tests - max_test - chem_name_max
    The reason is there are ~200 different chem names so a simple 
        onehot encoding on chem names won't be useful
    So df is grouped by ID, with some diff depending on column

    Args:
        df (pandas dataframe) : the dataframe

    Returns:
        df after modifications grouped by ID

    """

    # do one-hot encoding on chem_name and multiply amount_pc by the one-hot
    df_chem = _group_ID_chem(df)

    # a dict of names:values to check if values are more than
    dict_vals = {'over_mrl' : 1., 
             '75pc_mrl' : 0.75, 
             '50pc_mrl' : 0.5, 
             '25pc_mrl' : 0.25,
             '10pc_mrl' : 0.1,
             '05pc_mrl' : 0.05, 
             '00pc_mrl' : 0.00 }

    # create cols for df based on whether amountpc > dict_values
    newcols = _get_count_col(df_chem, minVal=list(dict_vals.values()))

    # add these cols to a new dataframe
    df_chem_new = copy.copy(df[['sample_id','chem_name']])
    for i, key in enumerate(dict_vals.keys()):
        df_chem_new[key] = newcols[i]

    # add column to get max  N.B. can't use df_chem_new and should only be one val
    df_chem_new['max_pc'] = df_chem.values.max(axis=1)
    

    # Start grouping by ID
    # First get no. of tests in ranges from dict_vals
    df_new = df_chem_new.groupby('sample_id').sum()

    # Get number of tests. N.B. some times get more than one test with 0 value??
    df_new['tests'] = df_chem_new.groupby('sample_id').count().iloc[:,0]
    # Get max value
    df_new['max_pc'] = df_chem_new[['sample_id','max_pc']].groupby('sample_id').max()
    # Get mean value
    df_new['mean_pc'] = df_chem_new[['sample_id','max_pc']].groupby('sample_id').mean()

    # to get chem_name of max value
    df_new2= df.loc[df.groupby(['sample_id'])['amount_pc'].idxmax(),:]
    df_new = df_new.merge(df_new2, left_on='sample_id', right_on='sample_id')

    
    return df_new
