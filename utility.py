from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import string
import json
from time import sleep
import os
import logging
from typing import List, Dict
import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi
import zipfile
import glob

# define some universal funtions for extraction
def xpath_finder(driver, xpath, many=False):
    if many:
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )
            return element
        except NoSuchElementException:
            return -1
    try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element
    except NoSuchElementException:
        return -1


def css_finder(driver, css, many=False):
    if many:
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, css))
            )
            return element
        except NoSuchElementException:
            return -1
    try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css))
        )
        return element
    except NoSuchElementException:
        return -1


# for each_csv file extract metadata, description, and filename
def extract_details(driver):
    description = xpath_finder(
        driver, "//div[@class='sc-eCqeQn edoUMz sc-icOqvn bOdfNc']"
    )
    if description != -1:
        description = description.text
    else:
        description = ""
        logging.info("Description not found..")
    columns = xpath_finder(
        driver, "//div[@class='sc-byEWUa sc-kRzYL fAuqll iNrYWF']", many=True
    )
    if columns == -1:
        logging.info("columns not found...skipping")
        return None
    metadata = dict()
    for each_column in columns:
        column_name = css_finder(each_column, "span")
        if column_name != -1:
            column_name = column_name.text
        else:
            column_name = ""
        col_desc = css_finder(each_column, "p")
        if col_desc != -1:
            col_desc = col_desc.text
        else:
            col_desc = ""
        metadata[column_name] = col_desc
    return description, metadata


# get the list of all csv files from the dataset url
def extract_list(driver) -> List[Dict]:
    
    list_of_files = xpath_finder(
        driver, "//div[@class='sc-lfmOwF gqobWc']//p[contains(.,'.csv')]", many=True
    )
    if list_of_files == -1:
        logging.info(f"List of csv files not found for {driver.current_url}..retrying")
        return -1
    else:
        logging.info(f"{len(list_of_files)} Files found..")
            
    res = []
    for each_file in list_of_files:
        tmp = dict()
        tmp["filename"] = each_file.text
        driver.execute_script("arguments[0].scrollIntoView();",each_file)
        sleep(3)
        driver.execute_script("arguments[0].click();", each_file)
        sleep(3)
        details = extract_details(driver)
        tmp["table_url"] = driver.current_url
        if details is not None:
            description, metadata = details
            tmp["description"] = description
            tmp["metadata"] = metadata
        url_splitted = tmp["table_url"].split("/")
        username = url_splitted[-2]
        dataset = username + "/" + url_splitted[-1].split("?")[0]
        tmp["dataset"] = dataset
        res.append(tmp)
    return res


# download csv file, and create all necessary metadata files
def save_everything(result: Dict) -> None:
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

    current_dir = os.getcwd()
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
            os.chdir(current_dir)
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

    # write to tablename_URLtotable.txt
    with open(f"{table_name}_URLtotable.txt", "w") as f:
        f.write(table_url)

    # write metadata to a json file
    with open(f"{table_name}_metadata.json", "w", encoding="utf-8") as f:
        json.dump(table_metadata, f)

    # write to a description file
    with open(f"{table_name}_description.txt", "w") as f:
        f.writelines(table_description)
