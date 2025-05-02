import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt
from datetime import datetime

# --- Configure the app layout ---
st.set_page_config(page_title="NutriCompare", layout="wide")

# --- Session State Defaults ---
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
        "nutrition_log": []
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

# --- BMR and Calorie Goal ---
def calculate_bmr(g, w, h, a):
    return 10 * w + 6.25 * h - 5 * a + (5 if g == "Male" else -161)

def estimate_calories(goal, bmr, activity):
    factor = {"Sedentary": 1.2, "Moderate": 1.55, "Active": 1.725}[activity]
    base = bmr * factor
    return base + (300 if goal == "Muscle Gain" else -500 if goal == "Weight Loss" else 0)

# --- Local Meal Bank ---
meal_bank = [
    {"Meal": "Oatmeal with Berries", "Type": "Breakfast", "Calories": 350, "Protein": 12, "Carbs": 45, "Fat": 10, "Tags": ["vegetarian"]},
    {"Meal": "Greek Yogurt Parfait", "Type": "Breakfast", "Calories": 300, "Protein": 18, "Carbs": 25, "Fat": 8, "Tags": ["high protein"]},
    {"Meal": "Grilled Chicken Bowl", "Type": "Lunch", "Calories": 500, "Protein": 38, "Carbs": 30, "Fat": 20, "Tags": ["high protein"]},
    {"Meal": "Veggie Stir Fry", "Type": "Lunch", "Calories": 420, "Protein": 14, "Carbs": 40, "Fat": 18, "Tags": ["vegetarian", "dairy free"]},
    {"Meal": "Tofu Curry with Rice", "Type": "Dinner", "Calories": 530, "Protein": 22, "Carbs": 60, "Fat": 18, "Tags": ["vegetarian"]},
    {"Meal": "Salmon with Quinoa", "Type": "Dinner", "Calories": 600, "Protein": 42, "Carbs": 25, "Fat": 24, "Tags": ["high protein"]},
    {"Meal": "Chickpea Salad", "Type": "Lunch", "Calories": 380, "Protein": 16, "Carbs": 35, "Fat": 12, "Tags": ["vegetarian"]},
    {"Meal": "Egg & Avocado Toast", "Type": "Breakfast", "Calories": 320, "Protein": 14, "Carbs": 28, "Fat": 16, "Tags": []},
    {"Meal": "Chicken Fajita Bowl", "Type": "Dinner", "Calories": 550, "Protein": 36, "Carbs": 45, "Fat": 22, "Tags": []},
]

# --- Sidebar Navigation ---
pages = ["Nutrition Analyzer", "Meal Planner", "Grocery List"]
page = st.sidebar.radio("📂 Navigate", pages)

# --- Sidebar User Profile ---
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

# --- PAGE 1: NUTRITION ANALYZER ---
if page == "Nutrition Analyzer":
    st.title("📊 Nutrition Analyzer")
    st.metric("🎯 Estimated Calorie Target", f"{cal_goal} kcal")

    st.subheader("🔍 Manually Enter Meals")
    foods = st.text_area("Enter foods eaten (one per line):")
    if st.button("Analyze Meals"):
        entries = []
        for line in foods.splitlines():
            matches = [m for m in meal_bank if m["Meal"].lower() in line.lower()]
            if matches:
                entries.append(matches[0])
        if entries:
            df = pd.DataFrame(entries)
            st.dataframe(df[["Meal", "Calories", "Protein", "Carbs", "Fat"]])
            totals = df[["Calories", "Protein", "Carbs", "Fat"]].sum()
            st.write("### 🧾 Daily Summary")
            st.json(totals.to_dict())

            # Donut chart
            fig, ax = plt.subplots()
            ax.pie([totals["Protein"], totals["Carbs"], totals["Fat"]],
                   labels=["Protein", "Carbs", "Fat"],
                   autopct="%1.1f%%",
                   startangle=90, wedgeprops={"width": 0.3})
            st.pyplot(fig)
        else:
            st.warning("No matching meals found in database.")

# --- PAGE 2: MEAL PLANNER ---
elif page == "Meal Planner":
    st.title("🧠 Goal-Aligned Meal Planner")
    filters = st.multiselect("Apply Dietary Filters (optional)", ["vegetarian", "high protein", "low carb", "dairy free"])
    days = st.slider("Plan for how many days?", 1, 7, 3)

    st.session_state.meal_plan = []
    st.session_state.grocery_list = []

    if st.button("🌀 Generate Meal Plan"):
        for d in range(days):
            for meal_type in ["Breakfast", "Lunch", "Dinner"]:
                portion = 0.3 if meal_type == "Breakfast" else 0.4 if meal_type == "Lunch" else 0.3
                target = cal_goal * portion

                candidates = [m for m in meal_bank if m["Type"] == meal_type and
                              all(f in m["Tags"] for f in filters) and
                              0.8 * target <= m["Calories"] <= 1.2 * target]
                if not candidates:
                    candidates = [m for m in meal_bank if m["Type"] == meal_type]

                selected = random.choice(candidates)
                st.session_state.meal_plan.append({
                    "Day": f"Day {d+1}",
                    "Meal": meal_type,
                    "Food": selected["Meal"],
                    "Calories": selected["Calories"],
                    "Protein": selected["Protein"],
                    "Carbs": selected["Carbs"],
                    "Fat": selected["Fat"]
                })
                st.session_state.grocery_list.append(selected["Meal"])

    if st.session_state.meal_plan:
        df = pd.DataFrame(st.session_state.meal_plan)
        st.dataframe(df)
        st.download_button("📥 Download Plan", df.to_csv(index=False).encode(), "meal_plan.csv")

# --- PAGE 3: GROCERY LIST ---
elif page == "Grocery List":
    st.title("🛒 Grocery List Generator")
    if st.session_state.grocery_list:
        items = sorted(set(i.split()[0] for i in st.session_state.grocery_list))
        for i in items:
            st.markdown(f"- [ ] {i}")
    else:
        st.info("No plan yet — generate one from the Meal Planner page.")