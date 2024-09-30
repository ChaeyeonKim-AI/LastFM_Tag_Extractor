import pandas as pd
import re

# Define the exclusion list (ensure all items are lowercase for case-insensitive matching)
exclusion_list = ['seen live', 'female vocalists', 'male vocalists', 'my favorite']

# Function to remove excluded tags
def clean_tags(tags):
    if not isinstance(tags, str) or tags.strip() == "":  # Check for non-string or empty entries
        return tags  # Return original value if empty or not a string
    
    # Split the tags into a list (comma-separated, and stripping whitespace)
    tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
    
    # Debug: Print original tags
    print(f"Original Tags: {tags_list}")
    
    # Filter out any tags in the exclusion_list (case-insensitive) or matching a number pattern
    cleaned_tags = [tag for tag in tags_list if tag.lower() not in exclusion_list and not re.match(r'^\d+$', tag)]
    
    # Debug: Print cleaned tags
    print(f"Cleaned Tags: {cleaned_tags}")
    
    # Return the cleaned tags as a comma-separated string or None if empty
    return ', '.join(cleaned_tags) if cleaned_tags else None

# Function to clean the 'LastFM Tags' column in the CSV file
def clean_lastfm_tags(csv_file_path, output_file_path):
    # Load the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Apply the clean_tags function to the 'LastFM Tags' column
    df['LastFM Tags'] = df['LastFM Tags'].apply(clean_tags)
    
    # Save the cleaned tags back to a new CSV file
    df.to_csv(output_file_path, index=False)
    print(f"Cleaned tags saved to {output_file_path}")

# Main
if __name__ == "__main__":
    csv_file_path = '/Users/chaeyeonkim/Projects/LastFM_URL_Search/data/updated_lastfm_tags.csv'
    output_file_path = '/Users/chaeyeonkim/Projects/LastFM_URL_Search/data/clean_lastfm_tags.csv'
    
    # Clean the tags in the 'LastFM Tags' column
    clean_lastfm_tags(csv_file_path, output_file_path)