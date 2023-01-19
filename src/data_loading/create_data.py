import os
import sys

MAIN_PATH = os.getcwd()
sys.path.append(MAIN_PATH)

import src.data_loading.loads_from_url as lfu


def main():

    file_folder = "./data/combined_df.csv"
    folder_path = "./data/"
    dfBIG = lfu.import_all_ods(folder_path)
    dfBIG.to_csv(file_folder)


if __name__ == "__main__":
    main()
