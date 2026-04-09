import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Sudijski Kliker", layout="centered", initial_sidebar_state="collapsed")
st_autorefresh(interval=3000, key="datarefresh") 

# --- 2. FIREBASE (Standardna konekcija) ---
if not firebase_admin._apps:
    fb_secrets = st.secrets["firebase"]
    fixed_key = fb_secrets["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate({
        "type": fb_secrets["type"], "project_id": fb_secrets["project_id"],
        "private_key_id": fb_secrets["private_key_id"], "private_key": fixed_key,
        "client_email": fb_secrets["client_email"], "client_id": fb_secrets["client_id"],
        "auth_uri": fb_secrets["auth_uri"], "token_uri": fb_secrets["token_uri"],
        "auth_provider_x509_cert_url": fb_secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": fb_secrets["client_x509_cert_url"],
    })
    firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["database"]["url"]})

# --- 3. CSS (Sada ciljamo kolone da bi razdvojili veličine) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    
    /* Prikaz rezultata */
    .score-box { text-align: center; margin: 20px 0; }
    .score-val { font-size: 110px; font-weight: 900; color: white; line-height: 1; }
    .score-lbl { font-size: 20px; color: #666; letter-spacing: 3px; }

    /* --- VELIKI ZELENI GUMB (+) --- */
    /* Koristimo specifičan selektor za prvu kolonu */
    [data-testid="column"]:nth-of-type(1) button {
        width: 320px !important;  /* PROMIJENI SAMO OVDJE ZA PLUS */
        height: 320px !important;
        background-color: #2da94f !important;
        border-radius: 50% !important;
        border: none !important;
        margin: 20px auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 10px 30px rgba(45, 169, 79, 0.4) !important;
    }
    [data-testid="column"]:nth-of-type(1) p {
        font-size: 160px !important; /* Veličina plusa */
        color: white !important;
        font-weight: bold !important;
    }

    /* --- MALI NARANDŽASTI GUMB (-) --- */
    /* Koristimo fiksnu poziciju za drugu kolonu (u kojoj je minus) */
    [data-testid="column"]:nth-of-type(2) button {
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        width: 80px !important;   /* PROMIJENI SAMO OVDJE ZA MINUS */
        height: 80px !important;
        background-color: #ff8a50 !important;
        border-radius: 50% !important;
        border: none !important;
        z-index: 9999 !important;
    }
    [data-testid="column"]:nth-of-type(2) p {
        font-size: 40px !important;
        color: white !important;
    }

    /* Čišćenje Streamlit UI-ja */
    [data-testid="stHeader"] { visibility: hidden; }
    button:active { transform: scale(0.92) !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. LOGIKA ---
st.title("⚖️ Sudijski Kliker")

# Mock podaci (zamijeni sa tvojom get_athletes funkcijom)
wod_list = ["WOD 1", "WOD 2", "WOD 3"]
athlete_list = ["1-Takmičar A", "2-Takmičar B"]

selected_wod = st.selectbox("Odaberite WOD:", wod_list)
selected_athlete = st.selectbox("Odaberite takmičara:", athlete_list)

a_id = selected_athlete.split("-")[0]
a_name = selected_athlete.split("-")[1]

# Firebase podaci
db_path = f'competitions/{selected_wod.replace(" ", "_")}/{a_id}'
ref = db.reference(db_path)
data = ref.get()
reps = data.get('reps', 0) if data else 0

# Prikaz rezultata
st.markdown(f'<div class="score-box"><div class="score-val">{reps}</div><div class="score-lbl">PONAVLJANJA</div></div>', unsafe_allow_html=True)

# --- 5. DUGMAD (Stavljamo ih u kolone da bi ih CSS razlikovao) ---
col_plus, col_minus = st.columns([1, 0.1])

with col_plus:
    # Ovo je sada tvoj jedini veliki gumb koji radi
    if st.button("+", key="p_btn"):
        ref.update({'reps': reps + 1, 'name': a_name})
        st.rerun()

with col_minus:
    # Ovo je fiksirani minus u uglu
    if st.button("-", key="m_btn"):
        if reps > 0:
            ref.update({'reps': reps - 1})
            st.rerun()
