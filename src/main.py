# Import required libraries for automation, logging, and time management
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import logging
import os

# Configure logging to capture key events and errors
logging.basicConfig(filename='process.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Check if the specified file exists before processing
def check_file_existence(file_path):
    try:
        with open(file_path) as f:
            logging.info(f"File {file_path} exists.")
            return True
    except FileNotFoundError:
        logging.error(f"File {file_path} not found.")
        return False

# Load keywords from the provided CSV file and handle encoding errors
def load_keywords(file_path):
    if check_file_existence(file_path):
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            logging.info(f"Loaded {len(df)} entries from {file_path} using UTF-8.")
            return df
        except UnicodeDecodeError:
            logging.warning(f"UTF-8 decoding failed. Trying ISO-8859-1 for {file_path}.")
            try:
                df = pd.read_csv(file_path, encoding='ISO-8859-1')
                logging.info(f"Loaded {len(df)} entries from {file_path} using ISO-8859-1.")
                return df
            except Exception as e:
                logging.error(f"Failed to load {file_path}: {e}")
    return None

# Initialize the Chrome WebDriver for automation tasks
def setup_driver(chrome_driver_path):
    try:
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service)
        logging.info("WebDriver initialized successfully.")
        return driver
    except Exception as e:
        logging.error(f"Failed to initialize WebDriver: {e}")
        return None

# Open a new tab in the browser and switch to it
def open_and_switch_to_new_tab(driver):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])

# Navigate directly to the Last.fm URL
def open_lastfm_url(driver, url):
    driver.get(url)

# Process the keywords in batches of 20
def process_keywords_in_batches(df, driver, batch_size=20, start_index=0):
    counter = start_index
    for index, row in df.iloc[start_index:].iterrows():  # Start from the last saved index
        if pd.isna(row['Artist']) or pd.isna(row['Track']):  # Skip if any data is missing
            logging.info("Empty artist or track name found. Skipping.")
            continue

        # Construct the Last.fm URL
        artist = row['Artist'].replace(' ', '+')
        track = row['Track'].replace(' ', '+')
        url = f"https://www.last.fm/music/{artist}/_/{track}/+tags"

        open_and_switch_to_new_tab(driver)
        open_lastfm_url(driver, url)  # Use the constructed URL to navigate
        time.sleep(1)  # Pause briefly between opening tabs

        counter += 1
        if counter % batch_size == 0:
            logging.info(f"Batch of {batch_size} completed. Pausing.")
            save_progress(counter)
            return  # End the batch without closing the browser

    logging.info("All keywords processed.")

# Save the progress of keyword processing to a file for later resumption
def save_progress(counter):
    with open('progress.txt', 'w') as f:
        f.write(str(counter))
    logging.info(f"Progress saved at keyword {counter}.")

# Load the progress from a file to resume keyword processing
def load_progress():
    if os.path.exists('progress.txt'):
        with open('progress.txt', 'r') as f:
            return int(f.read())
    return 0  # Default to starting from the first keyword

# Main execution logic: load data, set up the driver, and process keywords
if __name__ == "__main__":
    # Updated file path to match your new CSV
    file_path = '/Users/chaeyeonkim/Projects/LastFM_URL_Search/data/LastFM_URL.csv'
    df = load_keywords(file_path)

    if df is not None:
        chrome_driver_path = '/Users/chaeyeonkim/Downloads/chromedriver-mac-x64/chromedriver'
        driver = setup_driver(chrome_driver_path)

        if driver is not None:
            start_index = load_progress()
            process_keywords_in_batches(df, driver, batch_size=20, start_index=start_index)

            logging.info("Keeping browser open for manual tasks.")
            time.sleep(360)  # Pause execution for 6 minutes before closing manually
