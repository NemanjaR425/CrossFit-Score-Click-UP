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

# --- 3. CSS (Agresivno targetiranje veličine) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    
    /* Centriranje glavnog prikaza */
    .score-ui { text-align: center; margin: 20px 0; }
    .score-val { font-size: 120px; font-weight: 900; color: white; line-height: 1; }
    .score-lbl { font-size: 20px; color: #666; letter-spacing: 5px; margin-top: 10px; }

    /* --- PLUS DUGME (Zeleni krug) --- */
    #plus-box button {
        min-width: 300px !important;  /* OVDJE MIJENJAJ VELIČINU PLUS GUMBA */
        min-height: 300px !important;
        max-width: 300px !important;
        max-height: 300px !important;
        background-color: #2da94f !important;
        border-radius: 50% !important;
        border: none !important;
        margin: 20px auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 10px 30px rgba(45, 169, 79, 0.4) !important;
    }
    #plus-box p { font-size: 140px !important; color: white !important; font-weight: bold !important; }

    /* --- MINUS DUGME (Narandžasti krug) --- */
    #minus-box button {
        position: fixed !important;
        bottom: 40px !important;
        right: 30px !important;
        min-width: 80px !important;   /* OVDJE MIJENJAJ VELIČINU MINUS GUMBA */
        min-height: 80px !important;
        background-color: #ff8a50 !important;
        border-radius: 50% !important;
        border: none !important;
        z-index: 9999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    #minus-box p { font-size: 40px !important; color: white !important; }

    /* Resetuj Streamlit-ove defaultne stilove koji smetaju krugu */
    div.stButton { display: flex; justify-content: center; }
    button:active { transform: scale(0.95) !important; }
    [data-testid="stHeader"] { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# --- 4. LOGIKA ---
st.title("⚖️ Sudijski Kliker")

# Učitavanje atleta (Skraćeno za ovaj primjer)
wod_list = ["WOD 1", "WOD 2", "WOD 3"]
athlete_list = ["1-Marija Ristić", "2-Zeljka Cepic", "3-Anja Ristić"]

col1, col2 = st.columns(2)
with col1:
    selected_wod = st.selectbox("WOD:", wod_list)
with col2:
    selected_athlete = st.selectbox("Takmičar:", athlete_list)

a_id = selected_athlete.split("-")[0]
a_name = selected_athlete.split("-")[1]

# Firebase konekcija
db_path = f'competitions/{selected_wod.replace(" ", "_")}/{a_id}'
ref = db.reference(db_path)
data = ref.get()
reps = data.get('reps', 0) if data else 0

# Prikaz rezultata
st.markdown(f"""
    <div class="score-ui">
        <div class="score-val">{reps}</div>
        <div class="score-lbl">PONAVLJANJA</div>
    </div>
""", unsafe_allow_html=True)

# PLUS GUMB
st.markdown('<div id="plus-box">', unsafe_allow_html=True)
if st.button("+", key="p_btn"):
    ref.update({'reps': reps + 1, 'name': a_name})
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# MINUS GUMB
st.markdown('<div id="minus-box">', unsafe_allow_html=True)
if st.button("-", key="m_btn"):
    if reps > 0:
        ref.update({'reps': reps - 1})
        st.rerun()
# Zatvaramo div nakon dugmeta
st.markdown('</div>', unsafe_allow_html=True)
