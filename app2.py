import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import pandas as pd


GOOGLE_API_KEY = 'AIzaSyDfVvmvcwmBiQM5qBd3D2G1VjeGnUEzB5Y'#st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
cola, colb, colc = st.columns([1, 2, 1])
with colb:
    st.title("Carcinogenic detection")

col1, col2, col3 = st.columns([1, 2, 1]) 
with col2:
    st.markdown("##### How would you like to provide an image of the product label?")  # Optional title
    camera_selected = st.button("📷Use camera", key="camera_btn")
    upload_selected = st.button("🖼️ Upload Picture", key="upload_btn")

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
    st.markdown(
    """
    <style>
    [data-testid="stCameraInput"] video {
        width: 100% !important;
        height: auto !important;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
    )
    img_file = st.camera_input(
        "Take a picture", label_visibility="collapsed",
        width="stretch"  
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
            "You are an expert at reading product ingredient labels. And you are also an expert at identifying carcinogenic ingredients based on the IARC Monographs. Only according to the IARC Monographs."
            "Extract and list all the ingredients you can find in this image. Dont include introduction or presentation."
            "Return only the list of ingredients and the classification of each one. Carcinogenic 🟥, Probably carcinogenic 🟧, Possibly carcinogenic🟨, or Not classifiable or not carcinogenic 🟩. If the group is deferent of Not classifiable, put maximum 10 words of explanation about each ingredient."
            "Return only it using the format: Ingredient | IARC Classification | Explanation"
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