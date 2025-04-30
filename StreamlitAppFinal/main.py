""
import streamlit as st
import pandas as pd
import random
from datetime import date

# ---------------------- Modular Wardrobe ---------------------- #
wardrobe = {
    "female": {
        "hot": {
            "tops": ["Crop Top", "Sleeveless Shirt", "Off-Shoulder Blouse", "Tank Top"],
            "bottoms": ["Maxi Skirt", "Linen Shorts", "Flowy Pants"],
            "shoes": ["Sandals", "Flip Flops", "Barefoot Flats"],
            "accessories": ["Straw Hat", "Sunglasses", "Beach Tote"]
        },
        "cold": {
            "tops": ["Wool Blazer", "Turtleneck", "Coat", "Cardigan"],
            "bottoms": ["Wool Pants", "Corduroy Skirt", "Thermal Leggings"],
            "shoes": ["Leather Boots", "Heeled Boots", "Chelsea Boots"],
            "accessories": ["Scarf", "Gloves", "Crossbody Bag"]
        },
        "mild": {
            "tops": ["Blouse", "Sweater", "Long Sleeve Tee"],
            "bottoms": ["Jeans", "Pleated Skirt", "Chinos"],
            "shoes": ["Sneakers", "Ballet Flats", "Loafers"],
            "accessories": ["Mini Backpack", "Necklace", "Watch"]
        },
        "rainy": {
            "tops": ["Raincoat", "Hooded Jacket", "Waterproof Parka"],
            "bottoms": ["Leggings", "Quick-Dry Pants", "Knee-Length Skirt"],
            "shoes": ["Rain Boots", "Waterproof Sneakers", "Rubber Flats"],
            "accessories": ["Umbrella", "Waterproof Tote", "Hood"]
        }
    },
    "male": {
        "hot": {
            "tops": ["Short Sleeve Shirt", "Tank Top", "Linen Button-Up"],
            "bottoms": ["Linen Shorts", "Swim Trunks", "Chino Shorts"],
            "shoes": ["Flip Flops", "Sandals", "Slides"],
            "accessories": ["Sunglasses", "Cap", "Beach Tote"]
        },
        "cold": {
            "tops": ["Blazer", "Overcoat", "Thermal Shirt"],
            "bottoms": ["Wool Pants", "Corduroy Trousers", "Jeans"],
            "shoes": ["Boots", "Chelsea Boots", "Derby Shoes"],
            "accessories": ["Scarf", "Beanie", "Messenger Bag"]
        },
        "mild": {
            "tops": ["Hoodie", "Sweatshirt", "Henley Shirt"],
            "bottoms": ["Jeans", "Joggers", "Chinos"],
            "shoes": ["Sneakers", "Loafers", "Slip-Ons"],
            "accessories": ["Watch", "Cap", "Fanny Pack"]
        },
        "rainy": {
            "tops": ["Rain Jacket", "Waterproof Hoodie", "Windbreaker"],
            "bottoms": ["Quick-Dry Pants", "Jeans", "Waterproof Shorts"],
            "shoes": ["Rain Boots", "Water-Resistant Sneakers", "Rubber Shoes"],
            "accessories": ["Umbrella", "Rain Hat", "Waterproof Backpack"]
        }
    }
}

mannequin_image = "https://via.placeholder.com/300x400.png?text=Your+Outfit"

# ---------------------- Helper Functions ---------------------- #
def detect_event_category(description):
    desc = description.lower()
    if "beach" in desc or "wedding" in desc:
        return "hot"
    elif "business" in desc or "meeting" in desc or "office" in desc:
        return "cold"
    elif "rain" in desc:
        return "rainy"
    else:
        return "mild"

def get_outfit_options(gender, event_desc, weather):
    weather_key = weather.lower()
    gender_key = "female" if gender == "Female" else "male"
    category = wardrobe[gender_key][weather_key]

    options = []
    for _ in range(3):
        top = random.choice(category["tops"])
        bottom = random.choice(category["bottoms"])
        shoes = random.choice(category["shoes"])
        accessory = random.choice(category["accessories"])
        options.append([top, bottom, shoes, accessory])
    return options

def generate_shopping_link(item, color_pref=""):
    query = "+".join((color_pref + " " + item).strip().split())
    return f"https://www.google.com/search?q={query}+clothing"

# ---------------------- Streamlit App ---------------------- #
st.set_page_config(page_title="Outfit Generator", layout="wide")

st.sidebar.title("Select Your Stylist")
page = st.sidebar.selectbox("Choose:", ["Female Client Stylist", "Male Client Stylist"])

# Session state for wishlist
if "wishlist" not in st.session_state:
    st.session_state.wishlist = []

st.title("👗 Your Personal Outfit Stylist")
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
    outfit_options = get_outfit_options(gender, event_desc, weather)

    st.subheader("Here are your personalized outfit ideas:")

    for idx, outfit in enumerate(outfit_options, 1):
        st.markdown(f"### 🌟 Option {idx}")
        st.image(mannequin_image, width=300)

        st.markdown("\n".join([
            f"👚 Top: {outfit[0]}",
            f"👖 Bottom: {outfit[1]}",
            f"👟 Shoes: {outfit[2]}",
            f"👜 Accessory: {outfit[3]}"
        ]))

        st.markdown("**🛍️ Shopping Links:**")
        for item in outfit:
            link = generate_shopping_link(item, color_pref)
            st.markdown(f"- [{item}]({link})")

        if st.button(f"❤️ Save Option {idx} to Wishlist", key=f"save_{idx}"):
            st.session_state.wishlist.append({
                "Option": idx,
                "Top": outfit[0],
                "Bottom": outfit[1],
                "Shoes": outfit[2],
                "Accessory": outfit[3],
                "Event": event_desc,
                "Location": location,
                "Date": str(event_date),
                "Weather": weather,
                "Color Preference": color_pref,
                "Budget": f"${budget[0]}-${budget[1]}"
            })
            st.success(f"Option {idx} saved to your wishlist!")

# Sidebar wishlist display
st.sidebar.subheader("🛍️ Your Wishlist")
if st.sidebar.button("View Wishlist"):
    if st.session_state.wishlist:
        wishlist_df = pd.DataFrame(st.session_state.wishlist)
        st.sidebar.dataframe(wishlist_df)
        st.sidebar.download_button("Download Wishlist as CSV", wishlist_df.to_csv(index=False), "wishlist.csv", "text/csv")
    else:
        st.sidebar.info("Your wishlist is empty!")
""