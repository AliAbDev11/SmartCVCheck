import streamlit as st
import PyPDF2
import os
import io
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Streamlit page
st.set_page_config(page_title="Smart CV Check", page_icon="🤖", layout="centered")

# Hide Streamlit default header/footer
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 style='color:#4CAF50; text-align:center;'>🤖 Smart CV Check</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Upload your CV and receive expert feedback powered by AI.</p>", unsafe_allow_html=True)

# File uploader and job role input
with st.container():
    col1, col2 = st.columns([2, 3])
    with col1:
        uploaded_file = st.file_uploader("📄 Upload your CV (PDF or TXT)", type=["pdf", "txt"])
    with col2:
        job_role = st.text_input("💼 Target Job Role")
        language = st.selectbox("🌐 Choose the language for feedback:", ["English", "Arabic", "French"])
    # market = st.selectbox(
    #     "🌍 Choose Job Market",
    #     {
    #         "United States": "us",
    #         "United Kingdom": "gb",
    #         "Canada": "ca",
    #         "Australia": "au",
    #         "Germany": "de",
    #         "France": "fr",
    #         "Netherlands": "nl",
    #         "India": "in"
    #     }
    # )
    

# Button
analyze_button = st.button("🔍 Analyze My CV", use_container_width=True)

# OpenAI API
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
# ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
# ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
# def fetch_job_listings(query, market="us", location="remote", results=5):
#     url = f"https://api.adzuna.com/v1/api/jobs/{market}/search/1"
#     params = {
#         "app_id": ADZUNA_APP_ID,
#         "app_key": ADZUNA_APP_KEY,
#         "results_per_page": results,
#         "what": query,
#         "where": location,
#         "content-type": "application/json"
#     }
#     response = requests.get(url, params=params)
#     if response.status_code == 200:
#         return response.json().get("results", [])
#     else:
#         return []

# Helper functions
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

def extract_text_from_file(file):
    if file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(file.read()))
    return file.read().decode("utf-8")

# Analysis logic
if analyze_button:
    if not uploaded_file:
        st.warning("Please upload a file.")
    else:
        with st.spinner("Analyzing your CV..."):
            try:
                text = extract_text_from_file(uploaded_file)
                if not text.strip():
                    st.error("The uploaded file is empty.")
                    st.stop()

                prompt = f"""
                    Please analyze this resume and provide constructive feedback **in {language}**.

                    Focus on:
                    1. Content clarity and impact
                    2. Skills presentation
                    3. Experience descriptions
                    4. Specific improvements for {job_role if job_role else 'general roles'}

                    Resume content:
                    {text}

                    Respond only in {language} using a clear, structured format with specific recommendations.
                    """

                response = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": "You are an expert resume reviewer. Respond in {language}."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )

                st.markdown("### 📝 Analysis Results")
                st.markdown(f"""
                    <div style="background-color:#111827; padding:20px; border-left: 5px solid #4CAF50; border-radius: 8px;">
                        {response.choices[0].message.content}
                    </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {str(e)}")

# Footer
st.markdown("""
    <hr>
    <div style='text-align: center; color: #888; font-size: 0.8em'>
        Smart CV Check © 2025 | Built by Ali AB
    </div>
""", unsafe_allow_html=True)