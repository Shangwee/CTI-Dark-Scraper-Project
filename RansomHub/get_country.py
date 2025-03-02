"""
Author: Derrick
File: get_country.py
Date: 02/03/2025
---------
Description:
"""

import pandas as pd
from bs4 import BeautifulSoup


def extract_country(html_file, csv_file):
    # Read the HTML file
    with open(html_file, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Extract all rows
    rows = soup.find_all("tr")
    country_dict = {}

    for row in rows:
        company_tag = row.find("td")
        country_tag = row.find("td", class_="victim-country")

        if company_tag and country_tag:
            company_name = company_tag.text.strip()
            img_tag = country_tag.find("img")
            country_file = img_tag["src"].split("/")[-1] if img_tag else "not found"
            country_dict[company_name] = country_file

    # Load CSV file
    df = pd.read_csv(csv_file)

    # Populate country of origin
    df["Country"] = df["Company"].map(lambda x: country_dict.get(x, "not found"))

    # Save updated CSV
    df.to_csv("updated_companies.csv", index=False)
    print("Updated file saved as 'updated_companies.csv'")


# Example usage
extract_country("Ransomware Groups.html", "Companies.csv")
