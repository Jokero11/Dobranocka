# =============================
# IMPORTY
# =============================

import streamlit as st
from PIL import Image
from datetime import datetime
import os
from openai import OpenAI
import base64


# =============================
# FUNKCJA: TŁO + STYL
# =============================

def set_magic_bg_for_story_panel(image_file):
    with open(image_file, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{b64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        .block-container {{
            background: rgba(0,0,0,0.35);
            border-radius: 16px;
            padding: 2rem;
        }}

        h1, h2, h3, p, label {{
            color: white !important;
        }}

        section[data-testid="stFileUploader"] {{
            background: white;
            border-radius: 16px;
            padding: 1rem;
            box-shadow: 0 6px 16px rgba(0,0,0,0.35);
        }}

        section[data-testid="stFileUploader"] * {{
            color: black !important;
        }}

        input, textarea {{
            background-color: #ffffff !important;
            color: #000000 !important;
            border-radius: 12px !important;
            border: 1px solid #cccccc !important;
        }}

        input::placeholder,
        textarea::placeholder {{
            color: #666666 !important;
        }}

        .stButton {{
            background: white;
            border-radius: 16px;
            padding: 1rem;
            box-shadow: 0 6px 16px rgba(0,0,0,0.35);
            margin-top: 1rem;
        }}

        .stButton > button {{
            width: 100% !important;
            background-color: #ffffff !important;
            color: #000000 !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            border-radius: 16px !important;
            padding: 1rem 1.2rem !important;
            border: 1px solid #cccccc !important;
            cursor: pointer;
        }}

        .stButton > button:hover {{
            background-color: #f0f0f0 !important;
        }}

        .stButton > button,
        .stButton > button span {{
            color: #000000 !important;
            opacity: 1 !important;
            visibility: visible !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# =============================
# KONFIGURACJA STRONY
# =============================

st.set_page_config(
    page_title="Dobranocka",
    page_icon="icons8-moon-96.png",
    layout="centered"
)

set_magic_bg_for_story_panel("tło1.jpg")


# =============================
# NAGŁÓWKI
# =============================

st.title("🌙 Dobranocka")
st.write("Przygoda, która dzieje się naprawdę.")


# =============================
# FOLDER NA RYSUNKI
# =============================

IMAGE_DIR = "rysunki"
os.makedirs(IMAGE_DIR, exist_ok=True)


# =============================
# OPENAI — NOWA AUTORYZACJA (PROJECT KEYS)
# =============================

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
    project=st.secrets["OPENAI_PROJECT_ID"]
)


# =============================
# FUNKCJA ANALIZY RYSUNKU
# =============================

def analyze_child_drawing(image_path):
    with open(image_path, "rb") as img:
        image_bytes = img.read()

    response = client.chat.completions.create(
        model="gpt-4o",   # model z obsługą obrazów
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Opisz świat z rysunku."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64.b64encode(image_bytes).decode()}"
                    }
                }
            ]
        }],
        max_tokens=400
    )

    return response.choices[0].message["content"]


# =============================
# INPUTY
# =============================

uploaded_file = st.file_uploader("Prześlij rysunek", type=["jpg","png","jpeg"])
imiona_dzieci = st.text_input("Imię lub imiona dzieci")
opis_oczami_dziecka = st.text_area("Co jest na rysunku oczami dziecka?")
moment_dnia = st.text_area("Co dziś było szczególnie miłe lub ważne?")


# =============================
# LOGIKA
# =============================

if uploaded_file and imiona_dzieci and opis_oczami_dziecka and moment_dnia:

    image = Image.open(uploaded_file)
    st.image(image, use_container_width=True)

    if "analiza" not in st.session_state:
        path = os.path.join(IMAGE_DIR, "rysunek.png")
        image.save(path)
        st.session_state.analiza = analyze_child_drawing(path)

    generate = st.button("🌙 Wygeneruj bajkę")

    if generate:
        st.markdown("### 🌙 Rozpoczyna się przygoda...")

        prompt = f""" 
        Napisz przygodową bajkę na dobranoc dla dziecka w wieku 5–7 lat. 
        ZASADY: 
        - Bajka NIE JEST o rysowaniu ani obrazku. 
        - Historia dzieje się w świecie z opisu dziecka. 
        - Opis dziecka ma ABSOLUTNY PRIORYTET. 
        - Analiza AI służy tylko do uzupełniania szczegółów. 
        --- 
        Imię / imiona dzieci: {imiona_dzieci} 
        ŚWIAT (oczami dziecka – priorytet): {opis_oczami_dziecka} 
        Dodatkowe szczegóły świata (pomocniczo): {st.session_state.analiza} 
        Wydarzenie z dnia: {moment_dnia} 
        --- 
        Wytyczne fabularne: 
        - realna przygoda 
        - decyzje i działanie 
        - wyzwanie lub zagadka 
        - świat reaguje na bohaterów 
        Styl: 
        - prosty 
        - dynamiczny 
        - bez przesłodzenia 
        Zakończenie: 
        - spokojne 
        - domknięte 
        - bez morału wprost 
        Długość: 800–1000 słów 
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        st.subheader("📖 Bajka na dobranoc")
        st.write(response.choices[0].message["content"])
