# main.py (Modified to Remove API Dependency for Meal Generation)
# Author: [Your Name Here] — This version replaces Nutritionix calls with a local meal database

import streamlit as st
import pandas as pd
import random
from datetime import datetime

# --- Configure the Streamlit app layout and metadata ---
st.set_page_config(page_title="🥗 NutriCompare: Smart Meal & Nutrition Analyzer", layout="wide")

# --- Initialize default session state values ---
def init_state():
    defaults = {
        "gender": "Female",
        "weight": 60.0,
        "height": 165.0,
        "age": 25,
        "goal": "Maintenance",
        "activity": "Moderate",
        "meal_plan": [],
        "grocery_list": [],
        "history": set()
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# --- Local meal dataset (simulated) ---
meal_bank = [
    {"Meal": "Greek Yogurt with Berries", "Type": "Breakfast", "Calories": 300, "Protein": 20, "Carbs": 25, "Fat": 10, "Tags": ["high protein"]},
    {"Meal": "Oatmeal with Almond Butter", "Type": "Breakfast", "Calories": 350, "Protein": 12, "Carbs": 40, "Fat": 15, "Tags": ["vegetarian"]},
    {"Meal": "Egg White Omelette", "Type": "Breakfast", "Calories": 250, "Protein": 22, "Carbs": 10, "Fat": 12, "Tags": ["low carb"]},
    {"Meal": "Grilled Chicken Salad", "Type": "Lunch", "Calories": 450, "Protein": 35, "Carbs": 15, "Fat": 18, "Tags": ["low carb", "high protein"]},
    {"Meal": "Veggie Wrap with Hummus", "Type": "Lunch", "Calories": 400, "Protein": 14, "Carbs": 45, "Fat": 12, "Tags": ["vegetarian"]},
    {"Meal": "Tofu Stir Fry", "Type": "Dinner", "Calories": 500, "Protein": 25, "Carbs": 35, "Fat": 20, "Tags": ["vegetarian", "dairy free"]},
    {"Meal": "Salmon and Quinoa Bowl", "Type": "Dinner", "Calories": 600, "Protein": 40, "Carbs": 30, "Fat": 25, "Tags": ["high protein"]},
    {"Meal": "Chicken and Sweet Potatoes", "Type": "Dinner", "Calories": 550, "Protein": 35, "Carbs": 45, "Fat": 18, "Tags": []}
]

# --- BMR and calorie estimation ---
def calculate_bmr(gender, weight, height, age):
    return 10 * weight + 6.25 * height - 5 * age + (5 if gender == "Male" else -161)

def estimate_calories(goal, bmr, activity):
    factor = {"Sedentary": 1.2, "Moderate": 1.55, "Active": 1.725}[activity]
    base = bmr * factor
    if goal == "Muscle Gain":
        return base + 300
    elif goal == "Weight Loss":
        return base - 500
    else:
        return base

# --- Sidebar Navigation ---
pages = ["Nutrition Analyzer", "Meal Planner", "Grocery List"]
page = st.sidebar.radio("📂 Navigate", pages)

# --- PAGE 1: NUTRITION ANALYZER ---
if page == "Nutrition Analyzer":
    st.title("🥗 NutriCompare: Nutrition Analyzer")

    with st.sidebar:
        st.subheader("👤 Your Profile")
        st.session_state.gender = st.selectbox("Gender", ["Male", "Female"], index=["Male", "Female"].index(st.session_state.gender))
        st.session_state.weight = st.number_input("Weight (kg)", value=st.session_state.weight)
        st.session_state.height = st.number_input("Height (cm)", value=st.session_state.height)
        st.session_state.age = st.slider("Age", 12, 80, value=st.session_state.age)
        st.session_state.goal = st.selectbox("Goal", ["Maintenance", "Weight Loss", "Muscle Gain"], index=["Maintenance", "Weight Loss", "Muscle Gain"].index(st.session_state.goal))
        st.session_state.activity = st.selectbox("Activity", ["Sedentary", "Moderate", "Active"], index=["Sedentary", "Moderate", "Active"].index(st.session_state.activity))

    bmr = calculate_bmr(st.session_state.gender, st.session_state.weight, st.session_state.height, st.session_state.age)
    cal_goal = int(estimate_calories(st.session_state.goal, bmr, st.session_state.activity))
    st.metric("🎯 Daily Calorie Target", f"{cal_goal} kcal")

# --- PAGE 2: MEAL PLANNER ---
elif page == "Meal Planner":
    st.title("🍽️ Smart Meal Planner (Offline Mode)")

    filters = st.multiselect("Dietary Filters", ["vegetarian", "low carb", "high protein", "dairy free"])
    days = st.slider("How many days to plan?", 1, 7, 3)

    st.session_state.meal_plan = []
    st.session_state.grocery_list = []

    bmr = calculate_bmr(st.session_state.gender, st.session_state.weight, st.session_state.height, st.session_state.age)
    cal_goal = estimate_calories(st.session_state.goal, bmr, st.session_state.activity)

    if st.button("🔄 Generate Plan"):
        for d in range(days):
            for meal_type in ["Breakfast", "Lunch", "Dinner"]:
                portion = 0.3 if meal_type == "Breakfast" else 0.4 if meal_type == "Lunch" else 0.3
                target_cals = cal_goal * portion
                
                # Filter meals by type, tag, and calorie range
                filtered = [m for m in meal_bank if m["Type"] == meal_type and \
                            all(tag in m["Tags"] for tag in filters) and \
                            0.8 * target_cals < m["Calories"] < 1.2 * target_cals]

                # Fallback if too few matches
                if not filtered:
                    filtered = [m for m in meal_bank if m["Type"] == meal_type]

                meal = random.choice(filtered)
                st.session_state.meal_plan.append({
                    "Day": f"Day {d+1}",
                    "Meal": meal["Type"],
                    "Food": meal["Meal"],
                    "Calories": meal["Calories"],
                    "Protein": meal["Protein"],
                    "Carbs": meal["Carbs"],
                    "Fat": meal["Fat"]
                })
                st.session_state.grocery_list.append(meal["Meal"])

    if st.session_state.meal_plan:
        df = pd.DataFrame(st.session_state.meal_plan)[["Day", "Meal", "Food", "Calories", "Protein", "Carbs", "Fat"]]
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Plan", csv, file_name="meal_plan.csv", mime="text/csv")

# --- PAGE 3: GROCERY LIST ---
elif page == "Grocery List":
    st.title("🛒 Grocery List")

    if not st.session_state.grocery_list:
        st.info("No grocery list found. Run the Meal Planner first.")
    else:
        items = sorted(set([i.split()[0].capitalize() for i in st.session_state.grocery_list]))
        st.write("Based on your meal plan:")
        for i in items:
            st.markdown(f"- [ ] {i}")