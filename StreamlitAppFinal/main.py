import streamlit as st
import pandas as pd
import requests
import altair as alt
import random
from PIL import Image

# --- PAGE CONFIG ---
st.set_page_config(page_title="🥗 NutriCompare: Smart Meal & Nutrition Analyzer", layout="wide")

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
for key in ["gender", "weight", "height", "age", "goal", "activity", "data_rows"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "data_rows" else []

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

# --- PAGE NAVIGATION ---
pages = ["Nutrition Analyzer", "Meal Planner", "Menu Scanner"]
selection = st.sidebar.radio("Navigation", pages)

# --- PAGE 1: NUTRITION ANALYZER ---
if selection == "Nutrition Analyzer":
    st.title("🥗 Nutrition Analyzer")
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

# --- PAGE 2: MEAL PLANNER ---
elif selection == "Meal Planner":
    st.title("🍽️ Personalized Meal Planner")

    if not st.session_state.age:
        st.warning("Please complete your profile on the Nutrition Analyzer page.")
    else:
        calorie_goal = estimate_calories(
            st.session_state.goal,
            calculate_bmr(st.session_state.gender, st.session_state.weight, st.session_state.height, st.session_state.age),
            st.session_state.activity
        )
        st.markdown(f"### 🌟 Daily Calorie Goal: `{int(calorie_goal)} kcal`")
        st.markdown("---")

        dietary_pref = st.multiselect("🍽️ Select preferences (optional):", ["Vegetarian", "High Protein", "Low Carb"])

        st.subheader("🎲 Click to generate a smart meal plan!")

        if st.button("Generate My Plan"):
            # Expanded meal pool
            breakfast_pool = [
                {"meal": "Oatmeal with fruit", "calories": 300, "tags": ["Vegetarian"]},
                {"meal": "Greek yogurt with granola", "calories": 400, "tags": ["Vegetarian", "High Protein"]},
                {"meal": "Scrambled eggs with toast", "calories": 350, "tags": ["High Protein"]},
                {"meal": "Smoothie with protein powder", "calories": 500, "tags": ["Vegetarian", "High Protein", "Low Carb"]},
                {"meal": "Avocado toast", "calories": 320, "tags": ["Vegetarian", "Low Carb"]},
                {"meal": "Protein pancakes", "calories": 430, "tags": ["Vegetarian", "High Protein"]},
                {"meal": "Egg muffins with spinach", "calories": 310, "tags": ["Low Carb", "High Protein"]},
                {"meal": "Banana chia pudding", "calories": 340, "tags": ["Vegetarian", "Low Carb"]},
                {"meal": "Tofu breakfast scramble", "calories": 370, "tags": ["Vegetarian", "High Protein"]},
                {"meal": "Apple almond butter toast", "calories": 380, "tags": ["Vegetarian"]},
            ]
            lunch_pool = [
                {"meal": "Grilled chicken salad", "calories": 500, "tags": ["Low Carb", "High Protein"]},
                {"meal": "Veggie wrap", "calories": 450, "tags": ["Vegetarian"]},
                {"meal": "Quinoa and black bean bowl", "calories": 550, "tags": ["Vegetarian", "High Protein"]},
                {"meal": "Turkey sandwich", "calories": 480, "tags": ["High Protein"]},
                {"meal": "Tofu stir-fry", "calories": 520, "tags": ["Vegetarian", "Low Carb"]},
                {"meal": "Shrimp and avocado salad", "calories": 510, "tags": ["Low Carb", "High Protein"]},
                {"meal": "Lentil soup", "calories": 490, "tags": ["Vegetarian"]},
                {"meal": "Grilled halloumi and veggies", "calories": 530, "tags": ["Vegetarian", "High Protein"]},
                {"meal": "Chicken quinoa power bowl", "calories": 560, "tags": ["High Protein"]},
                {"meal": "Falafel and tabbouleh plate", "calories": 540, "tags": ["Vegetarian"]},
            ]
            dinner_pool = [
                {"meal": "Baked salmon with broccoli", "calories": 600, "tags": ["Low Carb", "High Protein"]},
                {"meal": "Lentil stew", "calories": 550, "tags": ["Vegetarian"]},
                {"meal": "Zucchini noodles with chicken", "calories": 530, "tags": ["Low Carb", "High Protein"]},
                {"meal": "Beef stir-fry", "calories": 580, "tags": ["High Protein", "Low Carb"]},
                {"meal": "Chickpea curry", "calories": 540, "tags": ["Vegetarian"]},
                {"meal": "Stuffed bell peppers", "calories": 560, "tags": ["Vegetarian", "Low Carb"]},
                {"meal": "Grilled tofu with miso glaze", "calories": 500, "tags": ["Vegetarian", "High Protein"]},
                {"meal": "Shrimp cauliflower rice bowl", "calories": 520, "tags": ["Low Carb", "High Protein"]},
                {"meal": "Eggplant parm (light)", "calories": 540, "tags": ["Vegetarian"]},
                {"meal": "Chicken fajita bowl", "calories": 570, "tags": ["Low Carb", "High Protein"]},
            ]

            def filter_meals(pool, max_cal, prefs):
                return [
                    item["meal"] for item in pool
                    if item["calories"] <= max_cal and (not prefs or any(tag in item["tags"] for tag in prefs))
                ] or [item["meal"] for item in pool]

            b = random.choice(filter_meals(breakfast_pool, calorie_goal * 0.3, dietary_pref))
            l = random.choice(filter_meals(lunch_pool, calorie_goal * 0.35, dietary_pref))
            d = random.choice(filter_meals(dinner_pool, calorie_goal * 0.35, dietary_pref))

            st.markdown("### 🥣 Breakfast")
            st.markdown(f"- {b}")
            st.markdown("### 🥪 Lunch")
            st.markdown(f"- {l}")
            st.markdown("### 🍲 Dinner")
            st.markdown(f"- {d}")

        st.markdown("---")
        st.caption("Meals vary daily based on your preferences and nutrition goals 🎯")

# --- PAGE 3: MENU SCANNER ---
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
            st.info("🧠 OCR not enabled in this version, please upload a .txt file.")

    dish_lines = [line.strip() for line in menu_lines if len(line.strip()) > 3]
    if dish_lines:
        calorie_goal = estimate_calories(
            st.session_state.goal,
            calculate_bmr(st.session_state.gender, st.session_state.weight, st.session_state.height, st.session_state.age),
            st.session_state.activity
        )
        suggestions = []
        for line in dish_lines:
            nutri = get_nutrition_data(line)
            if nutri and nutri['Calories'] <= calorie_goal * 0.4:
                suggestions.append(nutri['Food'])

        if suggestions:
            st.subheader("✅ Healthier Dish Suggestions")
            for s in suggestions:
                st.markdown(f"- {s}")
        else:
            st.info("No suitable dishes found. Try uploading a cleaner or shorter menu.")