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

# --- 3. STILIZACIJA (Dizajnirano za telefon) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    
    /* Velika dugmad za lakše kliktanje */
    div.stButton > button {
        width: 100%;
        height: 120px;
        font-size: 60px !important;
        font-weight: bold;
        border-radius: 20px;
        margin: 10px 0;
    }
    
    /* Boja za plus dugme */
    div.stButton > button:first-child {
        background-color: #2da94f !important;
        color: white !important;
    }
    
    /* Boja za minus dugme */
    .minus-btn > div > button {
        background-color: #2da94f !important; 
        opacity: 0.8;
        height: 80px !important;
        font-size: 40px !important;
    }

    .score-display {
        font-size: 80px;
        font-weight: 900;
        color: white;
        text-align: center;
        margin: 20px 0;
    }
    
    label { color: #aaa !important; font-size: 16px !important; }
    h1 { color: white !important; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 4. LOGIKA I INTERFEJS ---
st.title("⚖️ Sudijski Kliker")

# Odabir WOD-a i Takmičara
selected_wod = st.selectbox("Odaberite WOD:", ["WOD 1", "WOD 2", "WOD 3", "WOD 4", "WOD 5", "WOD 6"])
db_path = f'competitions/{selected_wod.replace(" ", "_")}'

# Ovdje unesite listu takmičara (možete je povući i iz baze)
athletes = ["1-Marija Ristić", "2-Zeljka Cepic", "3-Anja Ristić", "4-Nemanja Ristić", "5-Srdjan Pavicevic"]
target_athlete = st.selectbox("Odaberite takmičara:", athletes)

# Referenca u bazi za konkretnog takmičara
athlete_id = target_athlete.split("-")[0]
athlete_name = target_athlete.split("-")[1]
ref = db.reference(f'{db_path}/{athlete_id}')

# Dobavljanje trenutnog rezultata
current_data = ref.get()
reps = current_data.get("reps", 0) if current_data else 0

# Prikaz trenutnog broja ponavljanja
st.markdown(f'<div class="score-display">{reps} <span style="font-size: 30px; color: #666;">PON.</span></div>', unsafe_allow_html=True)

# Dugmad za unos
col1 = st.columns(1)[0]
with col1:
    if st.button("＋"):
        reps += 1
        ref.update({"name": athlete_name, "reps": reps})
        st.rerun()

st.markdown('<div class="minus-btn">', unsafe_allow_html=True)
if st.button("－"):
    if reps > 0:
        reps -= 1
        ref.update({"name": athlete_name, "reps": reps})
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Statusna poruka
st.divider()
st.caption(f"Bilježenje rezultata za: {athlete_name}")
