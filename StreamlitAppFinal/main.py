import streamlit as st
import pandas as pd
import requests
import altair as alt
import random
from datetime import datetime
from PIL import Image
import streamlit.components.v1 as components

# --- PAGE CONFIG ---
# Set up Streamlit page with title and wide layout
st.set_page_config(page_title="🌿 ThriveHub: Your Personal Wellness Companion", layout="wide")

# --- SECRETS ---
# Load API credentials for Nutritionix
NUTRITIONIX_APP_ID = st.secrets["NUTRITIONIX_APP_ID"]
NUTRITIONIX_API_KEY = st.secrets["NUTRITIONIX_API_KEY"]
API_URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"
HEADERS = {
    "x-app-id": NUTRITIONIX_APP_ID,
    "x-app-key": NUTRITIONIX_API_KEY,
    "Content-Type": "application/json"
}

# --- SESSION STATE DEFAULTS ---
# Initialize all session variables to store user input and logs
for key in ["gender", "weight", "height", "age", "goal", "activity", "data_rows", "mood_log", "activity_log", "selected_tab"]:
    if key not in st.session_state:
        st.session_state[key] = None if key not in ["data_rows", "mood_log", "activity_log"] else []

if st.session_state.selected_tab is None:
    st.session_state.selected_tab = "🏠 Home"


# --- NAVIGATION ---
# Sidebar tab selection
tabs = ["🏠 Home", "🍽️ Nutrition", "🧘 Mood & Mind", "🚶 Fitness Boost", "📈 Lifestyle Tracker"]
selection = st.sidebar.radio("Navigate ThriveHub:", tabs, index=tabs.index(st.session_state.selected_tab))
st.session_state.selected_tab = selection

# --- PROFILE SIDEBAR ---
# Persistent profile inputs in sidebar for all tabs
with st.sidebar:
    st.subheader("👤 Your Profile")
    st.session_state.gender = st.selectbox("Gender", ["Male", "Female"], index=0 if not st.session_state.gender else ["Male", "Female"].index(st.session_state.gender))
    st.session_state.weight = st.number_input("Weight (kg)", value=st.session_state.weight if st.session_state.weight else 65.0)
    st.session_state.height = st.number_input("Height (cm)", value=st.session_state.height if st.session_state.height else 170.0)
    st.session_state.age = st.slider("Age", 12, 80, value=st.session_state.age if st.session_state.age else 25)
    st.session_state.goal = st.selectbox("Goal", ["Maintenance", "Weight Loss", "Muscle Gain"], index=0 if not st.session_state.goal else ["Maintenance", "Weight Loss", "Muscle Gain"].index(st.session_state.goal))
    st.session_state.activity = st.selectbox("Activity Level", ["Sedentary", "Moderate", "Active"], index=0 if not st.session_state.activity else ["Sedentary", "Moderate", "Active"].index(st.session_state.activity))

# --- HOME PAGE ---
if st.session_state.selected_tab == "🏠 Home":
    st.markdown("<h1 style='text-align: center;'>🌿 ThriveHub</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Your Personal Wellness Companion</h3>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 👋 Welcome!")
    st.write("ThriveHub helps you track your nutrition, check in with your mood, move your body, and reflect on your lifestyle. Let’s thrive together — one mindful day at a time.")

    st.markdown("### 🌟 Choose where to begin:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🥗 Nutrition"):
            st.session_state.selected_tab = "🏋️ Nutrition"
    with col2:
        if st.button("🧘 Mood & Mind"):
            st.session_state.selected_tab = "🧘 Mood & Mind"
    col3, col4 = st.columns(2)
    with col3:
        if st.button("🚶 Fitness Boost"):
            st.session_state.selected_tab = "🚶 Fitness Boost"
    with col4:
        if st.button("📈 Lifestyle Tracker"):
            st.session_state.selected_tab = "📈 Lifestyle Tracker"

# --- FUNCTIONS ---
# Calculate BMR (Basal Metabolic Rate) using Mifflin-St Jeor equation
def calculate_bmr(gender, weight, height, age):
    return 10 * weight + 6.25 * height - 5 * age + (5 if gender == "Male" else -161)

# Estimate daily calorie needs based on goal and activity level
def estimate_calories(goal, bmr, activity):
    factor = {"Sedentary": 1.2, "Moderate": 1.55, "Active": 1.725}[activity]
    adjustment = {"Weight Loss": -500, "Maintenance": 0, "Muscle Gain": 300}[goal]
    return bmr * factor + adjustment

# Make API call to Nutritionix to get nutrition info for a food item
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

