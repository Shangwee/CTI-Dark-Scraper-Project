import pandas as pd

# Reload the uploaded file
file_path = "./PlayData_V1.csv"
df = pd.read_csv(file_path, encoding="utf-8")

# Function to clean the Data Size column
def clean_data_size(value):
    if isinstance(value, str):
        value = value.lower().strip()
        if "gb" in value:
            value = value.replace("gb", "").strip()  # Remove "gb"
        if value == "???":
            value = "0"  # Replace "???" with 0
    return value

# Apply the cleaning function to the Data Size column
df["Data_Volume"] = df["Data_Volume"].apply(clean_data_size)

# Convert to numeric (optional, if needed for calculations)
df["Data_Volume"] = pd.to_numeric(df["Data_Volume"], errors="coerce").fillna(0).astype(int)


# Save the cleaned dataset
output_file_path = "PlayData_V2.csv"
df.to_csv(output_file_path, index=False)

print(f"Cleaned data saved to {output_file_path}")