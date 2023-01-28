from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import json
from time import sleep
import os
import logging
import utility


logging.basicConfig(
    filename="logs.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


def setup():
    # Headless/incognito Chrome driver
    options = Options()
    # chrome_options.add_argument("headless")
    driver = webdriver.Firefox(
        service=Service(GeckoDriverManager().install()), options=options
    )

    logging.info("Webdriver setup done.")

    driver.get("https://www.google.com/")
    driver.maximize_window()
    sleep(2)

    return driver


def main(driver, filename):
    # load all the links to all_datasets
    with open(filename, "r") as file:
        all_datasets = json.load(file)
    logging.info(f"{len(all_datasets)} different tables found.")

    scrapped = 0
    for each_link in all_datasets:
        if each_link["scraped"]:
            scrapped += 1

    logging.info(
        f"Scraped {scrapped} tables and {len(all_datasets) - scrapped} are remaining.."
    )
    try:

        logging.info(f"{len(all_datasets)} different tables found.")

        scrapped = 0
        for each_link in all_datasets:
            if each_link["scraped"]:
                scrapped += 1

        logging.info(
            f"Scraped {scrapped} tables and {len(all_datasets) - scrapped} are remaining.."
        )

        # # iterate through each link
        logging.info("Iterating through each table")
        for each_link in all_datasets:
            if each_link["scraped"]:
                continue
            os.chdir("/home/ik-pc/Desktop/scraping_charles/data/kaggle")

            # create new tab for each new link, extract everything and return back
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            # get the new url
            driver.get(each_link["link"])
            sleep(5)

            # extract details

            res = utility.extract_list(driver)
            for each_result in res:
                utility.save_everything(each_result)
            each_link["scraped"] = True

            # close and switch back to the original tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    except (KeyboardInterrupt, Exception) as e:
        each_link["scraped"] = True

        logging.info(f"{e} in extractor")

        # save the correct state json to the file
        os.chdir("/home/ik-pc/Desktop/scraping_charles")
        with open(filename, "w") as file:
            json.dump(all_datasets, file)
        logging.info(f"Error {e} occured...restarting the program again...")

        return -1


def all_scraped(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    for each_row in data:
        if not each_row["scraped"]:
            return False
    return True


if __name__ == "__main__":
    filename = "links_kaggle.json"
    limit = 100
    count = 99
    while count < limit:
        driver = setup()
        retval = main(driver, filename)
        # if retval == -1:
        count += 1
        if all_scraped(filename):
            break
