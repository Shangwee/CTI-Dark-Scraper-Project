# The goal of this script is to get the type of stolen data, country of origin and the sector of the company from the CSV file and store in a new CSV file

import csv
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time
import re
import json

load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv("GEMINI_API_TOKEN")

CLEAN_DATA_LIST = []

def get_sector_of_company(company_name, tag):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Create explicit prompt that requests JSON without markdown formatting
        prompt = f"""You are a highly accurate industry classification AI based on the Global Industry Classification Standard (GICS).
        Your task is to categorize the company into its appropriate GICS sector based on its name and provided tags.

        Company Name: '{company_name}'
        Tags: {tag}

        Respond with ONLY a valid JSON object containing these two fields:
        - GICS Sector: One of the 11 official GICS sectors
        - GICS Industry Group: The specific industry group under the identified sector

        IMPORTANT: Return ONLY the JSON object with no other text, markdown formatting, or code block markers."""

        # Get the sector of the company
        response = model.generate_content(prompt)
        
        # Check if we have a valid response
        if not response or not response.candidates or not response.candidates[0].content.parts:
            print("Error: No valid response received from the model")
            return None, None
            
        # Process the response
        sectors = response.candidates[0].content.parts[0].text
        
        # Clean the text of any markdown or extra formatting
        clean_text = re.sub(r'```json\s*|\s*```$', '', sectors)
        clean_text = clean_text.strip()
        
        print("Raw response:", clean_text)
            
        try:
            # Parse the cleaned JSON
            sectors_json = json.loads(clean_text)
            
            clean_sector = sectors_json.get("GICS Sector", None)
            clean_industry_group = sectors_json.get("GICS Industry Group", None)

            return clean_sector, clean_industry_group
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return None, None
            
    except Exception as e:
        print(f"An error occurred when calling the API: {e}")
        return None, None
    

def get_country_of_origin(tag):
    #split the tag into a list of words (eg. "usa, law.legal" -> ["usa", "law.legal"])
    tag_list = tag.split(",")

    # get the first word in the list
    country_tag = tag_list[0].strip().lower()

    # print the country tag
    print("Country tag:", country_tag)

    # check if the country tag is a common abbreviation
    if country_tag == "usa" or country_tag == "us":
        return "United States"
    elif country_tag == "uk":
        return "United Kingdom"
    else:
        # return capitalized country name
        return country_tag.capitalize()

    
def get_type_of_data_stolen(data_description):
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
        
        categories = response.candidates[0].content.parts[0].text

        try:
            clean = categories.split(":")
            return clean[1].strip()
        except Exception as e:
            print(f"An error occurred when parsing the categories: {e}")
            return None

    except Exception as e:
        print(f"An error occurred when calling the API: {e}")
        return None

def get_cleaned_data():
    with open(".\BianLianData_V0.csv", mode='r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)

        # Read and print each row
        next(csvreader)  # Skip the header row

        count = 0
        for row in csvreader:
            # Assuming the tag column is the second column (index 1)
            
            if not row[1]:
                continue
        
            company_name = row[0]
            data_description = row[1]
            tag = row[2] 
            date = row[3]
            data_volume = row[5]

            
            # Get the sector of the company
            time.sleep(15) # Sleep for 15 seconds to avoid rate limiting
            clean_sector, clean_industry_group = get_sector_of_company(company_name, tag)

            # Get what type of data stolen
            time.sleep(15) # Sleep for 15 seconds to avoid rate limiting
            type_of_data = get_type_of_data_stolen(data_description)
            
            # Get the country of origin of the company
            country = get_country_of_origin(tag)

            print("Number", count+1, "completed")
            # Append the cleaned data to the list
            CLEAN_DATA_LIST.append([company_name, clean_sector, clean_industry_group, country, type_of_data, date, data_volume])

    # Close the file
    csvfile.close()


# Write the cleaned data to a new CSV file
def insert_data():
    with open(".\BianLianData_V1.csv", mode='w', newline='') as csvfile2:
        csvwriter = csv.writer(csvfile2)

        # Write the header row
        csvwriter.writerow(["Company_Name", "Sector", "Industry_Group", "Country_of_Origin", "Type_of_Data_Stolen", "Date", "Data_Volume"])

        # Write the cleaned data
        for row in CLEAN_DATA_LIST:
            csvwriter.writerow(row)

    # Close the file
    csvfile2.close()

if __name__ == "__main__":
    get_cleaned_data()
    insert_data()

    print("Data cleaning and formatting complete!")
