import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Sudijski Kliker", layout="centered")

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

# --- 3. AGRESIVNI CSS (Targetiranje Streamlit klasa) ---
st.markdown("""
    <style>
    /* Pozadina i osnovni tekst */
    .stApp { background-color: #0b0e14; }
    
    /* Povećanje glavnog kontejnera dugmeta */
    div[data-testid="stVerticalBlock"] > div:has(div.stButton) {
        gap: 0rem;
    }

    /* Stil za PLUS dugme */
    div.stButton > button[key="plus_btn"] {
        width: 100% !important;
        height: 250px !important; /* Ekstremna visina */
        background-color: #2da94f !important;
        color: white !important;
        font-size: 120px !important; /* Ogroman plus */
        border-radius: 30px !important;
        border: none !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3) !important;
        margin-top: 10px !important;
    }

    /* Stil za MINUS dugme */
    div.stButton > button[key="minus_btn"] {
        width: 100% !important;
        height: 100px !important;
        background-color: #1a1e26 !important;
        color: #ff4b4b !important;
        font-size: 50px !important;
        border-radius: 20px !important;
        border: 1px solid #333 !important;
        margin-top: 20px !important;
    }

    /* Prikaz rezultata */
    .score-display {
        font-size: 130px;
        font-weight: 900;
        color: white;
        text-align: center;
        margin: 0px;
        line-height: 1;
    }
    
    .score-label {
        font-size: 18px;
        color: #666;
        text-align: center;
        margin-bottom: 20px;
        letter-spacing: 3px;
    }

    /* Skrivanje Streamlit elemenata koji smetaju na mobilnom */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 4. INTERFEJS ---
st.title("⚖️ Sudijski Kliker")

# Selektori
selected_wod = st.selectbox("WOD:", ["WOD 1", "WOD 2", "WOD 3", "WOD 4", "WOD 5", "WOD 6"])
db_path = f'competitions/{selected_wod.replace(" ", "_")}'

athletes = ["1-Marija Ristić", "2-Zeljka Cepic", "3-Anja Ristić", "4-Nemanja Ristić", "5-Srdjan Pavicevic"]
target_athlete = st.selectbox("Takmičar:", athletes)

# Firebase logika
athlete_id = target_athlete.split("-")[0]
athlete_name = target_athlete.split("-")[1]
ref = db.reference(f'{db_path}/{athlete_id}')

current_data = ref.get()
reps = current_data.get("reps", 0) if current_data else 0

# Glavni ekran za rezultat
st.markdown(f'<div class="score-display">{reps}</div>', unsafe_allow_html=True)
st.markdown('<div class="score-label">PONAVLJANJA</div>', unsafe_allow_html=True)

# --- DUGMAD ---
# Koristimo key parametar koji smo definisali u CSS-u
st.button("＋", key="plus_btn", on_click=lambda: ref.update({"name": athlete_name, "reps": reps + 1}))

st.button("－", key="minus_btn", on_click=lambda: ref.update({"name": athlete_name, "reps": max(0, reps - 1)}))

# Info
st.divider()
st.caption(f"Unos za: {athlete_name}")
