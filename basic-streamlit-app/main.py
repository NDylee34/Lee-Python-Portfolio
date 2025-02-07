import streamlit as st
import pandas as pd

st.title("Penguins!")
st.write("This Streamlit app allows users to retrieve data about penguins that inhabit in different islands. The data contains information about the penguins' ID number, Species type, Located Island, Physical measurements, Sex, and Birth Year.")

# Loading data
df = pd.read_csv("data/penguins.csv")

# Display the imported dataset
st.write("Here's the dataset loaded from a CSV file:")
st.dataframe(df)

st.write("Please select an island of your preference below to view penguins' data filtered by location:")

# Using a selectbox to allow users to filter data by island
island = st.selectbox("Select an island", df["island"].unique())

# Filtering the DataFrame based on user selection
filtered_df = df[df["island"] == island]

# Display the filtered results
st.write(f"Penguins in {island}:")
st.dataframe(filtered_df)