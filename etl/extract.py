import requests
import json
import os
import json
import pandas as pd
from pathlib import Path
from config.settings import Config
import logging

logger = logging.getLogger(__name__)


def extract_from_api(file_number=1):
    # API request details
    url = "https://api.rentcast.io/v1/properties/random?limit=500"
    headers = {
        "accept": "application/json",
        "X-Api-Key": "put-in-the-write-api"
    }

    # Request data
    response = requests.get(url, headers=headers)

    # Check for success before saving
    if response.status_code == 200:
        data = response.json()

        # Ensure data/raw directory exists
        os.makedirs("data/raw", exist_ok=True)

        # Save the file with sequential numbering
        filename = f"data/raw/propertyrecords{file_number:02d}.json"
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
            print(f"✅ File saved as: {filename}")

    else:
        print(f"❌ Failed to fetch data: {response.status_code} - {response.text}")


def combine_data():
    import json
    from pathlib import Path

    # Get all propertyrecords files
    input_files = Path('data/raw').glob('propertyrecords*.json')
    combined_data = []

    # Read and combine the records
    for file in input_files:
        with open(file, 'r') as f:
            data = json.load(f)
            combined_data.extend(data)  # assumes each file contains a list of records

    # Write the combined data into Records.json
    with open('data/raw/property_records.json', 'w') as outfile:
        json.dump(combined_data, outfile, indent=4)

    print("✅ Successfully combined into 'data/raw/property_records.json'")


def load_raw_data():
    # Read the combined JSON file
    with open('data/raw/property_records.json', 'r') as file:
        data = json.load(file)

    # Convert to DataFrame
    propertyrecords_df = pd.DataFrame(data)

    # Save to CSV
    os.makedirs("data/processed", exist_ok=True)
    propertyrecords_df.to_csv('data/processed/property_records.csv', index=False)
    print("✅ Successfully extracted and saved to 'data/processed/property_records.csv'")
    return propertyrecords_df