# --- NUTRITION PAGE ---
if st.session_state.selected_tab == "🍽️ Nutrition":
    st.title("🍎 Nutrition Tracker")
    
    # Calculate user's BMR and estimate their daily calorie needs
    bmr = calculate_bmr(st.session_state.gender, st.session_state.weight, st.session_state.height, st.session_state.age)
    calorie_goal = estimate_calories(st.session_state.goal, bmr, st.session_state.activity)
    st.sidebar.metric("🎯 Daily Calorie Goal", f"{int(calorie_goal)} kcal")

    # User selects how to enter food data: Upload or Manual
    input_method = st.radio("Choose Input Method:", ["Upload CSV", "Manual Entry"])

    # --- CSV Upload Option ---
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

    # --- Manual Entry Option ---
    if input_method == "Manual Entry":
        food_items = st.text_area("Enter food items (one per line):")
        if st.button("Analyze Nutrition"):
            st.session_state.data_rows.clear()
            for food in food_items.splitlines():
                if food.strip():
                    nutri_data = get_nutrition_data(food)
                    if nutri_data:
                        st.session_state.data_rows.append(nutri_data)

    # --- Display Nutritional Analysis ---
    if st.session_state.data_rows:
        result_df = pd.DataFrame(st.session_state.data_rows)
        st.dataframe(result_df)
        totals = result_df[["Calories", "Protein (g)", "Carbs (g)", "Fat (g)", "Sodium (mg)"]].sum()
        st.metric("Total Calories", f"{totals['Calories']:.0f} kcal")

        # Create a donut chart showing macronutrient breakdown
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

# --- MOOD & MIND PAGE ---
elif st.session_state.selected_tab == "🧘 Mood & Mind":
    st.title("🧠 Mood & Mind")

    # User selects mood and energy level
    mood = st.selectbox("How are you feeling?", ["Happy", "Stressed", "Tired", "Energetic", "Anxious", "Motivated"])
    energy = st.slider("Your energy level:", 0, 100, 50)

    # Log energy and mood when button is clicked
    if st.button("➕ Log Energy Level"):
        st.session_state.mood_log.append({"time": datetime.now(), "mood": mood, "energy": energy})
        st.success("Energy level added to your mood log!")

    st.markdown("### 🎧 Curated Playlist for You")
    playlist_embeds = {
        "Happy": "37i9dQZF1DXdPec7aLTmlC",
        "Energetic": "37i9dQZF1DX70RN3TfWWJh",
        "Tired": "37i9dQZF1DX0SM0LYsmbMT",
        "Stressed": "37i9dQZF1DWXe9gFZP0gtP",
        "Anxious": "37i9dQZF1DX4sWSpwq3LiO",
        "Motivated": "37i9dQZF1DXc5e2bJhV6pu",
    }
    embed_url = f"https://open.spotify.com/embed/playlist/{playlist_embeds[mood]}"
    components.iframe(embed_url, height=80, width=700)

    st.markdown("### 💬 Quote of the Day")
    quotes = {
        "Happy": "“Happiness is not something ready made. It comes from your own actions.” – Dalai Lama",
        "Stressed": "“Almost everything will work again if you unplug it for a few minutes, including you.” – Anne Lamott",
        "Tired": "“Rest and self-care are so important. When you take time to replenish your spirit, it allows you to serve others.” – Eleanor Brown",
        "Energetic": "“Energy and persistence conquer all things.” – Benjamin Franklin",
        "Anxious": "“You don’t have to control your thoughts. You just have to stop letting them control you.” – Dan Millman",
        "Motivated": "“Don’t watch the clock; do what it does. Keep going.” – Sam Levenson"
    }
    st.success(quotes[mood])

