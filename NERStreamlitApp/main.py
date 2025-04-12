import streamlit as st
import spacy
from spacy.pipeline import EntityRuler
import pandas as pd

st.set_page_config(page_title="Custom NER App", layout="centered")
st.title("🧠 Custom Named Entity Recognition (NER) App")

# Initialize spaCy blank English model
nlp = spacy.blank("en")

# Add EntityRuler to pipeline
if "ruler" not in nlp.pipe_names:
    ruler = nlp.add_pipe("entity_ruler")
else:
    ruler = nlp.get_pipe("entity_ruler")

# Sidebar for Entity Patterns
st.sidebar.header("🛠️ Define Custom Entity Patterns")
label = st.sidebar.text_input("Entity Label (e.g., BRAND, TOOL)").strip().upper()
patterns_input = st.sidebar.text_area("Entity Patterns (comma-separated)", "Python, Streamlit, spaCy")

if st.sidebar.button("➕ Add Pattern"):
    if label and patterns_input:
        new_patterns = [{"label": label, "pattern": word.strip()} for word in patterns_input.split(",")]
        ruler.add_patterns(new_patterns)
        st.sidebar.success(f"Added {len(new_patterns)} patterns under '{label}'")

# Text Input Section
st.subheader("📄 Enter or Upload Text")
uploaded_file = st.file_uploader("Upload a text file", type="txt")
default_text = "Streamlit is a great tool for data apps. spaCy excels in natural language processing."

text_input = ""
if uploaded_file:
    text_input = uploaded_file.read().decode("utf-8")
else:
    text_input = st.text_area("Or type/paste text below:", default_text)

# Run NER
if st.button("🚀 Run NER"):
    if not text_input:
        st.warning("Please upload or enter some text.")
    else:
        doc = nlp(text_input)

        # Show results table
        st.subheader("🔍 Entities Found")
        if doc.ents:
            ent_data = [(ent.text, ent.label_) for ent in doc.ents]
            st.dataframe(pd.DataFrame(ent_data, columns=["Entity", "Label"]))
        else:
            st.write("No entities found.")

        # Show visual output
        st.subheader("🎨 Annotated Text")
        html = spacy.displacy.render(doc, style="ent", page=True)
        st.components.v1.html(html, height=300, scrolling=True)