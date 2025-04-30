# main.py
import streamlit as st
import pandas as pd
import requests
import altair as alt
import matplotlib.pyplot as plt
import os
import random
from PIL import Image
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="NutriCompare", layout="wide")

# --- LOAD SECRETS ---
NUTRITIONIX_APP_ID = st.secrets["NUTRITIONIX_APP_ID"]
NUTRITIONIX_API_KEY = st.secrets["NUTRITIONIX_API_KEY"]

API_URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"
HEADERS = {
    "x-app-id": NUTRITIONIX_APP_ID,
    "x-app-key": NUTRITIONIX_API_KEY,
    "Content-Type": "application/json"
}

# --- SESSION STATE DEFAULTS ---
for key in ["gender", "weight", "height", "age", "goal", "activity", "data_rows"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "data_rows" else []

# --- BMR CALCULATION FUNCTION ---
def calculate_bmr(gender, weight, height, age):
    if gender == "Male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

# --- CALORIE GOAL ESTIMATION ---
def estimate_calories(goal, bmr, activity):
    factor = 1.2 if activity == "Sedentary" else 1.55 if activity == "Moderate" else 1.725
    base = bmr * factor
    if goal == "Weight Loss":
        return base - 500
    elif goal == "Muscle Gain":
        return base + 300
    else:
        return base

# --- GET NUTRITION DATA ---
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
        st.error(f"API error: {response.status_code} — {response.text}")
        return None

# --- PAGE NAVIGATION ---
pages = ["Nutrition Analyzer", "Meal Planner", "Menu Scanner"]
selection = st.sidebar.radio("Navigation", pages)

# --- PAGE: NUTRITION ANALYZER ---
if selection == "Nutrition Analyzer":
    st.title("🥗 NutriCompare: Nutrition Analyzer")
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
    st.sidebar.metric("Estimated Daily Calorie Goal", f"{int(calorie_goal)} kcal")

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

# --- PAGE: MEAL PLANNER ---
elif selection == "Meal Planner":
    st.title("🍽️ Personalized Meal Planner")

    if not st.session_state.age:
        st.warning("Go to the Nutrition Analyzer page to enter your profile first.")
    else:
        calorie_goal = estimate_calories(st.session_state.goal, calculate_bmr(st.session_state.gender, st.session_state.weight, st.session_state.height, st.session_state.age), st.session_state.activity)
        st.write(f"Daily Calorie Goal: **{int(calorie_goal)} kcal**")

        meals = {
            "Breakfast": ["Oatmeal with banana", "Scrambled eggs with spinach", "Smoothie with protein powder"],
            "Lunch": ["Grilled chicken salad", "Turkey wrap with veggies", "Quinoa bowl with tofu"],
            "Dinner": ["Baked salmon with rice", "Veggie stir-fry with tofu", "Grilled steak with sweet potato"]
        }

        if st.button("Randomize Meal Plan"):
            for meal, options in meals.items():
                st.markdown(f"**{meal}:** {random.choice(options)}")

# --- PAGE: MENU SCANNER ---
elif selection == "Menu Scanner":
    st.title("📷 Menu Scanner")
    uploaded_file = st.file_uploader("Upload a text file of a menu (e.g., .txt)", type="txt")

    if uploaded_file:
        raw_text = uploaded_file.read().decode("utf-8")
        st.text_area("Scanned Menu Text", value=raw_text, height=200)

        dish_lines = [line.strip() for line in raw_text.splitlines() if len(line.strip()) > 3]
        suggestions = []
        for line in dish_lines:
            nutri = get_nutrition_data(line)
            if nutri and nutri['Calories'] <= estimate_calories(st.session_state.goal, calculate_bmr(st.session_state.gender, st.session_state.weight, st.session_state.height, st.session_state.age), st.session_state.activity) * 0.4:
                suggestions.append(nutri['Food'])

        if suggestions:
            st.subheader("✅ Healthier Dish Suggestions")
            for s in suggestions:
                st.markdown(f"- {s}")
        else:
            st.info("No suitable dishes found. Try uploading a clearer text menu.")