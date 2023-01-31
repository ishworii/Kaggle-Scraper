<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Kaggle-Scraper Readme</title>
  </head>
  <body>
    <h1>Kaggle-Scraper</h1>
    <p>A tool for extracting datasets from Kaggle and downloading them to a local machine</p>
    <h2>Introduction</h2>
    <p>The purpose of this project is to extract datasets from Kaggle and download them to a local machine. The project consists of three main scripts:</p>
    <ul>
      <li><strong>links.py:</strong> extracts dataset links from the Kaggle site that are in CSV format</li>
      <li><strong>extractor.py:</strong> extracts the table description, associated column descriptions, dataset name, and table URL from the dataset page to a CSV file</li>
      <li><strong>downloader.py:</strong> downloads the table using the KaggleAPI, along with the data dictionary, table description, and URL to the table. Each extracted table has a parent directory with 4 files</li>
    </ul>
    <p>Additionally, there are other important files such as <strong>count_columns.py</strong> which counts the total number of columns collected so far, and <strong>filter_empty_dirs.py</strong> which processes the scraped data, such as deleting empty folders, limiting the number of rows in a CSV file, converting JSON strings into actual JSON files, and copying the folders from the test directory to the processed directory.</p>
    <h2>Technologies Used</h2>
    <p>This project uses selenium-python, KaggleAPI, and pandas. To use the KaggleAPI, you need to have your <strong>kaggle.json</strong> file in the <strong>~/.kaggle</strong> folder.</p>
    <h2>Improvements to be Made</h2>
    <p>There are some areas of improvement for this project, such as using multi-threading to speed up the extraction process, and better exception handling.</p>
  </body>
</html>
