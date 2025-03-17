import pandas as pd

<<<<<<< HEAD
# Loading data
df = pd.read_csv("data/olympics_08_medalists.csv")
=======
# Load the dataset
olympics_data = "data/olympics_08_medalists.csv"
df = pd.read_csv(olympics_data)

# Display basic information about the dataset
df.info(), df.head()
>>>>>>> f618272d9377cfc9497d15ee7c3741953d789131
