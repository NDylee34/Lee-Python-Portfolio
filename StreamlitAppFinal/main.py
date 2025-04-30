import streamlit as st
import pandas as pd
import requests
import random
import os
from datetime import datetime

# --- Configure the Streamlit app layout and metadata ---
st.set_page_config(page_title="NutriCompare 4.0", layout="wide")

# --- Load Nutritionix API credentials from secrets ---
NUTRITIONIX_APP_ID = st.secrets["NUTRITIONIX_APP_ID"]
NUTRITIONIX_API_KEY = st.secrets["NUTRITIONIX_API_KEY"]

# API endpoints for Nutritionix
NUTRITIONIX_SEARCH_URL = "https://trackapi.nutritionix.com/v2/search/instant"
NUTRITIONIX_NUTRIENTS_URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"

# Common headers to authenticate requests to Nutritionix
HEADERS = {
    "x-app-id": NUTRITIONIX_APP_ID,
    "x-app-key": NUTRITIONIX_API_KEY,
    "Content-Type": "application/json"
}

# --- Initialize default session state values ---
def init_state():
    defaults = {
        "gender": "Female",
        "weight": 60.0,
        "height": 165.0,
        "age": 25,
        "goal": "Maintenance",
        "activity": "Moderate",
        "meal_plan": [],  # Stores the generated meals
        "grocery_list": [],  # Stores food names for grocery checklist
        "history": set()  # Used to avoid repetition when picking meals
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# --- Calculate Basal Metabolic Rate (BMR) based on profile ---
def calculate_bmr(gender, weight, height, age):
    return 10 * weight + 6.25 * height - 5 * age + (5 if gender == "Male" else -161)

# --- Estimate daily calorie needs based on activity level and goal ---
def estimate_calories(goal, bmr, activity):
    factor = {"Sedentary": 1.2, "Moderate": 1.55, "Active": 1.725}[activity]
    base = bmr * factor
    if goal == "Muscle Gain":
        return base + 300
    elif goal == "Weight Loss":
        return base - 500
    else:
        return base

# --- Search common food items using Nutritionix's instant endpoint ---
def search_foods(query):
    res = requests.get(NUTRITIONIX_SEARCH_URL, headers=HEADERS, params={"query": query, "branded": False})
    if res.status_code == 200:
        common = res.json().get("common", [])
        # Filter out previously used items to ensure variety
        return [item["food_name"] for item in common if item["food_name"] not in st.session_state.history]
    return []

# --- Fetch macro + calorie data for a given food item ---
def get_nutrition(food):
    res = requests.post(NUTRITIONIX_NUTRIENTS_URL, headers=HEADERS, json={"query": food})
    if res.status_code == 200:
        food = res.json()["foods"][0]
        return {
            "Food": food["food_name"].title(),
            "Calories": food["nf_calories"],
            "Protein": food["nf_protein"],
            "Carbs": food["nf_total_carbohydrate"],
            "Fat": food["nf_total_fat"]
        }
    return None

# --- Sidebar Navigation ---
pages = ["Nutrition Analyzer", "Meal Planner", "Grocery List"]
page = st.sidebar.radio("📂 Navigate", pages)

# ========== PAGE 1: NUTRITION ANALYZER ========== #
if page == "Nutrition Analyzer":
    st.title("🥗 NutriCompare: Nutrition Analyzer")

    # Sidebar input form for user profile
    with st.sidebar:
        st.subheader("👤 Your Profile")
        st.session_state.gender = st.selectbox("Gender", ["Male", "Female"], index=["Male", "Female"].index(st.session_state.gender))
        st.session_state.weight = st.number_input("Weight (kg)", value=st.session_state.weight)
        st.session_state.height = st.number_input("Height (cm)", value=st.session_state.height)
        st.session_state.age = st.slider("Age", 12, 80, value=st.session_state.age)
        st.session_state.goal = st.selectbox("Goal", ["Maintenance", "Weight Loss", "Muscle Gain"], index=["Maintenance", "Weight Loss", "Muscle Gain"].index(st.session_state.goal))
        st.session_state.activity = st.selectbox("Activity", ["Sedentary", "Moderate", "Active"], index=["Sedentary", "Moderate", "Active"].index(st.session_state.activity))

    # Calculate calorie target and show as metric
    bmr = calculate_bmr(st.session_state.gender, st.session_state.weight, st.session_state.height, st.session_state.age)
    cal_goal = int(estimate_calories(st.session_state.goal, bmr, st.session_state.activity))
    st.metric("🎯 Daily Calorie Target", f"{cal_goal} kcal")

    # Text-based meal analysis
    st.subheader("🔍 Try Typing Meals to Analyze")
    foods = st.text_area("Enter each food on a new line")
    if st.button("Analyze Meals"):
        results = [get_nutrition(f) for f in foods.splitlines() if f.strip()]
        clean = [r for r in results if r]
        if clean:
            df = pd.DataFrame(clean)
            st.dataframe(df)
            totals = df.drop(columns="Food").sum()
            st.write("**Total:**")
            st.json(totals.to_dict())
        else:
            st.error("No valid entries found.")

# ========== PAGE 2: MEAL PLANNER ========== #
elif page == "Meal Planner":
    st.title("🍽️ AI-Powered Meal Planner")
    st.markdown("Create balanced meals personalized to your profile.")

    # Allow user to select dietary filters and number of days
    filters = st.multiselect("Dietary Filters", ["vegetarian", "low carb", "high protein", "dairy free"])
    days = st.slider("How many days to plan?", 1, 7, 3)

    # Reset meal plan and grocery list
    st.session_state.meal_plan = []
    st.session_state.grocery_list = []
    st.session_state.history = set()

    # Calorie goal from profile
    bmr = calculate_bmr(st.session_state.gender, st.session_state.weight, st.session_state.height, st.session_state.age)
    cal_goal = estimate_calories(st.session_state.goal, bmr, st.session_state.activity)

    if st.button("🔄 Generate Plan"):
        for d in range(days):
            for meal_type in ["Breakfast", "Lunch", "Dinner"]:
                # Split calories across meals
                portion = 0.3 if meal_type == "Breakfast" else 0.4 if meal_type == "Lunch" else 0.3
                target_cals = cal_goal * portion

                # Build query based on meal + filter
                search_term = f"{meal_type.lower()} {random.choice(filters) if filters else ''}".strip()
                options = search_foods(search_term)

                # Loop through search results to find something in range
                for food in options:
                    info = get_nutrition(food)
                    if info and 0.8 * target_cals < info["Calories"] < 1.2 * target_cals:
                        info["Day"] = f"Day {d+1}"
                        info["Meal"] = meal_type
                        st.session_state.meal_plan.append(info)
                        st.session_state.grocery_list.append(info["Food"])
                        st.session_state.history.add(food)
                        break

    # Display results in table format
    if st.session_state.meal_plan:
        df = pd.DataFrame(st.session_state.meal_plan)[["Day", "Meal", "Food", "Calories", "Protein", "Carbs", "Fat"]]
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Plan", csv, file_name="meal_plan.csv", mime="text/csv")

# ========== PAGE 3: GROCERY LIST ========== #
elif page == "Grocery List":
    st.title("🛒 Grocery List")

    if not st.session_state.grocery_list:
        st.info("No grocery list found. Run the Meal Planner first.")
    else:
        # Extract first word of each food item to generalize grocery items
        items = sorted(set([i.split()[0].capitalize() for i in st.session_state.grocery_list]))
        st.write("Based on your meal plan:")
        for i in items:
            st.markdown(f"- [ ] {i}")