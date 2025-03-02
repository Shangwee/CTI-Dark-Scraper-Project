import pandas as pd

def convert_to_gb(value):
    """Convert data volume to GB."""
    if pd.isna(value) or value == "0":
        return 0  # Keep missing or zero values as 0 GB

    value = value.strip().lower()  # Normalize case and spaces

    if "tb" in value:  # Convert TB to GB
        return float(value.replace("tb", "").strip()) * 1024

    if "gb" in value:  # Already in GB, just extract the number
        return float(value.replace("gb", "").strip())

    return None  # If unrecognized, return None

# Load the dataset
file_path = "./BianLianData_V1.csv"
df = pd.read_csv(file_path, encoding="ISO-8859-1")

# Apply conversion function
df["Data_Volume_GB"] = df["Data_Volume"].apply(convert_to_gb)

# Save the standardized dataset
output_file_path = "BianLianData_V2.csv"
df.to_csv(output_file_path, index=False)

print(f"Standardized data saved to {output_file_path}")
