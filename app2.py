import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import pandas as pd
from fuzzywuzzy import fuzz, process

df = pd.read_csv('List of Classifications – IARC Monographs on the Identification of Carcinogenic Hazards to Humans.csv')

def find_group_for_ingredient(ingredient, threshold=80):
    agents = df["Agent"].dropna().unique()
    match, score = process.extractOne(ingredient, agents, scorer=fuzz.token_set_ratio)
    if score >= threshold:
        group = df[df["Agent"] == match]["Group"].values[0]
        return match, group, score
    else:
        return None, None, score

def check_ingredients(ingredients, threshold=80):
    results = []
    for ing in ingredients:
        agent, group, score = find_group_for_ingredient(ing, threshold)
        if agent:
            results.append({"ingredient": ing, "matched_agent": agent, "group": group})
        else:
            results.append({"ingredient": ing, "matched_agent": None, "group": None})
    return results

def get_iarc_flag(group):
    group = str(group).strip().upper()
    if group == "1":
        return "🟥 Group 1 (Carcinogenic to humans)"
    elif group == "2A":
        return "🟧 Group 2A (Probably carcinogenic to humans)"
    elif group == "2B":
        return "🟨 Group 2B (Possibly carcinogenic to humans)"
    else:
        return "🟩 Group 3 or Other (Not classifiable or not carcinogenic)"



GOOGLE_API_KEY = 'AIzaSyDfVvmvcwmBiQM5qBd3D2G1VjeGnUEzB5Y'#st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

st.title("Detection of carcinogenic ingredients")
st.subheader("First, provide an image of the Ingredients of the product")
st.subheader("How would you like to provide an image?")

col1, col2 = st.columns(2)
with col1:
    camera_selected = st.button("📷 Camera", key="camera_btn")
with col2:
    upload_selected = st.button("🖼️ Upload", key="upload_btn")

if "input_method" not in st.session_state:
    st.session_state.input_method = None

if camera_selected:
    st.session_state.input_method = "Camera"
if upload_selected:
    st.session_state.input_method = "Upload"

input_method = st.session_state.input_method

img_file = None
if input_method == "Camera":
    st.info("Use your device camera to take a picture of the ingredient label.")
    img_file = st.camera_input(
        "Take a picture", label_visibility="collapsed",
    )
elif input_method == "Upload":
    st.info("Upload an image of the ingredient label (JPG or PNG).")
    img_file = st.file_uploader(
        "Upload an image", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
    )

if img_file:
    image = Image.open(img_file)
    st.image(image, caption="Your Image", use_container_width=True)

    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()

    st.header("Detected Ingredients")
    with st.spinner("Analyzing image with Gemini..."):
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            "You are an expert at reading product ingredient labels. And you are also an expert at identifying carcinogenic ingredients based on the IARC Monographs."
            "Extract and list all the ingredients you can find in this image."
            "Return only the list of ingredients and the classification of each one. Carcinogenic 🟥, Probably carcinogenic 🟧, Possibly carcinogenic🟨, or Not classifiable or not carcinogenic 🟩"
        )
        response = model.generate_content([
            prompt,
            {
                "mime_type": "image/png",
                "data": img_bytes
            }
        ])
        st.subheader("Ingredients Detected:")
        for i in response.text.splitlines():
            if i.strip():
                st.markdown(f"- {i.strip()}")
