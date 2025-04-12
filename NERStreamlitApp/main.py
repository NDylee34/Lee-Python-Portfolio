import streamlit as st
import spacy
from spacy.pipeline import EntityRuler
import pandas as pd

st.set_page_config(page_title="Custom NER App", layout="centered")
st.title("🧠 Custom Named Entity Recognition (NER) App")

# Load a blank English spaCy model
nlp = spacy.blank("en")

# Add EntityRuler to pipeline
if "ruler" not in nlp.pipe_names:
    ruler = nlp.add_pipe("entity_ruler")
else:
    ruler = nlp.get_pipe("entity_ruler")

# Initialize session state to store patterns
if "patterns" not in st.session_state:
    st.session_state.patterns = []

# Sidebar: Add Custom Entity Patterns
st.sidebar.header("🛠️ Define Custom Entity Patterns")
label = st.sidebar.text_input(("Entity Label (e.g., BRAND, TOOL)").strip().upper(), "ORG")
patterns_input = st.sidebar.text_area("Entity Patterns (comma-separated)", "The Wall Street Journal, Federal Deposit Insurance Corp.")

if st.sidebar.button("➕ Add Pattern"):
    if label and patterns_input:
        new_patterns = [{"label": label, "pattern": word.strip()} for word in patterns_input.split(",")]
        st.session_state.patterns.extend(new_patterns)
        st.sidebar.success(f"✅ Added {len(new_patterns)} pattern(s) under '{label}'")

# Text Input Section
st.subheader("📄 Enter or Upload Text")
uploaded_file = st.file_uploader("Upload a text file", type="txt")
default_text = """President Donald Trump wanted to avoid sending the economy into a depression through his contentious plan for tariffs, according to The Wall Street Journal.

Trump privately said he was aware that his broad and steep plan for levies unveiled last week could tip the economy into a recession, but he didn’t want a depression, according to a Wednesday night report from the paper, citing people familiar with the conversations.

Trump also told advisors that he was willing to accept “pain” over the policy, a person who spoke with him on Monday told the Journal.

A depression is considered by economists to take place when a recession becomes more severe and entails higher unemployment and a more prolonged downturn. The U.S. has avoided them since the Great Depression in the 1930s — when unemployment hit 25% — because of progress in monetary policy and fiscal policy, along with programs like deposit insurance from the Federal Deposit Insurance Corp."""

text_input = ""
if uploaded_file:
    text_input = uploaded_file.read().decode("utf-8")
else:
    text_input = st.text_area("Or type/paste text below:", default_text, height=300)

# Run NER
if st.button("🚀 Run NER"):
    if not text_input.strip():
        st.warning("⚠️ Please upload or enter some text.")
    else:
        # Clear previous patterns and re-add current patterns from session state
        ruler.clear()
        ruler.add_patterns(st.session_state.patterns)

        # Process the text
        doc = nlp(text_input)

        # Display Detected Entities
        st.subheader("🔍 Entities Found")
        if doc.ents:
            ent_data = [(ent.text, ent.label_) for ent in doc.ents]
            st.dataframe(pd.DataFrame(ent_data, columns=["Entity", "Label"]))
        else:
            st.write("No entities found.")

        # Display Annotated Text
        st.subheader("🎨 Annotated Text")
        html = spacy.displacy.render(doc, style="ent", page=True)
        st.components.v1.html(html, height=300, scrolling=True)