import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
st.set_page_config(page_title="Judge Clicker", layout="centered", initial_sidebar_state="collapsed")
st_autorefresh(interval=3000, key="datarefresh") 

# --- 2. FIREBASE CONNECTION ---
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

# --- 3. DATA FETCHING ---
@st.cache_data(ttl=60)
def get_athletes():
    try:
        sheet_id = "1z1ga9p39C0KJDSOK6ZzU0OUSgKM1UbSh9BiMPMSQ1PY"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Athletes"
        df = pd.read_csv(url).dropna(subset=['Athlete_ID', 'Name'])
        return [f"{int(row['Athlete_ID'])}-{row['Name']}" for _, row in df.iterrows()]
    except: return ["1-Loading..."]

athlete_list = get_athletes()
wod_list = ["WOD 1", "WOD 2", "WOD 3", "WOD 4", "WOD 5", "WOD 6"]

# --- 4. THE "MAX-FOCUS" DESIGN ---
st.markdown("""
    <style>
    /* Global Container */
    .stApp { background-color: #0b0e14; overflow-x: hidden; }
    .block-container { max-width: 450px !important; padding-top: 1.5rem !important; margin: auto; }
    
    /* Header & Selectors */
    h1 { font-size: 32px !important; font-weight: 800 !important; color: white !important; }
    .stSelectbox label p { font-size: 16px !important; color: #888 !important; }
    
    /* Rep Counter Box */
    .score-ui { display: flex; align-items: center; gap: 15px; margin: 20px 0; }
    .score-box {
        background: #1a1e26;
        border: 2px solid #333;
        border-radius: 18px;
        width: 125px;
        height: 110px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 70px !important;
        font-weight: 900;
        color: white;
    }
    .reps-text { font-size: 70px; font-weight: 300; color: white; }

    /* --- NAVIGATION FOCUS BUTTONS --- */
    
    /* 1. DOMINANT Green Button (+) */
    div[data-testid="stButton"]:nth-of-type(1) button {
        width: 88vw !important; /* Maximized for focus */
        height: 88vw !important;
        max-width: 350px !important;
        max-height: 350px !important;
        background-color: #2da94f;
        border-radius: 50% !important;
        border: none !important;
        margin: 35px auto !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0 15px 45px rgba(45, 169, 79, 0.4) !important;
    }
    div[data-testid="stButton"]:nth-of-type(1) button p {
        font-size: 180px !important;
        font-weight: 100 !important;
        color: white !important;
    }

    /* 2. TINY Orange Button (-) Pinned to Corner */
    div[data-testid="stButton"]:nth-of-type(2) button {
        position: fixed !important;
        bottom: 30px !important;
        right: 25px !important;
        width: 65px !important; /* Shrunk for better navigation */
        height: 65px !important;
        background-color: #ff8a50;
        border-radius: 50% !important;
        border: none !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5) !important;
        z-index: 9999;
    }
    div[data-testid="stButton"]:nth-of-type(2) button p {
        font-size: 50px !important;
        font-weight: 100 !important;
        color: white !important;
    }

    /* Active Haptic Feedback */
    button:active { transform: scale(0.9) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. APP UI ---
st.title("Judge Clicker")

selected_wod = st.selectbox("Select WOD:", wod_list)
selected_athlete = st.selectbox("Select Athlete:", athlete_list)

a_id = selected_athlete.split("-")[0] if "-" in selected_athlete else "0"
a_name = selected_athlete.split("-")[1] if "-" in selected_athlete else "None"

if a_id != "0":
    db_path = f'competitions/{selected_wod.replace(" ", "_")}/{a_id}'
    ref = db.reference(db_path)
    current_data = ref.get()
    reps = current_data.get('reps', 0) if current_data else 0

    # Large Score Counter
    st.markdown(f"""
        <div class="score-ui">
            <div class="score-box">{reps}</div>
            <div class="reps-text">REPS</div>
        </div>
    """, unsafe_allow_html=True)

    # Big Green Plus Button
    if st.button("+", key="p"):
        ref.update({'reps': reps + 1, 'name': a_name})
        st.rerun()

    # Small Orange Minus Button
    if st.button("-", key="m"):
        if reps > 0:
            ref.update({'reps': reps - 1})
            st.rerun()
