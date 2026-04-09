import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Sudijski Kliker", layout="centered", initial_sidebar_state="collapsed")
st_autorefresh(interval=3000, key="datarefresh") 

# --- 2. FIREBASE KONEKCIJA ---
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

# --- 3. MOĆNI CSS (Ovdje mijenjaš dimenzije) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0b0e14; }}
    
    /* Prikaz rezultata */
    .score-container {{ text-align: center; margin-bottom: 20px; }}
    .score-val {{ font-size: 100px; font-weight: 900; color: white; line-height: 1; }}
    .score-lbl {{ font-size: 18px; color: #888; letter-spacing: 4px; text-transform: uppercase; }}

    /* --- STIL ZA VELIKI PLUS GUMB --- */
    /* Targetiramo kontejner, pa div, pa button sa !important na SVAKOM nivou */
    div.plus-wrap div[data-testid="stButton"] button {{
        width: 300px !important;   /* PROMIJENI SAMO OVDJE ZA PLUS */
        height: 300px !important;
        background-color: #2da94f !important;
        border-radius: 50% !important;
        border: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto !important;
        box-shadow: 0 10px 40px rgba(45, 169, 79, 0.4) !important;
    }}
    div.plus-wrap p {{ font-size: 140px !important; color: white !important; font-weight: bold !important; }}

    /* --- STIL ZA MANJI MINUS GUMB (Korekcija) --- */
    div.minus-wrap div[data-testid="stButton"] button {{
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        width: 70px !important;    /* PROMIJENI SAMO OVDJE ZA MINUS */
        height: 70px !important;
        background-color: #ff8a50 !important;
        border-radius: 50% !important;
        border: none !important;
        z-index: 9999 !important;
    }}
    div.minus-wrap p {{ font-size: 35px !important; color: white !important; }}

    /* Uklanjanje viška prostora koji Streamlit dodaje */
    [data-testid="stVerticalBlock"] {{ gap: 0rem !important; }}
    button:active {{ transform: scale(0.95) !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. LOGIKA ---
st.title("⚖️ Sudijski Kliker")

# (Ovdje ide tvoj dio koda za get_athletes() i ostalo)
wod_list = ["WOD 1", "WOD 2", "WOD 3"]
athlete_list = ["1-Marija Ristić", "2-Zeljka Cepic", "3-Nemanja Ristić"]

selected_wod = st.selectbox("Odaberite WOD:", wod_list)
selected_athlete = st.selectbox("Odaberite takmičara:", athlete_list)

a_id = selected_athlete.split("-")[0]
a_name = selected_athlete.split("-")[1]

# Dohvatanje podataka
db_path = f'competitions/{selected_wod.replace(" ", "_")}/{a_id}'
ref = db.reference(db_path)
data = ref.get()
reps = data.get('reps', 0) if data else 0

# Prikaz broja ponavljanja (Prevedeno)
st.markdown(f"""
    <div class="score-container">
        <div class="score-val">{reps}</div>
        <div class="score-lbl">Ponavljanja</div>
    </div>
""", unsafe_allow_html=True)

# --- DUGMAD SA POSEBNIM WRAPPERIMA ---

# PLUS GUMB
st.markdown('<div class="plus-wrap">', unsafe_allow_html=True)
if st.button("+", key="btn_plus"):
    ref.update({'reps': reps + 1, 'name': a_name})
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# MINUS GUMB
st.markdown('<div class="minus-wrap">', unsafe_allow_html=True)
if st.button("-", key="btn_minus"):
    if reps > 0:
        ref.update({'reps': reps - 1})
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
