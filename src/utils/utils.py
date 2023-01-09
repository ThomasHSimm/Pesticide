from ..data_loading.loads_from_url import *
from ..data_cleaning.modify_dfs import *

def getAllFilesThenSave(folder_path):
    """
    - (data.loading.import_all_files_save) imports ods files from a directory = folder_path for each file 
    uses import_ods to get a dataframe then joins them for one 
    big data frame
    - (data_cleaning.modify_dfs) Does the modifications 
    - Then save as a csv
    
    Args: the path to the data files
    Returns: nothing, save a file in folder_path as 'combined_data.csv'
    
    """
    df_combo = import_all_files_save(folder_path)

    file_out = os.path.join(folder_path,'combined_data.csv')   
    
    df_combo = modify_df(df_combo)
    
    df_combo.to_csv( file_out )