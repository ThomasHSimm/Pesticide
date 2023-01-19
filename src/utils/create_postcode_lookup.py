import copy
import os
import re
import sys

import pandas as pd

MAIN_PATH = os.getcwd()
sys.path.append(MAIN_PATH)

from src.data_loading.loads_from_url import get_postcode_df


def main(data_file="./data/combined_df.csv"):
    """
    main function creates a new postcode-area mapper file
    by searching for postcodes with less characters

    """
    # load data
    df = pd.read_csv(data_file, index_col=0)

    # load postcode mapper
    postcode_df = get_postcode_df(
        path_to_csv=".//src//utils//map_data//postcode_to_region.csv",
        usecols=["Postcode", "mapArea"],
    )

    # get a list of postcode data with characters removed
    # i.e. shorter_pc_list[0] = get_postcode_df()
    #      shorter_pc_list[0] = get_postcode_df( for postcode reduced by one char)
    shorter_pc_list = get_postcode_list(
        postcode_df, usecols=["Postcode", "mapArea"], reduce_p_max=4
    )

    # get the columns in the data containing postcode data
    postcode_cols_in_df = [col for col in df.columns if re.search(r"[Pp]ostcode", col)]

    for postcode_col in postcode_cols_in_df:
        print(postcode_col)
        postcode_df = addto_pcode_mapper(
            df, shorter_pc_list, postcode_column=postcode_col
        )
        shorter_pc_list[0] = postcode_df

    # save the new file
    path_to_new_csv = ".//src//utils//map_data//postcode_to_region_new.csv"
    postcode_df.to_csv(path_to_new_csv)


def get_postcode_list(postcodes_df, usecols=["Postcode", "mapArea"], reduce_p_max=4):
    """
    loads postcode data and returns that as a list of dataframes
    where postcode has has been reduced by 1:reduce_p_max-1 in length

    Args:   path_to_csv (path) csv file of postcode data
            usecols (list[str]) what columns to load, also includes latitude,longitude
            reduce_p_max (int) number of chars to take off end of potscode -1
    Returns:
        list_postcodes_df (list[pd.DataFrame]) list of pandas dataframe of the postcode data

    """
    postcodes_df = postcodes_df[usecols]
    postcodes_df_temp = postcodes_df.copy()

    list_postcodes_df = []
    list_postcodes_df.append(postcodes_df_temp.copy())

    for i in range(1, reduce_p_max):
        colname = f"Postcode_m{i}"
        postcodes_df_temp[colname] = postcodes_df_temp["Postcode"].str[:-i]

        df = _getpc(postcodes_df_temp, colname)
        df = df.rename(columns={colname: "Postcode"})
        list_postcodes_df.append(df)

    return list_postcodes_df


def addto_pcode_mapper(df, shorter_pc_list, postcode_column="address_postcode"):
    """
    the main function creates a new postcode-area mapper from data inputted
    using a basic algorithm of reducing the number of chars in a postcode

    Args:   df (pd.DataFrame) the data with a postcode column
            shorter_pc_list (list[pd.DataFrame]) list of dataframes to match postcodes to areas
                each list reduces the characters in the postcode
            postcode_column (str) name of column in df containg postcode
    Returns:
            postcodes_to_area_df (pd.DataFrame) an updated postcode-area mapper
    """

    # First run through for the full-postcode
    postcodes_to_area_df = shorter_pc_list[0]
    postcodes_to_area_df["removeChar"] = 0

    df_pc = copy.deepcopy(df)

    # get the unique post-codes and ignore ones that don't exist ='0'
    df_pc = pd.DataFrame(data=df[postcode_column].unique(), columns=["Postcode"])
    df_pc = df_pc.loc[df_pc.Postcode != "0"]

    postcode_column = "Postcode"

    # check if already in the postcode to area df
    # just use the ones that are not
    df_pc["mapArea"] = _create_area_col(
        df_pc, postcodes_to_area_df[["Postcode", "mapArea"]], "Postcode"
    )
    df_pc = df_pc.loc[df_pc["mapArea"].isna()]

    print(
        f"After initial mapping\n \
The length of postcode mapper is {len(postcodes_to_area_df)} \n \
and {len(df_pc)} still unknonwn\n"
    )

    for removeChar in range(1, 4):
        print(">> Post-code length reduced by ", removeChar)
        # remove 1 char from the postcode
        df_pc[postcode_column] = df_pc[postcode_column].str[:-1]

        df_pc["mapArea"] = _create_area_col(
            df_pc, shorter_pc_list[removeChar], postcode_column
        )

        # add new values to the dictionary
        df_add = copy.deepcopy(
            df_pc[["Postcode", "mapArea"]].loc[df_pc["mapArea"].notna()]
        )
        df_add["removeChar"] = removeChar

        postcodes_to_area_df = pd.concat([postcodes_to_area_df, df_add])
        print(f"Number of new postcodes added {len(df_add)}")

        # just use postcodes not found in next iteration
        df_pc = copy.deepcopy(df_pc.loc[df_pc["mapArea"].isna()])
        print(
            f"The length of postcode mapper is {len(postcodes_to_area_df)} \n\
and {len(df_pc)} still unknonwn"
        )

        print()

    return postcodes_to_area_df


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
    postcodes_df_temp = postcodes_df_temp.groupby(
        by=[colname, "mapArea"], as_index=False
    ).count()

    postcode_short = postcodes_df_temp.sort_values(
        "Postcode", ascending=False
    ).drop_duplicates([colname])

    postcode_short = postcode_short.loc[:, [colname, "mapArea"]].reset_index(drop=True)
    return postcode_short


def _create_area_col(df, postcodes_df, postcode_column):
    df_ = copy.deepcopy(df)
    postcode_dict = dict(postcodes_df[["Postcode", "mapArea"]].values)

    df_["mapArea"] = df_.loc[:, postcode_column].map(postcode_dict)
    return df_["mapArea"]


if __name__ == "__main__":
    main()
