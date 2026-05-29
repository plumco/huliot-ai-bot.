import base64
import os
import requests
import streamlit as st

st.set_page_config(page_title="Huliot Pipe Inspector AI", layout="centered")
st.title("Huliot Pipe Inspector AI")
st.write("Upload a photo of your plumbing issue, and our AI will identify the required Huliot parts.")

api_key = None
for secret_name in ["gemini_api_key", "GEMINI_API_KEY", "api_key", "API_KEY"]:
    api_key = st.secrets.get(secret_name)
    if api_key:
        break

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    api_key = st.text_input("Google Gemini API key", type="password", placeholder="Paste your Gemini API key here")
else:
    st.success("Using Gemini API key from Streamlit secrets or environment.")
uploaded_file = st.file_uploader("Upload a plumbing photo", type=["png", "jpg", "jpeg", "webp"])

if uploaded_file:
    image_bytes = uploaded_file.read()
    st.image(image_bytes, caption="Uploaded image", use_column_width=True)

    if not api_key:
        st.warning("Enter your Gemini API key to analyze the image.")
    else:
        if st.button("Analyze with AI"):
            with st.spinner("Analyzing the image with Gemini..."):
                base64_image = base64.b64encode(image_bytes).decode("utf-8")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                prompt_text = (
                    "You are a Huliot Technical Expert. Look closely at this plumbing photo. "
                    "Identify the pipes or joints shown. If there is a problem or an upgrade needed, explain it briefly. "
                    "Recommend which specific Huliot product (like Ultra Silent, PP-R, HT, etc.) should be used here. "
                    "Keep it professional and short."
                )
                request_body = {
                    "contents": [
                        {
                            "parts": [
                                {"text": prompt_text},
                                {
                                    "inlineData": {
                                        "mimeType": uploaded_file.type,
                                        "data": base64_image,
                                    }
                                }
                            ]
                        }
                    ]
                }

                response = requests.post(url, json=request_body, timeout=60)
                if response.status_code != 200:
                    st.error(f"Gemini request failed: {response.status_code} - {response.text}")
                else:
                    data = response.json()
                    answer = None
                    candidates = data.get("candidates")
                    if candidates:
                        candidate = candidates[0]
                        parts = candidate.get("content", {}).get("parts", [])
                        if parts and parts[0].get("text"):
                            answer = parts[0]["text"]

                    if answer:
                        st.markdown("**Huliot Expert Diagnosis:**")
                        st.write(answer)
                    else:
                        st.error("No answer was returned by Gemini. Check your API key and model response.")

else:
    st.info("Upload an image to start the analysis.")