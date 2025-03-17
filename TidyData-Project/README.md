# 🏅 Tidy Data Project: Olympics 2008 Medalists

![Logo](images/2008_Summer_Olympics_logo.png)

## 📌 Project Overview
This project applies **tidy data principles** to a dataset containing **2008 Olympics medalists**. The goal is to **clean, reshape, analyze, and visualize** the data while ensuring it follows the **three core tidy data principles**:

1️⃣ Each **variable** has its own **column**.  
2️⃣ Each **observation** forms its **own row**.  
3️⃣ Each **type of observational unit** forms its **own table**.  

By restructuring the dataset, we **enable deeper analysis** of Olympic trends, gender distribution, and sport-specific performance.


## 📌 Instructions to Run the Notebook

### 1️⃣ **Clone the Repository**
```bash
git clone https://github.com/yourusername/TidyData-Project.git
cd TidyData-Project
```

### 2️⃣ **Install Dependencies**
Ensure you have Python and the required libraries installed. You can install dependencies using:
```bash
pip install pandas matplotlib seaborn jupyter
```

### 3️⃣ **Run the Jupyter Notebook**
```bash
jupyter notebook
```
Open **tidy_olympics_analysis.ipynb** and execute the cells to explore the dataset.


## 📌 Dataset Description

The dataset includes information about athletes who won medals in the **2008 Beijing Olympics**. Key attributes:

- **medalist_name** – Name of the athlete.  
- **sport** – Sport category.  
- **gender** – Male/Female classification.  
- **medal** – Gold, Silver, or Bronze.  

### 🔹 **Preprocessing Steps**
✔ **Reshaped** the dataset from **wide to long format**.  
✔ **Split** combined columns (`sport_gender`) into **two separate variables** (`sport` and `gender`).  
✔ **Cleaned and formatted** text values for consistency.  


## 📌 References
- 📄 **[Tidy Data Principles (Hadley Wickham)](https://vita.had.co.nz/papers/tidy-data.pdf)**
- 🛠️ **[Pandas Cheat Sheet](https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf)**


## 📌 Visual Examples

### **1️⃣ Top 10 Sports with Most Medals**
![Top Sports Bar Chart](images/Top%2010%20with%20Most%20Medals.png)

### **2️⃣ Medal Distribution by Gender**
![Medal Gender Distribution](images/Medal%20Distribution%20by%20Gender.png)

### **3️⃣ Medal Distribution by Sport**
![Medal Sport Distribution](images/Medal%20Distribution%20by%20Sport.png)


## 📌 Conclusion
This project successfully **transforms an unstructured Olympic data into a structured format** using **tidy data principles**, enabling clear analysis and storytelling through **visualizations and insights**.