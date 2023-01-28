from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import logging
import pandas as pd

# Headless/incognito Chrome driver
chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("start-maximized")
# chrome_options.add_argument("headless")
driver = webdriver.Firefox(
    service=Service(GeckoDriverManager().install()), options=chrome_options
)

logging.info("Webdriver setup done.")


driver.get("https://www.kaggle.com/datasets?fileType=csv")

sleep(2)

arr = []

count = 0
while True:
    all_divs = driver.find_elements(
        By.XPATH, "//div[@data-testid='search']//li//a[@class='sc-gFGZVQ NUNdY']"
    )
    for each_div in all_divs:
        link = each_div.get_attribute("href")
        # print(link)
        tmp = {"link": link, "scraped": False}
        arr.append(tmp)

    try:
        next_button = driver.find_element(By.XPATH, "//i[@title='Next Page']")
        # print(next_button)
        driver.execute_script("arguments[0].click();", next_button)
        sleep(3)

    except NoSuchElementException:
        print("End...")
        break
    count += 1
    print(f"Scraping links from page {count+1}")


df = pd.DataFrame(arr)
df.to_json("links_kaggle_original.json", orient="records")
