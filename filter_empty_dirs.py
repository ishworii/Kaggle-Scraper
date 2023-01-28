import os
import glob
import pandas as pd
from tqdm import tqdm
import json
import shutil
from distutils.dir_util import copy_tree
import ast

import csv
import sys

csv.field_size_limit(sys.maxsize)


def delete_empty_folders(path):
    count = 0
    for each_folder in os.listdir(path):
        folder_path = os.path.join(path, each_folder)
        if os.listdir(folder_path) == []:
            os.rmdir(folder_path)
            count += 1
    print(f"Deleted {count} empty folders")


# delete_empty_folders(path="/home/ik-pc/Desktop/ec2/v5_data")


def find_multiple_csv(path):
    count = 0
    for each_folder in os.listdir(path):
        folder_path = os.path.join(path, each_folder)
        csv_files = glob.glob(f"{folder_path}/*.csv")
        if len(csv_files) > 1:
            json_file = glob.glob(f"{folder_path}/*.json")
            if len(json_file) > 0:
                json_file = json_file[0].split("/")[-1]
                filename = json_file.split(".")[0].split("_metadata")[0]
                for each_file in csv_files:
                    csv_file = each_file.split("/")[-1].split(".")[0]
                    if csv_file != filename:
                        os.remove(each_file)
                        print(f"removed {each_file}")
            count += 1
            print(f"Found {len(csv_files)} in {folder_path}")
    print(f"Found {count} folders with multiple csv files.")


# find_multiple_csv(path="/home/ik-pc/Desktop/ec2/v5_data")


def limit_csv(path):
    csv_files = glob.glob(f"{path}/*/*.csv")
    for each_file in tqdm(csv_files):
        try:
            df = pd.read_csv(
                each_file,
                nrows=1000,
                engine="python",
                encoding_errors="ignore",
                on_bad_lines="skip",
                quotechar='"',
            )
            df = df.iloc[:300]
            df.to_csv(each_file, index=False)
        except Exception as e:
            print(e)
            continue


limit_csv(path="/home/ik-pc/Desktop/scraping_charles/kaggle/non_empty")


def is_empty(json_file):
    try:
        with open(json_file, "r") as file:
            data = json.load(file)
        for val in data.values():
            if val != "":
                return False
        return True
    except json.decoder.JSONDecodeError:
        return False


# def count_empty(path):
#     count = 0
#     for each_folder in tqdm(os.listdir(path)):
#         folder_path = os.path.join(path, each_folder)
#         json_file = glob.glob(f"{folder_path}/*.json")
#         # print(json_file, folder_path, each_folder)
#         # break
#         if len(json_file) > 0:
#             if is_empty(json_file[0]):
#                 count += 1
#     print(count)


# count_empty(path="/home/ik-pc/Desktop/ec2/v2_data")


def move_files(path):
    for each_folder in tqdm(os.listdir(path)):
        folder_path = os.path.join(path, each_folder)
        json_file = glob.glob(f"{folder_path}/*.json")
        if len(json_file) > 0:
            if is_empty(json_file[0]):
                copy_tree(
                    folder_path,
                    f"/home/ik-pc/Desktop/scraping_charles/kaggle/empty/{each_folder}",
                )
                # move to a separate directory
            else:
                # move to a separate directory
                copy_tree(
                    folder_path,
                    f"/home/ik-pc/Desktop/scraping_charles/kaggle/non_empty/{each_folder}",
                )


# move_files(path="/home/ik-pc/Desktop/ec2/v5_data")


def find_zip(path):
    for each_folder in tqdm(os.listdir(path)):
        folder_path = os.path.join(path, each_folder)
        zip_files = glob.glob(f"{folder_path}/*.zip")
        if len(zip_files) > 0:
            os.remove(zip_files[0])
            print(f"Removed {zip_files[0]}")


# find_zip(path="/home/ik-pc/Desktop/ec2/v5_data")


def jsonify(path):
    for each_folder in tqdm(os.listdir(path)):
        folder_path = os.path.join(path, each_folder)
        json_files = glob.glob(f"{folder_path}/*.json")
        if len(json_files) > 0:
            json_file = json_files[0]
            with open(json_file, "r") as file:
                data = file.read()
            json_data = json.loads(data)
            json_data = ast.literal_eval(json_data)
            with open(json_file, "w", encoding="utf-8") as jf:
                json.dump(json_data, jf)


# jsonify(path="/home/ik-pc/Desktop/ec2/v5_data")


def find_malformed(path):
    for each_folder in tqdm(os.listdir(path)):
        folder_path = os.path.join(path, each_folder)
        num_files = len(os.listdir(folder_path))
        if num_files < 4:
            # os.rmdir(folder_path)
            print(f"Found {folder_path} with {num_files} files")


# find_malformed(path="/home/ik-pc/Desktop/ec2/v5_data")
