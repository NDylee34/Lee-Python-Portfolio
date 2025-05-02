import streamlit as st
import pandas as pd
import requests
import altair as alt
import random
from datetime import datetime
from PIL import Image

# --- PAGE CONFIG ---
st.set_page_config(page_title="🌿 ThriveHub: Your Personal Wellness Companion", layout="wide")

# --- SECRETS ---
NUTRITIONIX_APP_ID = st.secrets["NUTRITIONIX_APP_ID"]
NUTRITIONIX_API_KEY = st.secrets["NUTRITIONIX_API_KEY"]
API_URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"
HEADERS = {
    "x-app-id": NUTRITIONIX_APP_ID,
    "x-app-key": NUTRITIONIX_API_KEY,
    "Content-Type": "application/json"
}

# --- SESSION STATE DEFAULTS ---
for key in ["gender", "weight", "height", "age", "goal", "activity", "data_rows", "mood_log", "activity_log"]:
    if key not in st.session_state:
        st.session_state[key] = None if key not in ["data_rows", "mood_log", "activity_log"] else []

# --- FUNCTIONS ---
def calculate_bmr(gender, weight, height, age):
    return 10 * weight + 6.25 * height - 5 * age + (5 if gender == "Male" else -161)

def estimate_calories(goal, bmr, activity):
    factor = {"Sedentary": 1.2, "Moderate": 1.55, "Active": 1.725}[activity]
    adjustment = {"Weight Loss": -500, "Maintenance": 0, "Muscle Gain": 300}[goal]
    return bmr * factor + adjustment

def get_nutrition_data(food):
    response = requests.post(API_URL, headers=HEADERS, json={"query": food})
    if response.status_code == 200:
        nutrients = response.json()["foods"][0]
        return {
            "Food": nutrients["food_name"],
            "Calories": nutrients["nf_calories"],
            "Protein (g)": nutrients["nf_protein"],
            "Carbs (g)": nutrients["nf_total_carbohydrate"],
            "Fat (g)": nutrients["nf_total_fat"],
            "Sodium (mg)": nutrients.get("nf_sodium", 0)
        }
    else:
        st.error(f"API error: {response.status_code}")
        return None

# --- SIDEBAR NAVIGATION ---
tabs = ["🏠 Home", "🏋️ Nutrition", "🧘 Mood & Mind", "🚶 Fitness Boost", "📈 Lifestyle Tracker"]
if "selected_tab" not in st.session_state:
    st.session_state["selected_tab"] = "🏠 Home"

selection = st.sidebar.radio("Navigate ThriveHub:", tabs, index=tabs.index(st.session_state["selected_tab"]))
st.session_state["selected_tab"] = selection

# --- HOME TAB ---
if selection == "🏠 Home":
    st.markdown("<h1 style='text-align: center;'>🌿 ThriveHub</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Your Personal Wellness Companion</h3>", unsafe_allow_html=True)
    st.markdown("---")

    st.image("https://images.unsplash.com/photo-1571019613914-85f342c41a6c?auto=format&fit=crop&w=1650&q=80", use_column_width=True)

    st.markdown("### 👋 Welcome!")
    st.write(
        "ThriveHub is designed to support your physical and mental wellness. "
        "Whether you're tracking your nutrition, checking in with your mood, planning a workout, or just setting weekly goals — you're in the right place."
    )

    st.markdown("### 🧭 Where would you like to start?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🥗 Go to Nutrition"):
            st.session_state["selected_tab"] = "🏋️ Nutrition"
    with col2:
        if st.button("🧠 Go to Mood & Mind"):
            st.session_state["selected_tab"] = "🧘 Mood & Mind"

    col3, col4 = st.columns(2)
    with col3:
        if st.button("💪 Go to Fitness"):
            st.session_state["selected_tab"] = "🚶 Fitness Boost"
    with col4:
        if st.button("📊 Go to Lifestyle Tracker"):
            st.session_state["selected_tab"] = "📈 Lifestyle Tracker"

    # Redirect if button pressed
    if "selected_tab" in st.session_state and st.session_state["selected_tab"] != "🏠 Home":
        st.experimental_rerun()

