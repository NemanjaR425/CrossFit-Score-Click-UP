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

# --- 4. SMARTPHONE FIXED CSS ---
st.markdown("""
    <style>
    /* 1. Global Reset */
    .stApp { background-color: #0b0e14; }
    .block-container { padding: 1rem !important; max-width: 100% !important; }
    
    /* 2. Header & Selectors */
    h1 { font-size: 28px !important; color: white !important; text-align: center; margin-bottom: 10px !important; }
    .stSelectbox label { display: none; } /* Hide labels to save space */
    .stSelectbox { margin-bottom: 10px !important; }

    /* 3. The Score Display (Mockup Style) */
    .score-ui-row {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px 0;
        gap: 15px;
    }
    .score-number-box {
        background: #1a1e26;
        border: 2px solid #333;
        border-radius: 20px;
        padding: 15px 35px;
        font-size: 90px !important;
        font-weight: 900;
        color: white;
        line-height: 1;
    }
    .score-reps-text { font-size: 60px; font-weight: 300; color: white; letter-spacing: 2px; }

    /* 4. THE BUTTONS (Aggressive Round Styling) */
    
    /* Center Green Button (+) */
    button[kind="secondary"]:has(div:contains("+")) {
        position: fixed !important;
        left: 50% !important;
        bottom: 15% !important;
        transform: translateX(-50%) !important;
        width: 70vw !important; /* Scaled to phone width */
        height: 70vw !important; /* Kept square for a perfect circle */
        max-width: 300px !important;
        max-height: 300px !important;
        background-color: #28a745 !important;
        border-radius: 50% !important;
        border: none !important;
        color: white !important;
        font-size: 160px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 15px 45px rgba(40, 167, 69, 0.4) !important;
        z-index: 9999;
    }

    /* Bottom Right Orange Button (-) */
    button[kind="secondary"]:has(div:contains("-")) {
        position: fixed !important;
        right: 8% !important;
        bottom: 8% !important;
        width: 90px !important;
        height: 90px !important;
        background-color: #ff8a50 !important;
        border-radius: 50% !important;
        border: none !important;
        color: white !important;
        font-size: 60px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 8px 20px rgba(255, 138, 80, 0.3) !important;
        z-index: 10000;
    }

    /* Interaction Feedback */
    button:active { transform: translateX(-50%) scale(0.92) !important; opacity: 0.8; }
    button[kind="secondary"]:has(div:contains("-")):active { transform: scale(0.9) !important; }

    /* Hide standard Streamlit button decoration */
    div.stButton > button p { font-size: 0; } /* Hide the literal text inside */
    div.stButton > button div::before { content: attr(data-label); font-size: inherit; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. APP UI ---
st.title("Judge Clicker")

# Compact selectors
col_w, col_a = st.columns(2)
with col_w:
    selected_wod = st.selectbox("W", wod_list)
with col_a:
    selected_athlete = st.selectbox("A", athlete_list)

# Parse ID/Name
a_id = selected_athlete.split("-")[0] if "-" in selected_athlete else "0"
a_name = selected_athlete.split("-")[1] if "-" in selected_athlete else "None"

if a_id != "0":
    db_path = f'competitions/{selected_wod.replace(" ", "_")}/{a_id}'
    ref = db.reference(db_path)
    current_data = ref.get()
    reps = current_data.get('reps', 0) if current_data else 0

    # Score Display
    st.markdown(f"""
        <div class="score-ui-row">
            <div class="score-number-box">{reps}</div>
            <div class="score-reps-text">REPS</div>
        </div>
    """, unsafe_allow_html=True)

    # Placeholders for the CSS-positioned buttons
    if st.button("+", key="btn_plus"):
        ref.update({'reps': reps + 1, 'name': a_name})
        st.rerun()

    if st.button("-", key="btn_minus"):
        if reps > 0:
            ref.update({'reps': reps - 1})
            st.rerun()
