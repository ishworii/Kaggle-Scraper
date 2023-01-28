import pandas as pd
import os
import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi
import zipfile
import glob
import logging
import json
import string
import sys
import csv

csv.field_size_limit(sys.maxsize)


logging.basicConfig(
    filename="downloading_logs.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


def get_data(csv_filename):
    df = pd.read_csv(csv_filename, encoding_errors="ignore")
    df = df[df["table_description"].notna()]
    print(f"The size of the table is {df.shape}")
    result_list = df.to_dict(orient="records")
    return result_list


def save_everything(result, path):
    (
        table_filename,
        table_url,
        table_description,
        table_metadata,
        dataset,
    ) = result.values()
    # convert table name to correct format
    table_name = table_filename.split(".")[0]
    table_name = table_name.lower()
    table_name = table_name.translate(str.maketrans("", "", string.punctuation))
    if len(table_name) > 80:
        table_name = table_name[:80]
    table_name = table_name.replace(" ", "_")
    username = dataset.split("/")[-1]
    table_name = username + table_name
    os.chdir(path)
    if not os.path.isdir(table_name):
        os.mkdir(table_name)
    os.chdir(table_name)
    # download the csv file using the API, unzip the file and delete the zip
    filename = f"{table_name}.csv"
    api = KaggleApi()
    api.authenticate()
    try:
        downloaded = kaggle.api.dataset_download_file(
            dataset=dataset, file_name=table_filename
        )
        if downloaded:
            logging.info(f"Successfully downloaded the {filename}")
        else:
            logging.info(f"Could not download the {filename}")
    except Exception as e:
        logging.info(f"Error occured while downloading data...{e}")
        if os.path.isdir(table_name):
            os.remove(table_name)
        return
    # if zipfile is present extract the zip file and remove the zipfile
    zipped = glob.glob("*.zip")
    if zipped:
        zipped = zipped[0]
        with zipfile.ZipFile(zipped) as file:
            file.extractall()

        os.remove(zipped)
    # rename the table to proper name
    csv_file = glob.glob("*.csv")

    if csv_file:
        csv_file = csv_file[0]
        os.rename(csv_file, filename)
        try:
            df = pd.read_csv(
                filename,
                encoding_errors="ignore",
                nrows=500,
                engine="python",
                encoding_errors="ignore",
                on_bad_lines="skip",
                quotechar="'",
                sep=",",
            )
            df = df.iloc[:500]
            df.to_csv(filename, index=False)

        except Exception as e:
            logging.info(f"Error {e}")

    # write to tablename_URLtotable.txt
    with open(f"{table_name}_URLtotable.txt", "w") as f:
        f.write(table_url)

    # write metadata to a json file
    with open(f"{table_name}_metadata.json", "w", encoding="utf-8") as f:
        json.dump(table_metadata, f)

    # write to a description file
    with open(f"{table_name}_description.txt", "w") as f:
        f.writelines(table_description)


def main():
    csv_file = "details.csv"
    result_list = get_data(csv_file)
    total = len(result_list)
    for index, result in enumerate(result_list):
        try:
            save_everything(result, "")
            logging.info(f"Sucessfully downloaded {index+1}/{total}")
        except Exception as e:
            logging.info("Error")


if __name__ == "__main__":
    main()
