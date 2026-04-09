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

# --- 3. STILIZACIJA (Univerzalni CSS za veliku dugmad) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    
    /* Globalno pravilo za svu dugmad u aplikaciji */
    div.stButton > button {
        width: 100% !important;
        background-color: #2da94f !important;
        color: white !important;
        border-radius: 15px !important;
        border: none !important;
        display: block !important;
    }

    /* Specifično za PLUS dugme (veće) */
    div.stButton > button[p-typed-key="plus_btn"] {
        height: 150px !important;
        font-size: 80px !important;
        margin-bottom: 20px !important;
    }

    /* Specifično za MINUS dugme (manje) */
    div.stButton > button[p-typed-key="minus_btn"] {
        height: 80px !important;
        font-size: 40px !important;
        opacity: 0.7 !important;
    }

    .score-display {
        font-size: 100px;
        font-weight: 900;
        color: white;
        text-align: center;
        margin: 10px 0;
        line-height: 1;
    }
    
    .score-label {
        font-size: 24px;
        color: #666;
        text-align: center;
        margin-bottom: 30px;
        text-transform: uppercase;
    }
    
    label { color: #aaa !important; }
    h1 { color: white !important; text-align: center; margin-bottom: 30px !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. LOGIKA I INTERFEJS ---
st.title("⚖️ Sudijski Kliker")

selected_wod = st.selectbox("Odaberite WOD:", ["WOD 1", "WOD 2", "WOD 3", "WOD 4", "WOD 5", "WOD 6"])
db_path = f'competitions/{selected_wod.replace(" ", "_")}'

athletes = ["1-Marija Ristić", "2-Zeljka Cepic", "3-Anja Ristić", "4-Nemanja Ristić", "5-Srdjan Pavicevic"]
target_athlete = st.selectbox("Odaberite takmičara:", athletes)

athlete_id = target_athlete.split("-")[0]
athlete_name = target_athlete.split("-")[1]
ref = db.reference(f'{db_path}/{athlete_id}')

current_data = ref.get()
reps = current_data.get("reps", 0) if current_data else 0

# Prikaz rezultata
st.markdown(f'<div class="score-display">{reps}</div>', unsafe_allow_html=True)
st.markdown('<div class="score-label">Ponavljanja</div>', unsafe_allow_html=True)

# Dugmad sa fiksnim ključevima za CSS
if st.button("＋", key="plus_btn"):
    reps += 1
    ref.update({"name": athlete_name, "reps": reps})
    st.rerun()

if st.button("－", key="minus_btn"):
    if reps > 0:
        reps -= 1
        ref.update({"name": athlete_name, "reps": reps})
        st.rerun()

st.divider()
st.caption(f"Bilježenje za: {athlete_name}")
