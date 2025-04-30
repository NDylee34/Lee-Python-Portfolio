import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import altair as alt
from dotenv import load_dotenv
import os
import base64
from PIL import Image

# --- PAGE SETUP ---
st.set_page_config(page_title="NutriCompare", layout="wide")

# --- LOAD ENV VARS ---
load_dotenv()
NUTRITIONIX_APP_ID = os.getenv("NUTRITIONIX_APP_ID")
NUTRITIONIX_API_KEY = os.getenv("NUTRITIONIX_API_KEY")

API_URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"
HEADERS = {
    "x-app-id": NUTRITIONIX_APP_ID,
    "x-app-key": NUTRITIONIX_API_KEY,
    "Content-Type": "application/json"
}

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
        return None

# --- SIDEBAR NAVIGATION ---
pages = ["Nutrition Analyzer", "Meal Planner", "Menu Scanner"]
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", pages)

# --- PAGE: NUTRITION ANALYZER ---
if selection == "Nutrition Analyzer":
    st.title("🥗 NutriCompare: Smart Meal & Nutrition Analyzer")
    st.markdown("""
    Upload your meals or manually enter what you ate. We'll analyze your nutrition, show you where you're doing well, and suggest improvements!
    """)

    # Personal info
    with st.sidebar:
        st.markdown("---")
        st.subheader("Set Your Goals")
        gender = st.selectbox("Gender", ["Male", "Female"])
        weight = st.number_input("Weight (kg)", value=65.0)
        height = st.number_input("Height (cm)", value=170.0)
        age = st.slider("Age", 12, 80, 25)
        goal = st.selectbox("Goal", ["Maintenance", "Weight Loss", "Muscle Gain"])
        activity = st.selectbox("Activity Level", ["Sedentary", "Moderate", "Active"])

    bmr = calculate_bmr(gender, weight, height, age)
    calorie_goal = estimate_calories(goal, bmr, activity)
    st.sidebar.metric("Calorie Goal", f"{int(calorie_goal)} kcal")

    input_method = st.radio("Choose Input Method:", ["Upload CSV", "Manual Entry"])
    data_rows = []

    if input_method == "Upload CSV":
        uploaded_file = st.file_uploader("Upload a CSV with a column 'Food'", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            if "Food" in df.columns:
                with st.spinner("Analyzing your foods..."):
                    for food in df["Food"]:
                        nutri_data = get_nutrition_data(food)
                        if nutri_data:
                            data_rows.append(nutri_data)
            else:
                st.error("CSV must contain a 'Food' column")

    elif input_method == "Manual Entry":
        st.subheader("Enter Food Items")
        food_items = st.text_area("Enter each food item on a new line:")
        if st.button("Analyze Nutrition"):
            with st.spinner("Analyzing your foods..."):
                for food in food_items.splitlines():
                    if food.strip():
                        nutri_data = get_nutrition_data(food)
                        if nutri_data:
                            data_rows.append(nutri_data)

    if data_rows:
        result_df = pd.DataFrame(data_rows)
        st.subheader("🥄 Nutrition Summary")
        st.dataframe(result_df)

        totals = result_df[["Calories", "Protein (g)", "Carbs (g)", "Fat (g)", "Sodium (mg)"]].sum().to_dict()
        st.write("**Total Daily Intake:**")
        st.json(totals)

        st.subheader("🍽️ Macronutrient Distribution")
        fig, ax = plt.subplots()
        ax.pie(
            [totals["Protein (g)"], totals["Carbs (g)"], totals["Fat (g)"]],
            labels=["Protein", "Carbs", "Fat"],
            autopct="%1.1f%%"
        )
        st.pyplot(fig)

        st.subheader("📈 Nutrient Comparison with Goals")
        recs = pd.DataFrame({
            'Nutrient': ['Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)'],
            'Goal': [calorie_goal, 50, 275, 70],
            'Actual': [totals['Calories'], totals['Protein (g)'], totals['Carbs (g)'], totals['Fat (g)']]
        })

        chart = alt.Chart(recs).transform_fold(
            ["Goal", "Actual"],
            as_=["Type", "Value"]
        ).mark_bar().encode(
            x=alt.X("Nutrient:N", title="Nutrient"),
            y=alt.Y("Value:Q"),
            color="Type:N"
        ).properties(width=600)

        st.altair_chart(chart)

        st.subheader("🧠 Nutrition Feedback")
        if totals["Calories"] < calorie_goal * 0.8:
            st.warning("Your calorie intake is significantly lower than your estimated needs.")
        elif totals["Calories"] > calorie_goal * 1.2:
            st.warning("You're eating much more than your estimated needs.")
        else:
            st.success("Your calorie intake is aligned with your goal!")

        if totals["Sodium (mg)"] > 2300:
            st.warning("High sodium intake detected. Consider lowering salt-heavy foods.")

# --- PAGE: MEAL PLANNER ---
elif selection == "Meal Planner":
    st.title("🍳 AI Meal Planner")
    st.write("We’ll suggest a sample meal plan based on your calorie goal.")

    calorie_goal = st.number_input("Enter your daily calorie goal:", value=2000)

    st.subheader("🕐 Suggested Meals")
    st.markdown("**Breakfast**: Greek yogurt with granola and berries (~25%)")
    st.markdown("**Lunch**: Grilled chicken salad with quinoa (~35%)")
    st.markdown("**Dinner**: Salmon, roasted vegetables, and sweet potato (~40%)")

    if st.button("Randomize Plan"):
        st.info("Coming soon: AI-based meal generator from a large nutrition database!")

# --- PAGE: MENU SCANNER ---
elif selection == "Menu Scanner":
    st.title("📸 Upload a Menu or Screenshot")
    st.write("We'll try to recommend the healthiest dishes for your goals.")

    uploaded_image = st.file_uploader("Upload an image or screenshot of a menu", type=["jpg", "png", "jpeg"])

    if uploaded_image:
        st.image(Image.open(uploaded_image), caption="Uploaded Menu", use_column_width=True)
        st.info("🧠 Coming soon: OCR + NLP to scan dishes and match to nutrition data.")