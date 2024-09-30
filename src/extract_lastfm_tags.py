import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# Set up logging
logging.basicConfig(
    filename='extract_lastfm_tags.log',
    filemode='w',  # Overwrite the log file on each run
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

# Function to extract tags from a LastFM URL
def extract_tags_from_url(driver, url):
    try:
        driver.get(url)
        time.sleep(3)  # Adjust the sleep time as needed
        
        # Find all <h3> elements with class "big-tags-item-name" and inside it, find the "link-block-target"
        big_tags = driver.find_elements(By.XPATH, '//h3[@class="big-tags-item-name"]/a[@class="link-block-target"]')
        
        # Extract the text from each element
        tags = [element.text for element in big_tags if element.text]
        formatted_tags = ', '.join(tags)  # Join the tags with commas
        logging.info(f"Extracted tags for {url}: {formatted_tags}")
        return formatted_tags
    
    except Exception as e:
        logging.error(f"Failed to extract tags for {url}: {e}", exc_info=True)
        return ""

# Function to process the CSV and extract tags for each track URL
def process_csv_and_extract_tags(csv_file_path, output_file_path, batch_size=50):
    # Set up the WebDriver (adjust the path to your chromedriver)
    chrome_driver_path = '/Users/chaeyeonkim/Downloads/chromedriver-mac-x64/chromedriver'
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service)
    
    # Load the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Initialize a counter to track progress and batch processing
    total_tracks = len(df)
    start_index = 0  # You can change this if you want to resume processing from a specific point
    
    # Process in batches to avoid overloading the browser or the server
    while start_index < total_tracks:
        end_index = min(start_index + batch_size, total_tracks)
        logging.info(f"Processing tracks {start_index} to {end_index - 1}")
        
        for index, row in df.iloc[start_index:end_index].iterrows():
            url = row['LastFM URL']  # Assuming 'URL' is the column name in the CSV
            logging.info(f"Processing URL: {url}")
            
            # Extract tags from the LastFM URL
            tags = extract_tags_from_url(driver, url)
            
            # Save the extracted tags to the 'Tags' column (E column)
            df.at[index, 'Tags'] = tags
        
        # Save the progress to a new CSV file after each batch
        df.to_csv(output_file_path, index=False)
        logging.info(f"Batch {start_index} to {end_index - 1} saved to {output_file_path}")
        
        # Increment the start index for the next batch
        start_index += batch_size
    
    # Close the browser after processing all batches
    driver.quit()
    logging.info("All URLs processed and browser closed.")

# Main function
if __name__ == "__main__":
    csv_file_path = '/Users/chaeyeonkim/Projects/LastFM_URL_Search/data/lastfm_tags.csv'
    output_file_path = '/Users/chaeyeonkim/Projects/LastFM_URL_Search/data/updated_lastfm_tags.csv'
    
    # Process the CSV and extract tags
    process_csv_and_extract_tags(csv_file_path, output_file_path)
