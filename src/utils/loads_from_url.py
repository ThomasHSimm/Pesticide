import pandas as pd
import ezodf
import re
import os






def import_all_files_save(folder_path):
    """
    imports ods files from a directory = folder_path for each file 
    uses import_ods to get a dataframe then joins them for one 
    big data frame
    
    Args: the path to the data files
    Returns: dataframe of the combined file df_combo
    
    """
    
    file_path = []
    for x in os.listdir(folder_path):
        file_path.append(os.path.join(folder_path,x) )
    
    dict_column_names = {'Sampling Point':'Retail Outlet',
                     'Packer / Manufacturer':'Packer / Manufacturer / Importer'}


    for i,file in enumerate(file_path):
        if re.search(r'.ods',file) and not re.search(r'__',file):
            df_temp = import_ods(file)
            df_temp = df_temp.rename(columns=dict_column_names)

            if i>0:
                df_combo = pd.concat([df_combo, df_temp])
            else:
                df_combo = df_temp
        
    return df_combo
    
    
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
            df_new, bool_sheet = import_ods_inner(sheet)
            
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
    return df
            

    
    
    
    
    
    

def import_ods_inner(sheet):
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