# --- FITNESS BOOST PAGE ---
elif st.session_state.selected_tab == "🚶 Fitness Boost":
    st.title("💪 Fitness Boost")
    st.caption("Get personalized movement suggestions and calorie estimates based on your energy level and activity.")

    # Ask for current energy level
    energy = st.slider("⚡ How much energy do you have right now?", 0, 100, 50)

    # Suggest workout based on energy
    if energy > 70:
        st.markdown("🏃 High Energy: Try a 30-min HIIT session or an outdoor run.")
    elif energy > 40:
        st.markdown("🧘 Moderate Energy: Try yoga or 20-min strength training.")
    else:
        st.markdown("🚶 Low Energy: Go for a short walk or light stretching.")

    # --- Activity Type & Calorie Burn Calculator ---
    st.markdown("### 🏃 Choose an Activity")
    activity_type = st.selectbox("Select an activity:", [
    "Cycling", "Running", "Stairmaster", "Weightlifting", "Swimming", "Hiking", "Outdoor Soccer", "Basketball", "Tennis"])

    # MET values per kg per minute for each activity
    calories_per_kg_per_min = {
        "Cycling": 0.14,
        "Running": 0.17,
        "Stairmaster": 0.20,
        "Weightlifting": 0.09,
        "Swimming": 0.13,
        "Hiking": 0.12,
        "Outdoor Soccer": 0.15,
        "Basketball": 0.12,
        "Tennis": 0.11
    }

    # Input desired calories to burn
    calories_to_burn = st.number_input("Enter how many calories you want to burn:", min_value=50, value=200)

    # Calculate time required based on selected activity and weight
    if st.session_state.weight:
        burn_rate = calories_per_kg_per_min[activity_type] * st.session_state.weight
        required_minutes = calories_to_burn / burn_rate
        st.info(f"You need approximately **{required_minutes:.1f} minutes** of {activity_type.lower()} to burn {calories_to_burn} kcal.")

    # --- Log activity when button clicked ---
    if st.button("📌 Log Today’s Activity"):
        if st.session_state.weight:
            burn_rate = calories_per_kg_per_min[activity_type] * st.session_state.weight
            duration = calories_to_burn / burn_rate
            calories = burn_rate * duration

            st.session_state.activity_log.append({
                "date": datetime.now().date(),
                "time": datetime.now(),
                "energy": energy,
                "activity": activity_type,
                "duration": round(duration, 1),
                "calories": round(calories, 1)
            })
            st.success(f"✅ Logged {activity_type.lower()} for {duration:.1f} minutes — {calories:.1f} kcal burned!")
        else:
            st.warning("Please enter your weight in the sidebar to calculate activity metrics.")

    # --- Display recent activity log ---
    if st.session_state.activity_log:
        st.markdown("### 📘 Recent Activity Log")
        for entry in reversed(st.session_state.activity_log[-5:]):
            st.markdown(f"**📅 {entry['date']}** — ⚡ Energy: {entry['energy']}/100")

# --- LIFESTYLE TRACKER PAGE ---
elif st.session_state.selected_tab == "📈 Lifestyle Tracker":
    st.title("📊 Lifestyle Tracker")
    st.caption("View how your mood and energy evolve over time — powered by your own entries.")

    # --- Mood & Mind Section ---
    from pytz import timezone

    st.subheader("🧠 Mood & Energy Log")

    if st.session_state.mood_log:
        mood_df = pd.DataFrame(st.session_state.mood_log)
        mood_df["time"] = pd.to_datetime(mood_df["time"])

        # Convert to Eastern Time
        eastern = timezone("US/Eastern")
        mood_df["time_est"] = mood_df["time"].dt.tz_localize("UTC").dt.tz_convert(eastern)

        if len(mood_df) == 1:
            # Use a dot chart for single entry
            mood_chart = alt.Chart(mood_df).mark_circle(size=150, color="#8BC34A").encode(
                x=alt.X("time_est:T", title="Date & Time (EST)", axis=alt.Axis(format="%b %d %I:%M %p")),
                y=alt.Y("energy:Q", title="Energy Level"),
                tooltip=["mood", "energy", "time_est"]
            ).properties(height=300, title="Mood-Based Energy Over Time")
        else:
            # Use area chart for multiple entries
            mood_chart = alt.Chart(mood_df).mark_area(
                line={"color": "#8BC34A"},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[
                        alt.GradientStop(color='#C8E6C9', offset=0),
                        alt.GradientStop(color='#4CAF50', offset=1)
                    ],
                    x1=1, x2=1, y1=1, y2=0
                )
            ).encode(
                x=alt.X("time_est:T", title="Date & Time (EST)", axis=alt.Axis(format="%b %d %I:%M %p")),
                y=alt.Y("energy:Q", title="Energy Level"),
                tooltip=["mood", "energy", "time_est"]
            ).properties(height=300, title="Mood-Based Energy Over Time")

        st.altair_chart(mood_chart, use_container_width=True)
    else:
        st.info("No mood data logged yet. Check the 🧠 Mood & Mind tab!")

    # --- Fitness Boost Section ---
    st.subheader("💪 Physical Activity Log")
    if st.session_state.activity_log:
        activity_df = pd.DataFrame(st.session_state.activity_log)
        activity_df["time"] = pd.to_datetime(activity_df["time"])
        activity_df = activity_df[["date", "energy", "activity", "duration", "calories"]].sort_values(by="date", ascending=False)

        # Display table with formatted headers
        st.dataframe(activity_df.rename(columns={
            "date": "📅 Date",
            "energy": "⚡ Energy Level",
            "activity": "🏃 Activity",
            "duration": "⏱️ Duration (min)",
            "calories": "🔥 Calories Burned"
        }), use_container_width=True)
    else:
        st.info("No fitness activity logged yet. Head over to 🚶 Fitness Boost tab!")