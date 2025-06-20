import google.generativeai as genai
from PIL import Image
import requests

genai.configure(api_key="AIzaSyDfVvmvcwmBiQM5qBd3D2G1VjeGnUEzB5Y")

image_path = "/Users/alexandrekoiyama/Desktop/PROJECTS/streamlit_carcinogen/ff.jpeg"
image = Image.open(image_path)

prompt = "Based on this picture, read and give me all ingredients separated by comma."

model = genai.GenerativeModel("gemini-1.5-flash")

response = model.generate_content([prompt, image])

print("Extracted ingredients:")
print(response.text)
