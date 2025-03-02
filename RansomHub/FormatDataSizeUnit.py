import re

import pandas as pd

# Reload the uploaded file
file_path = "./RansomHubData_V1.csv"
df = pd.read_csv(file_path, encoding="utf-8")

def convert_to_gb(value):
    """Convert different data volume units to GB."""
    match = re.match(r"([\d\.]+)\s*(GB|MB|TB)", str(value), re.IGNORECASE)
    if match:
        num, unit = float(match.group(1)), match.group(2).upper()
        if unit == "MB":
            return num / 1024  # Convert MB to GB
        elif unit == "TB":
            return num * 1024  # Convert TB to GB
        return num  # Already in GB
    return None  # Handle unexpected values

# Apply conversion
df["Data_Volume_GB"] = df["Data_Volume"].apply(convert_to_gb)

# Save the cleaned dataset
output_file_path = "RansomHubData_V2.csv"
df.to_csv(output_file_path, index=False)

print(f"Data size converted to GB and saved to {output_file_path}")

# ** Note: not all data are formatted correctly, so some values may not be converted, thus resulting in manual correction.