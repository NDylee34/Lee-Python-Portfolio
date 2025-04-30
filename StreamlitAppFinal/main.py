# main.py
import streamlit as st
import pandas as pd
import requests
import altair as alt
import os
import random
from PIL import Image

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
        calorie_goal = estimate_calories(
            st.session_state.goal,
            calculate_bmr(st.session_state.gender, st.session_state.weight, st.session_state.height, st.session_state.age),
            st.session_state.activity
        )

        st.markdown(f"### 🌟 Daily Calorie Goal: `{int(calorie_goal)} kcal`")
        st.markdown("---")

        st.subheader("🎲 Click below to generate a fresh meal plan!")

        if st.button("Generate My Plan"):
            breakfast_pool = [
                ("Oatmeal with berries", "https://www.allrecipes.com/recipe/244251/easy-oatmeal-with-banana-and-peanut-butter/"),
                ("Greek yogurt & honey", "https://www.allrecipes.com/recipe/223180/honey-greek-yogurt/"),
                ("Spinach mushroom omelette", "https://www.allrecipes.com/recipe/23640/mushroom-omelet/"),
                ("Peanut butter toast & banana", "https://www.eatingwell.com/recipe/252652/peanut-butter-banana-toast/"),
                ("Protein smoothie with almond milk", "https://www.allrecipes.com/recipe/232028/banana-protein-smoothie/")
            ]
            lunch_pool = [
                ("Quinoa bowl with roasted veggies", "https://www.loveandlemons.com/roasted-veggie-quinoa-bowl/"),
                ("Grilled chicken wrap", "https://www.allrecipes.com/recipe/218634/grilled-chicken-wraps/"),
                ("Tofu poke bowl", "https://www.allrecipes.com/recipe/270351/tofu-poke-bowl/"),
                ("Turkey sandwich & side salad", "https://www.allrecipes.com/recipe/240820/healthy-turkey-sandwich/"),
                ("Lentil soup with avocado toast", "https://www.allrecipes.com/recipe/26692/lentil-soup/"),
            ]
            dinner_pool = [
                ("Salmon & asparagus", "https://www.allrecipes.com/recipe/240708/baked-salmon-asparagus-foil-packets/"),
                ("Tofu veggie stir-fry", "https://www.loveandlemons.com/tofu-stir-fry/"),
                ("Zucchini noodles with chicken", "https://www.eatingwell.com/recipe/268709/zucchini-noodles-with-chicken-tomatoes-avocado-pesto/"),
                ("Steak & sweet potato", "https://www.eatingwell.com/recipe/250660/grilled-steak-sweet-potatoes-with-orange-avocado-salsa/"),
                ("Shrimp & brown rice bowl", "https://www.allrecipes.com/recipe/273275/garlic-shrimp-stir-fry/")
            ]

            breakfast = random.choice(breakfast_pool)
            lunch = random.choice(lunch_pool)
            dinner = random.choice(dinner_pool)

            st.markdown("### 🥣 Breakfast")
            st.markdown(f"**[{breakfast[0]}]({breakfast[1]})**")

            st.markdown("### 🥪 Lunch")
            st.markdown(f"**[{lunch[0]}]({lunch[1]})**")

            st.markdown("### 🍲 Dinner")
            st.markdown(f"**[{dinner[0]}]({dinner[1]})**")

        st.markdown("---")
        st.caption("Randomized daily meals powered by curated healthy recipes ✨")

# --- PAGE: MENU SCANNER ---
elif selection == "Menu Scanner":
    st.title("📷 Menu Scanner")
    uploaded_file = st.file_uploader("Upload a menu screenshot (.jpg, .png) or text file", type=["txt", "png", "jpg", "jpeg"])

    menu_lines = []
    if uploaded_file:
        if uploaded_file.name.endswith(".txt"):
            raw_text = uploaded_file.read().decode("utf-8")
            st.text_area("Scanned Menu Text", value=raw_text, height=200)
            menu_lines = raw_text.splitlines()
        else:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Menu", use_column_width=True)
            st.info("🧠 OCR not enabled in this version, please use .txt upload for now.")

    dish_lines = [line.strip() for line in menu_lines if len(line.strip()) > 3]
    if dish_lines:
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