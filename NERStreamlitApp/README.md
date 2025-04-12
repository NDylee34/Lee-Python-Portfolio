# 🧠 Custom Named Entity Recognition (NER) Streamlit App

Welcome to the Custom NER App! This interactive web tool allows you to explore Named Entity Recognition using [spaCy](https://spacy.io/) and [Streamlit](https://streamlit.io/). You can define your own labels and entity patterns, upload or enter text, and visually explore detected entities.

🔗 **Live App**: [https://lee-ner.streamlit.app/](https://lee-ner.streamlit.app/)

---

## 📌 Project Overview

Named Entity Recognition (NER) is a Natural Language Processing (NLP) technique used to identify real-world entities (like people, organizations, and places) in text. This app uses **spaCy’s rule-based `EntityRuler`** to let users define custom patterns for entity detection and visualize results interactively.

---

## 💡 Installation & Local Setup

To run the app locally:

### 1. Clone the repository
```bash
git clone https://github.com/NDylee34/NERStreamlitApp.git
cd NERStreamlitApp
```

### 2. Create a virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install required packages
```bash
pip install -r requirements.txt
```

### 4. Launch the app
```bash
streamlit run app.py
```

---

## 🚀 App Features

### Upload or Paste Text
Users can either:
- Upload a `.txt` file, **OR**
- Paste or type text directly into the textbox

<img src="images/User%20Input.jpg" alt="User Input" width="500"/>

**Example Default Text:**
> President Donald Trump wanted to avoid sending the economy into a depression...  
> According to The Wall Street Journal...

---

### ✅ Define Custom Entities

Use the **sidebar** to create custom entity types:
- **Entity Label**: the category name (e.g., PERSON, ORG, BRAND, ENTITY)
- **Entity Patterns**: comma-separated phrases to identify in the text

💬 Example:
- **Label**: `ORG`
- **Patterns**: `The Wall Street Journal, Federal Deposit Insurance Corp.`

📌 Click the ➕ **"Add Pattern"** button to save your rules.

<img src="images/Custom%20Entity.jpg" alt="Custom Entity" width="300"/>
---

### ✅ Run NER and View Results

- Click **"🚀 Run NER"** to process your text using the added patterns.
- The app shows:
  - A table of all detected entities and their labels
  - A visual rendering of your text with highlighted entities

<img src="images/Run%20NER.jpg" alt="Run NER" width="500"/>
---

## 📚 References

- [spaCy: 101](https://spacy.io/api)
- [spaCy: EntityRuler](https://spacy.io/api/entityruler)
- [spaCy Rule-based Matching](https://spacy.io/usage/rule-based-matching)
- [Named Entity Recognition – Wikipedia](https://en.wikipedia.org/wiki/Named-entity_recognition)

---

## 📬 Feedback

Have ideas for improving the app? Feel free to fork, contribute, or open an issue in the repository.