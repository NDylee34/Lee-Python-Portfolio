# 🐧 Penguins! Streamlit App

Welcome to **Penguins!** — a beginner-friendly Streamlit app that allows users to interactively explore a dataset on penguins living on different islands.

---

## 📌 Project Overview

The app loads a CSV dataset containing information on various penguin species, including their location, physical characteristics, and demographic data. It introduces basic concepts of data loading and filtering in Streamlit.

---

## 💡 What is Streamlit?

[Streamlit](https://streamlit.io/) is an open-source Python framework that makes it easy to build interactive web applications for machine learning and data analysis. With minimal code, users can turn Python scripts into shareable apps that display data in real time — no front-end experience required.

---

## 🚀 Setup & Run Instructions

To run the Penguins! app locally, follow these steps:

### 1. Install Streamlit
```bash
pip install streamlit
```

### 2. Navigate to the project directory
```bash
cd basic-streamlit-app
```

### 3. Launch the app
```bash
streamlit run basic_streamlit_app/main.py
```

---

## 🧠 App Features

* 📂 **Data Import**: Loads a CSV dataset containing information about penguins' species, island, measurements, sex, and birth year.
* 🔍 **Interactive Filtering**: Users can filter the dataset based on the island using a dropdown menu.
* 📊 **Dynamic Display**: The app presents both the full dataset and the filtered view, allowing for easy comparison and exploration.

--- 
## 🔨 Future Improvements

* Add visualizations like bar charts for species counts by island
* Introduce multi-filtering (e.g. by sex or species)
* Display summary statistics (mean flipper length, weight, etc.)