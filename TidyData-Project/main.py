import pandas as pd

# Load the dataset
file_path = "/mnt/data/olympics_08_medalists.csv"
df = pd.read_csv(file_path)

# Display basic information about the dataset
df.info(), df.head()
