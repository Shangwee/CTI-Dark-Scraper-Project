import pandas as pd

# Load the dataset
file_path = "./PlayData_V2.csv"  # Update with the correct path
df = pd.read_csv(file_path, encoding="ISO-8859-1")

# Split 'Type_of_Data_Stolen' into separate rows
df_exploded = df.assign(Type_of_Data_Stolen=df["Type_of_Data_Stolen"].str.split(", ")).explode("Type_of_Data_Stolen")

# Save the transformed dataset
output_file_path = "PlayData_V3.csv"
df_exploded.to_csv(output_file_path, index=False)

print(f"Data split and saved to {output_file_path}")
