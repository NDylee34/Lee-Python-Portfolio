import streamlit as st
import pandas as pd
import random
from datetime import date

# --- Placeholder outfit images ---
female_images = [
    "https://images.unsplash.com/photo-1514996937319-344454492b37",
    "https://images.unsplash.com/photo-1520975922323-1c77d93b6939",
    "https://images.unsplash.com/photo-1503341455253-b2e723bb3dbb"
]

male_images = [
    "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab",
    "https://images.unsplash.com/photo-1520697222868-5203b57c58b3",
    "https://images.unsplash.com/photo-1573497161423-5f7c1a6a122d"
]

# --- Outfit templates ---
female_outfits = [
    ["Floral Dress", "Light Jacket", "Wedges", "Clutch Bag"],
    ["Blouse", "A-line Skirt", "Ballet Flats", "Handbag"],
    ["Crop Top", "Wide-leg Pants", "Sandals", "Crossbody Bag"]
]

male_outfits = [
    ["Polo Shirt", "Chinos", "Loafers", "Watch"],
    ["Dress Shirt", "Tailored Pants", "Oxford Shoes", "Briefcase"],
    ["T-shirt", "Jeans", "Sneakers", "Cap"]
]

# --- Helper functions ---
def generate_outfits(gender, weather, event_desc):
    if gender == "Female":
        base_outfits = female_outfits
    else:
        base_outfits = male_outfits

    # Simple random selection; could be smarter with event matching
    outfits = random.sample(base_outfits, 3)
    return outfits

def get_image(gender):
    if gender == "Female":
        return random.choice(female_images)
    else:
        return random.choice(male_images)

def generate_shopping_link(item, color_pref=""):
    query = "+".join((color_pref + " " + item).strip().split())
    return f"https://www.google.com/search?q={query}+clothing"

# --- Streamlit App ---
st.set_page_config(page_title="Outfit Generator", layout="wide")

st.sidebar.title("Select Your Stylist")
page = st.sidebar.selectbox("Choose:", ["Female Client Stylist", "Male Client Stylist"])

# Session state for wishlist
if "wishlist" not in st.session_state:
    st.session_state.wishlist = []

st.title("👗 Your Personal Outfit Stylist")

# --- Input Form ---
st.header(f"{page} Experience")

with st.form("user_inputs"):
    location = st.text_input("Event Location (City)")
    event_date = st.date_input("Event Date", min_value=date.today())
    event_desc = st.text_input("Describe your event (e.g., beach wedding, business meeting, hiking)")
    weather = st.selectbox("Select the weather:", ["Hot", "Cold", "Rainy", "Mild"])
    color_pref = st.text_input("Preferred Colors (optional)")
    budget = st.slider("Budget Range ($)", 0, 1000, (50, 300))

    submitted = st.form_submit_button("Generate Outfits")

if submitted:
    gender = "Female" if page == "Female Client Stylist" else "Male"

    outfit_options = generate_outfits(gender, weather, event_desc)

    st.subheader("Here are your outfit ideas!")

    for idx, outfit in enumerate(outfit_options, 1):
        st.markdown(f"### 🌟 Option {idx}")
        st.image(get_image(gender), width=300)
        for item in outfit:
            link = generate_shopping_link(item, color_pref)
            st.markdown(f"- [{item}]({link})")

        # Save button
        if st.button(f"Save Option {idx} to Wishlist", key=f"save_{idx}"):
            st.session_state.wishlist.append({
                "Option": idx,
                "Outfit": ", ".join(outfit),
                "Event": event_desc,
                "Location": location,
                "Date": str(event_date),
                "Weather": weather,
                "Color Preference": color_pref,
                "Budget Range": f"${budget[0]}-${budget[1]}"
            })
            st.success(f"Option {idx} saved to your wishlist!")

st.sidebar.subheader("🛍️ Your Wishlist")
if st.sidebar.button("View Wishlist"):
    if st.session_state.wishlist:
        wishlist_df = pd.DataFrame(st.session_state.wishlist)
        st.sidebar.dataframe(wishlist_df)
        st.sidebar.download_button("Download Wishlist as CSV", wishlist_df.to_csv(index=False), "wishlist.csv", "text/csv")
    else:
        st.sidebar.info("Your wishlist is empty!")