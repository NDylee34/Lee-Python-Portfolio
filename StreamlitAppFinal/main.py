import streamlit as st
import pandas as pd
import requests
import random
import matplotlib.pyplot as plt
from datetime import datetime

# --- CONFIGURE PAGE ---
st.set_page_config(page_title="🥗 NutriCompare: Smart Meal & Nutrition Analyzer", layout="wide")

# --- NUTRITIONIX API (for Nutrition Analyzer only) ---
NUTRITIONIX_APP_ID = st.secrets["NUTRITIONIX_APP_ID"]
NUTRITIONIX_API_KEY = st.secrets["NUTRITIONIX_API_KEY"]
NUTRITIONIX_URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"
HEADERS = {
    "x-app-id": NUTRITIONIX_APP_ID,
    "x-app-key": NUTRITIONIX_API_KEY,
    "Content-Type": "application/json"
}

# --- SESSION STATE INIT ---
def init_state():
    defaults = {
        "gender": "Female",
        "weight": 60.0,
        "height": 165.0,
        "age": 25,
        "goal": "Maintenance",
        "activity": "Moderate",
        "meal_plan": [],
        "grocery_list": []
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# --- CALCULATIONS ---
def calculate_bmr(g, w, h, a):
    return 10 * w + 6.25 * h - 5 * a + (5 if g == "Male" else -161)

def estimate_calories(goal, bmr, activity):
    factor = {"Sedentary": 1.2, "Moderate": 1.55, "Active": 1.725}[activity]
    base = bmr * factor
    return base + (300 if goal == "Muscle Gain" else -500 if goal == "Weight Loss" else 0)

# --- LOCAL MEAL BANK ---
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

# --- PAGE NAVIGATION ---
pages = ["Nutrition Analyzer", "Meal Planner", "Grocery List"]
page = st.sidebar.radio("📂 Navigate", pages)

# --- SIDEBAR PROFILE ---
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

    st.subheader("🔍 Enter What You Ate")
    foods = st.text_area("Describe your meals (one item per line)")

    if st.button("Analyze Nutrition"):
        rows = []
        for food in foods.splitlines():
            if food.strip():
                res = requests.post(NUTRITIONIX_URL, headers=HEADERS, json={"query": food})
                if res.status_code == 200:
                    data = res.json()["foods"][0]
                    rows.append({
                        "Food": data["food_name"].title(),
                        "Calories": data["nf_calories"],
                        "Protein": data["nf_protein"],
                        "Carbs": data["nf_total_carbohydrate"],
                        "Fat": data["nf_total_fat"]
                    })
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df)
            totals = df.drop(columns="Food").sum()
            st.write("### Summary")
            st.json(totals.to_dict())

            # Donut chart
            import numpy as np
            
            labels = ["Protein", "Carbs", "Fat"]
            values = [totals["Protein"], totals["Carbs"], totals["Fat"]]
            colors = ["#6A5ACD", "#20B2AA", "#FF8C00"]
            
            fig, ax = plt.subplots(figsize=(5, 5))
            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                autopct="%1.1f%%",
                startangle=90,
                wedgeprops={"width": 0.4},
                colors=colors,
                textprops={"fontsize": 12})
            
            centre_circle = plt.Circle((0, 0), 0.70, fc="white")
            fig.gca().add_artist(centre_circle)
            
            ax.axis("equal")
            plt.title("Macronutrient Breakdown", fontsize=16)
            st.pyplot(fig)

        else:
            st.warning("No valid entries found.")

# --- PAGE 2: MEAL PLANNER ---
elif page == "Meal Planner":
    st.title("🍽️ Smart Metadata Meal Planner")
    filters = st.multiselect("Filters", ["vegetarian", "high protein", "dairy free"])
    days = st.slider("Days to plan", 1, 7, 3)

    st.session_state.meal_plan = []
    st.session_state.grocery_list = []

    if st.button("Generate Plan"):
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
        st.download_button("📥 Download Plan", df.to_csv(index=False).encode(), file_name="meal_plan.csv")

# --- PAGE 3: GROCERY LIST ---
elif page == "Grocery List":
    st.title("🛒 Grocery List")
    if st.session_state.grocery_list:
        items = sorted(set([i.split()[0].capitalize() for i in st.session_state.grocery_list]))
        for i in items:
            st.markdown(f"- [ ] {i}")
    else:
        st.info("Run the meal planner first.")