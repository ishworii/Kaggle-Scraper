import os
import glob
import pandas as pd
from tqdm import tqdm
import json


def count_col(filename):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
        return len(data.keys())
    except:
        return 0


BASE_DIR = "/home/ik-pc/Desktop/scraping_charles/kaggle/non_empty"
count = 0
all_folders = os.listdir(BASE_DIR)
for each_folder in tqdm(all_folders):
    # print(each_folder)
    full_path = os.path.abspath(each_folder)
    os.chdir(f"{BASE_DIR}/{each_folder}")
    json_files = glob.glob("*.json")
    for each_file in json_files:
        col = count_col(each_file)
        count += col
    os.chdir("/".join(full_path.split("/")[:-1]))
print(f"Number of columns : {count}")
