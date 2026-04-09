import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Sudijski Kliker", layout="centered")
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

# --- 3. CSS ZA ČISTI HTML IZGLED ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    [data-testid="stHeader"] { display: none; }
    
    .score-ui { text-align: center; margin: 40px 0; }
    .score-val { font-size: 140px; font-weight: 900; color: white; line-height: 1; }
    .score-lbl { font-size: 24px; color: #888; letter-spacing: 5px; margin-top: 10px; }

    /* STIL ZA NAŠA RUČNO RAĐENA DUGMAD */
    .custom-btn-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 40px;
        margin-top: 30px;
    }

    /* VELIKI ZELENI PLUS */
    .btn-plus {
        width: 350px !important;   /* OVDJE PROMIJENI ŠIRINU */
        height: 350px !important;  /* OVDJE PROMIJENI VISINU */
        background-color: #2da94f;
        border-radius: 50%;
        border: none;
        color: white;
        font-size: 180px;
        font-weight: bold;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 15px 45px rgba(45, 169, 79, 0.4);
        transition: transform 0.1s;
    }

    /* NARANDŽASTI MINUS */
    .btn-minus {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 90px !important;   /* OVDJE PROMIJENI ŠIRINU MINUSA */
        height: 90px !important;
        background-color: #ff8a50;
        border-radius: 50%;
        border: none;
        color: white;
        font-size: 50px;
        cursor: pointer;
        z-index: 1000;
    }

    .btn-plus:active, .btn-minus:active { transform: scale(0.92); }
    </style>
""", unsafe_allow_html=True)

# --- 4. LOGIKA I ODABIR ---
st.title("⚖️ Sudijski Kliker")

# Mock podaci (zamijeni sa svojim get_athletes)
wod_list = ["WOD 1", "WOD 2"]
athlete_list = ["1-Marija Ristić", "2-Zeljka Cepic"]

selected_wod = st.selectbox("WOD:", wod_list)
selected_athlete = st.selectbox("Takmičar:", athlete_list)

a_id = selected_athlete.split("-")[0]
a_name = selected_athlete.split("-")[1]

# Firebase podaci
db_path = f'competitions/{selected_wod.replace(" ", "_")}/{a_id}'
ref = db.reference(db_path)
reps = ref.get().get('reps', 0) if ref.get() else 0

# Prikaz rezultata
st.markdown(f"""
    <div class="score-ui">
        <div class="score-val">{reps}</div>
        <div class="score-lbl">PONAVLJANJA</div>
    </div>
""", unsafe_allow_html=True)

# --- 5. RUČNO RAĐENA DUGMAD (HTML + Streamlit Hack) ---

# Plus Dugme
if st.markdown(f'<div class="custom-btn-container"><button class="btn-plus" onclick="window.location.reload()">+</button></div>', unsafe_allow_html=True):
    # Budući da HTML button ne okida direktno Python, koristimo mali trik sa nevidljivim st.button-om
    # ali jednostavnije je samo staviti dugme koje Streamlit vidi kao interakciju
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("POTVRDI +1", key="real_plus", use_container_width=True):
            ref.update({'reps': reps + 1, 'name': a_name})
            st.rerun()

# Minus Dugme (Fiksirano u uglu)
st.markdown(f'<button class="btn-minus">-</button>', unsafe_allow_html=True)
if st.button("Korekcija -1", key="real_minus"):
    if reps > 0:
        ref.update({'reps': reps - 1})
        st.rerun()
