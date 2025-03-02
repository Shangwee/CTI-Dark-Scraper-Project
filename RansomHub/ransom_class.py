"""
Author: Derrick
File: ransom_class.py
Date: 02/03/2025
---------
Description:
"""

import pandas as pd
import time
import agent
import re


def parse_classification(classification_string):
    """
    Parses the classification string into separate columns.

    Args:
        classification_string: The classification string from Gemini.

    Returns:
        A dictionary with parsed values, or None if parsing fails.
    """
    if not isinstance(classification_string, str) or not classification_string:
        return None  # Handle non-string or empty input

    try:
        categories_match = re.search(r"Categories:\s*(.*)", classification_string)
        sector_match = re.search(r"GICS Sector:\s*(.*)", classification_string)
        industry_match = re.search(r"GICS Industry Group:\s*(.*)", classification_string)

        if categories_match and sector_match and industry_match:
            categories = categories_match.group(1).strip()
            sector = sector_match.group(1).strip()
            industry = industry_match.group(1).strip()

            return {
                "categories": categories,
                "GICS Sector": sector,
                "GICS Industry": industry,
            }
        else:
            return None  # Parsing failed
    except Exception as e:
        print(f"Error parsing classification string: {e}")
        return None


def process_csv_batches(csv_file, batch_size=10, pause_time=120):
    """
    Reads a CSV, classifies company descriptions in batches, and saves results.

    Args:
        csv_file: Path to the CSV file.
        batch_size: Number of rows to process per batch.
        pause_time: Time to pause (in seconds) after each batch.
    """
    try:
        df = pd.read_csv(csv_file)
        results = []  # Store classification results
        parsed_results = []  # store parsed results
        start_index = 0

        while start_index < len(df):
            end_index = min(start_index + batch_size, len(df))
            batch = df['Company Details'][start_index:end_index]

            for desc in batch:
                output_result = agent.get_classification(desc)
                print(output_result)
                results.append(output_result)
                parsed_results.append(parse_classification(output_result))  # parse result

            df.loc[start_index:end_index - 1, 'classification'] = results[start_index:end_index]  # Assign classification results
            parsed_df = pd.DataFrame(parsed_results[start_index:end_index])  # Create dataframe from parsed results
            df.loc[start_index:end_index - 1, 'categories'] = parsed_df['categories'].values
            df.loc[start_index:end_index - 1, 'GICS Sector'] = parsed_df['GICS Sector'].values
            df.loc[start_index:end_index - 1, 'GICS Industry'] = parsed_df['GICS Industry'].values

            df.to_csv("classified_companies.csv", index=False)  # save after each batch.

            print(f"Processed batch {start_index // batch_size + 1}. Saved to classified_companies.csv")

            if end_index < len(df):
                print(f"Pausing for {pause_time} seconds...")
                time.sleep(pause_time)

            start_index = end_index

        print("Classification complete. Results saved to classified_companies.csv")

    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
    except Exception as e:
        print(f"An error occurred during CSV processing: {e}")


if __name__ == "__main__":
    csv_file = "RansomHubData_V0.csv"  # Replace with your CSV file name
    process_csv_batches(csv_file)