# --- TAB 1: NUTRITION ---
if selection == "🍽️ Nutrition":
    st.title("🍎 Nutrition Tracker")

    with st.sidebar:
        st.subheader("👤 Your Profile")
        st.session_state.gender = st.selectbox("Gender", ["Male", "Female"])
        st.session_state.weight = st.number_input("Weight (kg)", value=65.0)
        st.session_state.height = st.number_input("Height (cm)", value=170.0)
        st.session_state.age = st.slider("Age", 12, 80, 25)
        st.session_state.goal = st.selectbox("Goal", ["Maintenance", "Weight Loss", "Muscle Gain"])
        st.session_state.activity = st.selectbox("Activity Level", ["Sedentary", "Moderate", "Active"])

    bmr = calculate_bmr(st.session_state.gender, st.session_state.weight, st.session_state.height, st.session_state.age)
    calorie_goal = estimate_calories(st.session_state.goal, bmr, st.session_state.activity)
    st.sidebar.metric("🎯 Daily Calorie Goal", f"{int(calorie_goal)} kcal")

    input_method = st.radio("Choose Input Method:", ["Upload CSV", "Manual Entry"])

    if input_method == "Upload CSV":
        uploaded_file = st.file_uploader("Upload CSV with a 'Food' column", type="csv")
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            if "Food" in df.columns:
                for food in df["Food"]:
                    nutri_data = get_nutrition_data(food)
                    if nutri_data:
                        st.session_state.data_rows.append(nutri_data)
            else:
                st.error("CSV must contain 'Food' column")

    if input_method == "Manual Entry":
        food_items = st.text_area("Enter food items (one per line):")
        if st.button("Analyze Nutrition"):
            st.session_state.data_rows.clear()
            for food in food_items.splitlines():
                if food.strip():
                    nutri_data = get_nutrition_data(food)
                    if nutri_data:
                        st.session_state.data_rows.append(nutri_data)

    if st.session_state.data_rows:
        result_df = pd.DataFrame(st.session_state.data_rows)
        st.dataframe(result_df)
        totals = result_df[["Calories", "Protein (g)", "Carbs (g)", "Fat (g)", "Sodium (mg)"]].sum()
        st.metric("Total Calories", f"{totals['Calories']:.0f} kcal")

        donut_data = pd.DataFrame({
            'Nutrient': ['Protein', 'Carbs', 'Fat'],
            'Grams': [totals["Protein (g)"], totals["Carbs (g)"], totals["Fat (g)"]]
        })

        donut_chart = alt.Chart(donut_data).mark_arc(innerRadius=50).encode(
            theta="Grams",
            color="Nutrient",
            tooltip=["Nutrient", "Grams"]
        ).properties(width=350, height=350)

        st.altair_chart(donut_chart)

# --- TAB 2: MOOD & MIND ---
elif selection == "🧘 Mood & Mind":
    st.title("🧠 Mood & Mind")

    mood = st.selectbox("How are you feeling?", ["Happy", "Stressed", "Tired", "Energetic", "Anxious", "Motivated"])
    energy = st.slider("Your energy level:", 0, 100, 50)

    st.session_state.mood_log.append({"time": datetime.now(), "mood": mood, "energy": energy})

    if mood in ["Happy", "Energetic"]:
        st.markdown("🎧 [Feel Good Hits](https://open.spotify.com/playlist/37i9dQZF1DXdPec7aLTmlC)")
    elif mood in ["Tired", "Stressed"]:
        st.markdown("🎧 [Chill Vibes](https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO)")
    else:
        st.markdown("🎧 [Motivation Mix](https://open.spotify.com/playlist/37i9dQZF1DX3rxVfibe1L0)")

    quotes = {
        "Happy": "“Happiness is not something ready made. It comes from your own actions.” – Dalai Lama",
        "Stressed": "“Almost everything will work again if you unplug it for a few minutes, including you.” – Anne Lamott",
        "Tired": "“Rest and self-care are so important. When you take time to replenish your spirit, it allows you to serve others.” – Eleanor Brown",
        "Energetic": "“Energy and persistence conquer all things.” – Benjamin Franklin",
        "Anxious": "“You don’t have to control your thoughts. You just have to stop letting them control you.” – Dan Millman",
        "Motivated": "“Don’t watch the clock; do what it does. Keep going.” – Sam Levenson"
    }

    st.success(quotes[mood])

# --- TAB 3: FITNESS BOOST ---
elif selection == "🏋️ Fitness Boost":
    st.title("💪 Fitness Boost")

    energy = st.slider("How much energy do you have right now?", 0, 100, 50)
    if energy > 70:
        st.markdown("🏃 Try a **30-min HIIT** session or an outdoor **run**")
    elif energy > 40:
        st.markdown("🧘 Try **yoga** or **20-min strength training**")
    else:
        st.markdown("🚶 Go for a **short walk** or light **stretching**")

    if st.button("Log today’s activity"):
        st.session_state.activity_log.append({"date": datetime.now().date(), "energy": energy})
        st.success("Activity logged!")

# --- TAB 4: LIFESTYLE TRACKER ---
elif selection == "📈 Lifestyle Tracker":
    st.title("📊 Lifestyle Tracker")

    st.subheader("📅 Mood Over Time")
    if st.session_state.mood_log:
        mood_df = pd.DataFrame(st.session_state.mood_log)
        mood_chart = alt.Chart(mood_df).mark_line(point=True).encode(
            x="time:T",
            y="energy:Q",
            tooltip=["mood", "energy", "time"]
        ).properties(height=300)
        st.altair_chart(mood_chart)
    else:
        st.info("No mood data yet.")

    st.subheader("📅 Activity Log")
    if st.session_state.activity_log:
        activity_df = pd.DataFrame(st.session_state.activity_log)
        activity_chart = alt.Chart(activity_df).mark_bar().encode(
            x="date:T",
            y="energy:Q"
        ).properties(height=200)
        st.altair_chart(activity_chart)
    else:
        st.info("No activity data yet.")