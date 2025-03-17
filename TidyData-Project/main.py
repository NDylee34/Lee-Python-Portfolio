import pandas as pd

# Load the dataset
olympics_data = "data/olympics_08_medalists.csv"
df = pd.read_csv(olympics_data)

# Display basic information about the dataset
df.info(), df.head()
