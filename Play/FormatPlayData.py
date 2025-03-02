# The goal of this script is to get the type of stolen data, country of origin and the sector of the company from the CSV file and store in a new CSV file

import csv
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time
import json
import pandas as pd

load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv("GEMINI_API_TOKEN")

CLEAN_DATA_LIST = []

def get_sector_of_company(company_name, company_details):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""You are a highly accurate industry classification AI based on the Global Industry Classification Standard (GICS).
        Your task is to categorize the company into its appropriate GICS sector based on its name and provided company detail provided.

        Company Name: '{company_name}'
        Company detail: {company_details}

        Respond with ONLY a valid JSON object containing these two fields:
        - GICS Sector: One of the 11 official GICS sectors
        - GICS Industry Group: The specific industry group under the identified sector

        IMPORTANT: Return ONLY the JSON object with no other text, markdown formatting, or code block markers."""

        response = model.generate_content(prompt)

        if not response or not response.candidates or not response.candidates[0].content.parts:
            print("Error: No valid response received from the model")
            return None, None
        
        result = response.candidates[0].content.parts[0].text

        try:
            # Parse the cleaned JSON
            sectors_json = json.loads(result)
            
            clean_sector = sectors_json.get("GICS Sector", None)
            clean_industry_group = sectors_json.get("GICS Industry Group", None)

            return clean_sector, clean_industry_group
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return None, None

    except Exception as e:
        print(f"An error occurred when calling the API: {e}")
        return None, None

def get_stolen_data_type(data_description):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""You are a cybersecurity AI specializing in classifying stolen data. Given a data description, categorize the stolen data into one or more of the following standard categories:

        Personal Identifiable Information (PII)
        Financial & Payment Data
        Authentication & Credential Data
        Medical & Health Records (PHI)
        Corporate & Business Data
        Government & Military Data
        Intellectual Property (IP) & Research Data
        Communication & Social Data
        System & Infrastructure Data
        Dark Web & Underground Economy Data

        Input Format:
        Data Description: A short description of the type of stolen data (e.g., "Usernames, hashed passwords, email addresses from an online banking platform.") Here is the data {data_description}
        
        Output Format:
        Categories: (A comma-separated list of applicable categories, e.g., "Authentication & Credential Data, Personal Identifiable Information")
        """

        response = model.generate_content(prompt)

        if not response or not response.candidates or not response.candidates[0].content.parts:
            print("Error: No valid response received from the model")
            return None
        
        result = response.candidates[0].content.parts[0].text

        try:
            clean = result.split(":")
            return clean[1].strip()
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return None
        
    except Exception as e:
        print(f"An error occurred when calling the API: {e}")
        return None
    
def get_cleaned_data():

    # Read the CSV file
    file_path = "PlayData_V0.csv"
    # Read CSV with proper parsing
    df = pd.read_csv(file_path)
    total_rows = len(df)  # Get total row count
    progress_count = 0  # Initialize progress counter

    # Extract relevant columns safely
    for _, row in df.iterrows():
        company_name = row["Company Name"]
        company_details = row["Company Details"]
        country = row["Location"]
        visits = row["Visits"]
        date = row["Added Date"]
        data_size = row["Data Size"]
        data_info = row["Data Information"]

        # Get the sector of the company
        time.sleep(15) # Sleep for 15 seconds to avoid rate limiting
        clean_sector, clean_industry_group  = get_sector_of_company(company_name, company_details)

        print(f"clean_sector: {clean_sector}, clean_industry_group: {clean_industry_group}")

        # Get the type of stolen data
        time.sleep(15) # Sleep for 15 seconds to avoid rate limiting
        stolen_data_type = get_stolen_data_type(data_info)

        print(f"stolen_data_type: {stolen_data_type}")

        # Append the cleaned data to the list
        CLEAN_DATA_LIST.append([company_name, clean_sector, clean_industry_group, country, stolen_data_type, date, data_size, visits])
        print(f"Appended data for {company_name}")

        # Update progress counter
        progress_count += 1
        print(f"Processed {progress_count}/{total_rows} rows ({(progress_count / total_rows) * 100:.2f}% complete)")

# Write the cleaned data to a new CSV file
def insert_data():
    with open('PlavData_V1.csv', mode='w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)

        # Write the header
        csvwriter.writerow(["Company_Name", "Sector", "Industry_Group", "Country_of_Origin", "Type_of_Data_Stolen", "Date", "Data_Volume", "Visits"])

        # Write the data
        for data in CLEAN_DATA_LIST:
            csvwriter.writerow(data)

    # Close the file
    csvfile.close()

if __name__ == "__main__":
    get_cleaned_data()
    insert_data()
    print("Data cleaning and insertion completed!")