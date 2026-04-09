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

# --- 3. CSS (Razdvojeni selektori za svaki gumb) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; overflow-x: hidden; }
    .block-container { max-width: 450px !important; padding-top: 1rem !important; margin: auto; }
    
    .score-ui { display: flex; align-items: center; gap: 15px; margin: 15px 0; justify-content: center; }
    .score-box {
        background: #1a1e26;
        border: 2px solid #333;
        border-radius: 18px;
        width: 120px;
        height: 100px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 65px !important;
        font-weight: 900;
        color: white;
    }
    .reps-text { font-size: 55px; font-weight: 300; color: white; }

    /* STIL ZA PLUS GUMB (p) */
    div.stButton > button[key="p"] {
        width: 300px !important; /* Promijeni samo ovdje za PLUS */
        height: 300px !important;
        background-color: #2da94f !important;
        border-radius: 50% !important;
        border: none !important;
        margin: 20px auto !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0 10px 30px rgba(45, 169, 79, 0.3) !important;
    }
    div.stButton > button[key="p"] p {
        font-size: 150px !important;
        color: white !important;
    }

    /* STIL ZA MINUS GUMB (m) */
    div.stButton > button[key="m"] {
        position: fixed !important;
        bottom: 30px !important;
        right: 25px !important;
        width: 80px !important; /* Promijeni samo ovdje za MINUS */
        height: 80px !important;
        background-color: #ff8a50 !important;
        border-radius: 50% !important;
        border: none !important;
        z-index: 9999 !important;
    }
    div.stButton > button[key="m"] p {
        font-size: 50px !important;
        color: white !important;
    }

    button:active { transform: scale(0.95) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIKA ---
st.title("Sudijski Kliker")

# (Ovdje ide tvoj standardni kod za dobavljanje atleta i odabir)
# ... [Pretpostavljam da koristiš get_athletes() funkciju]

# Primjer liste za testiranje ako nemaš učitavanje
wod_list = ["WOD 1", "WOD 2", "WOD 3"]
athlete_list = ["1-Takmičar A", "2-Takmičar B"]

selected_wod = st.selectbox("Odaberite WOD:", wod_list)
selected_athlete = st.selectbox("Odaberite takmičara:", athlete_list)

a_id = selected_athlete.split("-")[0]
a_name = selected_athlete.split("-")[1]

db_path = f'competitions/{selected_wod.replace(" ", "_")}/{a_id}'
ref = db.reference(db_path)
reps = ref.get().get('reps', 0) if ref.get() else 0

st.markdown(f'<div class="score-ui"><div class="score-box">{reps}</div><div class="reps-text">PON.</div></div>', unsafe_allow_html=True)

# SADA DUGMAD KORISTE KEY ZA STILIZACIJU
if st.button("+", key="p"):
    ref.update({'reps': reps + 1, 'name': a_name})
    st.rerun()

if st.button("-", key="m"):
    if reps > 0:
        ref.update({'reps': reps - 1})
        st.rerun()
