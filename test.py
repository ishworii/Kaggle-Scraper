from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
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
import pandas as pd

# define some universal funtions for extraction
def xpath_finder(driver, xpath, many=False):
    if many:
        try:
            element = driver.find_elements(By.XPATH, xpath)
            return element
        except NoSuchElementException:
            return -1
    try:
        element = driver.find_element(By.XPATH, xpath)
        return element
    except NoSuchElementException:
        return -1


def css_finder(driver, xpath, many=False):
    if many:
        try:
            element = driver.find_elements(By.CSS_SELECTOR, xpath)
            return element
        except NoSuchElementException:
            return -1
    try:
        element = driver.find_element(By.CSS_SELECTOR, xpath)
        return element
    except NoSuchElementException:
        return -1


# for each_csv file extract metadata, description, and filename
def extract_details(driver):
    description = xpath_finder(
        driver, "//div[@class='sc-eCqeQn edoUMz sc-icOqvn bOdfNc']"
    )
    if description != -1:
        logging.info("Table description found...")
        description = description.text
    else:
        description = ""
    columns = xpath_finder(
        driver, "//div[@class='sc-byEWUa sc-kRzYL fAuqll iNrYWF']", many=True
    )
    if columns == -1:
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

    # find data
    count = 0
    action = webdriver.ActionChains(driver)
    first_column = xpath_finder(
        driver, "//span[@class='sc-jOrMOR sc-dPyBCJ iHqEhn idytGD']"
    )
    action.move_to_element(first_column)
    action.perform()
    return description, metadata


def extract_list(url, driver) -> List[Dict]:
    driver.get(url)
    sleep(5)
    list_of_files = xpath_finder(
        driver, "//div[@class='sc-lfmOwF gqobWc']//p[contains(.,'.csv')]", many=True
    )
    if list_of_files == -1:
        return -1
    res = []
    for each_file in list_of_files:
        tmp = dict()
        tmp["filename"] = each_file.text
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


def create_browser():
    options = Options()
    options.add_argument("start-maximized")
    # options.add_argument("--headless")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    return driver


def main():
    url = "https://www.kaggle.com/datasets/atulanandjha/imdb-50k-movie-reviews-test-your-bert"
    driver = create_browser()
    res_list = extract_list(url, driver)


main()
