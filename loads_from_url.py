import pandas as pd
import ezodf

def import_ods(fname):
    """
    imports ods files given a filename and returns a pd dataframe
    used with function import_ods_inner which does the importing for each sheet != 0
    
    Args:
        fname (string): a string to location of the ods file
    
    Returns:
        a dataframe of the ods file
    """
    doc = ezodf.opendoc(fname)
    for i, sheet in enumerate(doc.sheets):
        if i!=0: #ignore 1st sheet
            product = sheet.name
            print(product)
            
            df_new =import_ods_inner(sheet)
            df_new.columns = df_new.columns.str.strip()
            try:
                df = pd.concat([df,df_new])
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
    """
    df_dict = {}
    for i, row in enumerate(sheet.rows()):
    # row is a list of cells
    # assume the header is on the first row
        if i == 1:
        # columns as lists in a dictionary
            df_dict = {cell.value:[] for cell in row}

    # create index for the column headers
    for i,row in enumerate(sheet.rows()):
        if i == 0:
            continue
        elif i == 1:
            col_index = [cell.value for cell in row]
            continue
        for j,cell in enumerate(row):
            df_dict[col_index[j]].append(cell.value)
            
    # delete none column
    try:
        del df_dict[None]
    except:
        pass
    # and convert to a DataFrame
    df = pd.DataFrame(df_dict)
    
    # fill based on previous values    
    df.fillna(method='ffill', inplace=True)

    return df
