
import streamlit as st
import random
import google.generativeai as genai
import time

# Configure Gemini API (Replace with your API Key)
genai.configure(api_key="AIzaSyAgXeDaq-YDqbnJIKWPeUwJ8-j1PGF1W04")

# List of Programmer Jokes
jokes = [
      "😂Why do programmers prefer dark mode? Because light attracts bugs!",
  
      "Why did the programmer quit his job? He didn’t get arrays!",
  
      "🧐Why do Java developers wear glasses? Because they don’t C#!",
      
      "🖥️How do you comfort a JavaScript bug? You console it.",
      
      "🎭Why was the function so arrogant? Because it had too many arguments!",
      
      "🍻What’s a programmer’s favorite place to hang out?The Foo Bar.",
      
      "🐍Why do Python programmers prefer snakes over birds?Because Pythons have more libraries than a Nest!",
      
      "😂Why do programmers prefer dark mode? Because light attracts bugs!",
      
      "💡There are 10 types of people in the world: Those who understand binary and those who don’t.",
    
      "🐞Debugging: Being the detective in a crime movie where you are also the murderer.",
 ]

# Function to Generate Recipe using Gemini API
def generate_recipe(recipe_name, word_count=1200):
    prompt = f"Create a {word_count}-word detailed recipe for {recipe_name}. Include ingredients, step-by-step instructions, and tips."

    model = genai.GenerativeModel("gemini-1.5-flash")  # Use Gemini Pro
    response = model.generate_content(prompt)
    
    return response.text if response else "Error generating recipe."


#Custom CSS for Background Color
custom_css = """
    <style>
        body {
            background-color: #121212; /* Dark Theme */
            color: white;
        }
        .stTextInput, .stButton>button {
            border-radius: 8px;
            font-size: 18px;
            padding: 10px;
        }
    </style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Streamlit UI
st.title("🍽️ Fusion Recipe")
if jokes:
    st.header(random.choice(jokes))  # Show a random joke if available
else:
    st.header("Let's cook up something amazing!")

# User Input for Recipe
recipe_name = st.text_input("🍜Which recipe do you want to make?", placeholder="Enter a dish name...")

if recipe_name:
    st.subheader("📖 Generating Recipe... 🍽️")
    # Animated loading icon (Rotating plate)
    loading_placeholder = st.empty()
    
    # Progress bar
    progress_bar = st.progress(0)

    for i in range(100):
        time.sleep(0.02)
        progress_bar.progress(i + 1)
        if i % 10 == 0:
            loading_placeholder.markdown(f"🍽️ **Loading... {i}%**")
    
    # Clear loading text
    loading_placeholder.empty()
    st.image("https://media4.giphy.com/media/MPhcO7HVYcXgZoLxRo/giphy.gif?cid=6c09b952x4klipa12ik7x22f02qk6e3i11h3k4omyi5lrwjw&ep=v1_internal_gif_by_id&rid=giphy.gif&ct=g")

    
    

    # Success message
    st.success("✅ Recipe Generated Successfully!")
if recipe_name:
    recipe_text = generate_recipe(recipe_name)
    st.write(recipe_text)
