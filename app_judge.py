import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & REFRESH ---
st.set_page_config(page_title="Judge Clicker", layout="centered", initial_sidebar_state="collapsed")
st_autorefresh(interval=3000, key="datarefresh") # Keeps rep count live

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

# --- 4. THE DESIGN (Custom Mobile CSS) ---
st.markdown("""
    <style>
    /* 1. Global Reset & Mobile Focus */
    .stApp { background-color: #0b0e14; }
    .block-container { padding: 1rem !important; max-width: 400px !important; margin: auto; }
    
    /* 2. Header & Selectors */
    h1 { font-size: 32px !important; font-weight: 800; text-align: left; margin-bottom: 20px !important; }
    .stSelectbox label { font-size: 18px !important; font-weight: 600 !important; color: #fff !important; margin-bottom: 5px !important; }
    .stSelectbox div[data-baseweb="select"] { background-color: #1a1e26 !important; border: 1px solid #333 !important; border-radius: 10px !important; }

    /* 3. The Rep Score Box (Matches image_e940c8.png) */
    .score-container {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        margin: 30px 0;
        gap: 20px;
    }
    .score-number-box {
        background: #1a1e26;
        border: 3px solid #444;
        border-radius: 20px;
        width: 120px;
        height: 120px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 70px !important;
        font-weight: 900;
        color: white;
    }
    .reps-label { font-size: 75px; font-weight: 400; color: white; }

    /* 4. THE BUTTONS (Aggressive Mobile Layout) */
    
    /* Main Green Rep Up Button (+) */
    div.stButton > button[kind="secondary"]:has(div:contains("+")) {
        width: 230px !important;
        height: 230px !important;
        background-color: #2da94f !important;
        border-radius: 50% !important;
        border: none !important;
        color: white !important;
        font-size: 140px !important;
        margin: 20px auto !important;
        display: block !important;
        box-shadow: 0 10px 30px rgba(45, 169, 79, 0.3) !important;
        transition: transform 0.1s;
    }

    /* Small Orange Undo Button (-) */
    div.stButton > button[kind="secondary"]:has(div:contains("-")) {
        position: fixed !important;
        right: 25px !important;
        bottom: 40px !important;
        width: 85px !important;
        height: 85px !important;
        background-color: #ff8a50 !important;
        border-radius: 50% !important;
        border: none !important;
        color: white !important;
        font-size: 70px !important;
        box-shadow: 0 5px 15px rgba(255, 138, 80, 0.3) !important;
    }

    /* Feedback on Click */
    button:active { transform: scale(0.9) !important; }
    
    /* Remove padding between elements */
    .element-container { margin-bottom: -10px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. APP UI ---
st.title("Judge Clicker")

# Selectors stacked vertically to avoid "wide" feeling
selected_wod = st.selectbox("Select WOD:", wod_list)
selected_athlete = st.selectbox("Select Athlete:", athlete_list)

# Parse ID/Name
a_id = selected_athlete.split("-")[0] if "-" in selected_athlete else "0"
a_name = selected_athlete.split("-")[1] if "-" in selected_athlete else "None"

if a_id != "0":
    db_path = f'competitions/{selected_wod.replace(" ", "_")}/{a_id}'
    ref = db.reference(db_path)
    current_data = ref.get()
    reps = current_data.get('reps', 0) if current_data else 0

    # Score Box
    st.markdown(f"""
        <div class="score-container">
            <div class="score-number-box">{reps}</div>
            <div class="reps-label">REPS</div>
        </div>
    """, unsafe_allow_html=True)

    # Placeholders for the CSS-styled buttons
    # The green button stays in the normal flow below the score
    if st.button("+", key="btn_plus"):
        ref.update({'reps': reps + 1, 'name': a_name})
        st.rerun()

    # The orange button is pinned to the bottom right via CSS
    if st.button("-", key="btn_minus"):
        if reps > 0:
            ref.update({'reps': reps - 1})
            st.rerun()
