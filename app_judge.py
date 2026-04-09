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

# --- 3. DOBAVLJANJE PODATAKA ---
@st.cache_data(ttl=60)
def get_athletes():
    try:
        sheet_id = "1z1ga9p39C0KJDSOK6ZzU0OUSgKM1UbSh9BiMPMSQ1PY"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Athletes"
        df = pd.read_csv(url).dropna(subset=['Athlete_ID', 'Name'])
        return [f"{int(row['Athlete_ID'])}-{row['Name']}" for _, row in df.iterrows()]
    except: return ["1-Učitavanje..."]

athlete_list = get_athletes()
wod_list = ["WOD 1", "WOD 2", "WOD 3", "WOD 4", "WOD 5", "WOD 6"]

# --- 4. DIZAJN (CSS za kružnu dugmad) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; overflow-x: hidden; }
    .block-container { max-width: 450px !important; padding-top: 1rem !important; margin: auto; }
    
    /* Prikaz rezultata */
    .score-ui { display: flex; align-items: center; gap: 15px; margin: 15px 0; }
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
    .reps-text { font-size: 55px; font-weight: 300; color: white; letter-spacing: 2px; }

    /* --- DUGMAD --- */
    
    /* 1. ZELENI PLUS (+) */
    div[data-testid="stButton"]:nth-of-type(1) > button {
        width: 75vw !important;
        height: 75vw !important;
        max-width: 320px !important;
        max-height: 320px !important;
        background-color: #2da94f !important;
        border-radius: 50% !important;
        border: none !important;
        margin: 20px auto !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0 10px 30px rgba(45, 169, 79, 0.3) !important;
    }
    div[data-testid="stButton"]:nth-of-type(1) p {
        font-size: 150px !important;
        color: white !important;
        margin: 0 !important;
        line-height: 1 !important;
    }

    /* 2. NARANDŽASTI MINUS (-) - Korekcija */
    div[data-testid="stButton"]:nth-of-type(2) > button {
        position: fixed !important;
        bottom: 30px !important;
        right: 25px !important;
        width: 70px !important;
        height: 70px !important;
        background-color: #ff8a50 !important;
        color: white !important;
        border-radius: 50% !important;
        border: none !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        z-index: 9999 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
    }
    div[data-testid="stButton"]:nth-of-type(2) p {
        font-size: 45px !important;
        color: white !important;
        margin: 0 !important;
        line-height: 1 !important;
    }

    button:active { transform: scale(0.92) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LOGIKA APLIKACIJE ---
st.title("Sudijski Kliker")

selected_wod = st.selectbox("Odaberite WOD:", wod_list)
selected_athlete = st.selectbox("Odaberite takmičara:", athlete_list)

a_id = selected_athlete.split("-")[0] if "-" in selected_athlete else "0"
a_name = selected_athlete.split("-")[1] if "-" in selected_athlete else "Nema"

if a_id != "0":
    db_path = f'competitions/{selected_wod.replace(" ", "_")}/{a_id}'
    ref = db.reference(db_path)
    current_data = ref.get()
    reps = current_data.get('reps', 0) if current_data else 0

    st.markdown(f"""
        <div class="score-ui">
            <div class="score-box">{reps}</div>
            <div class="reps-text">PON.</div>
        </div>
    """, unsafe_allow_html=True)

    # Glavni kliker (Plus)
    if st.button("+", key="p"):
        ref.update({'reps': reps + 1, 'name': a_name})
        st.rerun()

    # Sigurnosna korekcija (Minus)
    if st.button("-", key="m"):
        if reps > 0:
            ref.update({'reps': reps - 1})
            st.rerun()
