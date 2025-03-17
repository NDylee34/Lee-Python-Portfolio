import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Loading data
df = pd.read_csv("TidyData-Project/data/olympics_08_medalists.csv")

# Display basic info
print("Dataset Overview:\n")
print(df.info())

# Display first few rows
df.head()

# Convert wide format to long format
df_long = df.melt(id_vars=["medalist_name"], var_name="sport_gender", value_name="medal")

# Drop rows with missing medal values
df_long = df_long.dropna(subset=["medal"])

# Extract gender and sport separately
df_long[["gender", "sport"]] = df_long["sport_gender"].str.extract(r'^(male|female)_(.*)')

# Clean sport names
df_long["sport"] = df_long["sport"].str.replace("_", " ").str.title()

# Keep only necessary columns
df_long = df_long[["medalist_name", "sport", "gender", "medal"]].reset_index(drop=True)

# Display transformed data
df_long.head()