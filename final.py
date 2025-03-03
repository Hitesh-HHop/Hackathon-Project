import streamlit as st
import sqlite3
import random
import google.generativeai as genai
import time
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(layout="wide")

# Initialize SQLite Database
conn = sqlite3.connect("recipes.db", check_same_thread=False)
c = conn.cursor()

# Create Tables if they don't exist
c.execute('''CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY, 
                name TEXT, 
                password TEXT
            )''')

c.execute('''CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT, 
                recipe_name TEXT, 
                recipe_text TEXT,
                FOREIGN KEY(email) REFERENCES users(email)
            )''')
conn.commit()

# Function to register a new user
def register_user(email, name, password):
    c.execute("INSERT INTO users (email, name, password) VALUES (?, ?, ?)", (email, name, password))
    conn.commit()

# Function to check user login
def login_user(email, password):
    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    return c.fetchone()

# Function to get user recipes
def get_user_recipes(email):
    c.execute("SELECT recipe_name, recipe_text FROM recipes WHERE email = ?", (email,))
    result = c.fetchall()
    return dict(result) if result else {}  # Ensure it returns a dictionary

# Function to save or update recipe
def save_or_update_recipe(email, recipe_name, recipe_text):
    c.execute("SELECT * FROM recipes WHERE email = ? AND recipe_name = ?", (email, recipe_name))
    existing_recipe = c.fetchone()
    if existing_recipe:
        c.execute("UPDATE recipes SET recipe_text = ? WHERE email = ? AND recipe_name = ?", (recipe_text, email, recipe_name))
    else:
        c.execute("INSERT INTO recipes (email, recipe_name, recipe_text) VALUES (?, ?, ?)", (email, recipe_name, recipe_text))
    conn.commit()

# Function to delete a recipe
def delete_recipe(email, recipe_name):
    c.execute("DELETE FROM recipes WHERE email = ? AND recipe_name = ?", (email, recipe_name))
    conn.commit()

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_profile = {"saved_recipes": {}}
    st.session_state.page = "login"
    st.session_state.generated_recipe = ""  # Store generated recipe

# -------- LOGIN / REGISTER PAGE --------
def login_page():
    st.title("🔐 Login or Register")
    option = st.radio("Select an option:", ["Login", "Register"])
    email = st.text_input("📧 Email")
    password = st.text_input("🔑 Password", type="password")

    if option == "Register":
        name = st.text_input("👤 Name")
        if st.button("Register"):
            register_user(email, name, password)
            st.success("✅ Registration successful! Please log in.")

    elif option == "Login":
        if st.button("Login"):
            user = login_user(email, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_profile = {
                    "name": user[1],
                    "saved_recipes": get_user_recipes(email)
                }
                st.session_state.page = "fusion_recipe"
                st.success(f"✅ Welcome {user[1]}!")
                st.rerun()
            else:
                st.error("❌ Invalid email or password.")

# -------- MAIN PAGE: FUSION RECIPE --------
def fusion_recipe_page():
    st.sidebar.header(f"👤 Welcome, {st.session_state.user_profile['name']}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.rerun()

    st.title("🍽️ Fusion Recipe")
    st.header(random.choice([
         "😂Why do programmers prefer dark mode? Because light attracts bugs!",
        "Why did the programmer quit his job? He didn’t get arrays!",
        "🧐Why do Java developers wear glasses? Because they don’t C#!",
        "🖥️How do you comfort a JavaScript bug? You console it.",
        "🎭Why was the function so arrogant? Because it had too many arguments!",
        "🍻What’s a programmer’s favorite place to hang out?The Foo Bar.",
        "🐍Why do Python programmers prefer snakes over birds?Because Pythons have more libraries than a Nest!",
        "💡There are 10 types of people in the world: Those who understand binary and those who don’t.",
        "🐞Debugging: Being the detective in a crime movie where you are also the murderer.",
    ]))

    # Recipe Generation
    recipe_name = st.text_input("Enter Recipe Name")
    
    def generate_recipe(recipe_name):
        prompt = f"Create a 1200-word recipe for {recipe_name}. Include ingredients, instructions, and tips."
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text if response else "Error generating recipe."

    if recipe_name and st.button("Generate Recipe with AI"):
        st.subheader("📖 Generating Recipe... 🍽️")
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.02)
            progress_bar.progress(i + 1)
        
        st.image("https://media4.giphy.com/media/MPhcO7HVYcXgZoLxRo/giphy.gif")
        
        st.session_state.generated_recipe = generate_recipe(recipe_name)
        st.write(st.session_state.generated_recipe)

    if recipe_name and st.button("Save Recipe"):
        recipe_text = st.session_state.get("generated_recipe", "").strip()

        if recipe_text:
            save_or_update_recipe(st.session_state.user_email, recipe_name, recipe_text)
            st.session_state.user_profile["saved_recipes"] = get_user_recipes(st.session_state.user_email)
            st.success(f"✅ '{recipe_name}' has been saved!")
            st.rerun()
        else:
            st.error("⚠️ Please generate a recipe before saving!")

    # Display saved recipes
    st.sidebar.subheader("📌 Your Saved Recipes")
    saved_recipes = st.session_state.user_profile["saved_recipes"]
    #saved_recipes = st.session_state.user_profile.get("saved_recipes", {})
    if saved_recipes:
        selected_recipe = st.sidebar.selectbox("Select the saved recipe:", list(saved_recipes.keys()))
        if selected_recipe:
            st.subheader(f"📖 Edit Recipe: {selected_recipe}")
            recipe_text = st.text_area("Edit your recipe here:", saved_recipes[selected_recipe], height=300)
            if st.button("Update Recipe"):
                save_or_update_recipe(st.session_state.user_email, selected_recipe, recipe_text)
                st.success(f"✅ '{selected_recipe}' has been updated!")
            if st.button("❌ Delete Recipe"):
                delete_recipe(st.session_state.user_email, selected_recipe)
                st.session_state.user_profile["saved_recipes"].pop(selected_recipe, None)
                st.success(f"🗑️ '{selected_recipe}' has been deleted!")
                st.rerun()
    else:
        st.sidebar.write("❌ No saved recipes yet.")

# -------- PAGE NAVIGATION --------
if st.session_state.page == "login":
    login_page()
else:
    fusion_recipe_page()
