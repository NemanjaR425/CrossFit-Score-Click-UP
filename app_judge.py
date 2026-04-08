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

# --- 4. SMARTPHONE-OPTIMIZED CSS ---
st.markdown("""
    <style>
    /* Force full height and remove padding */
    .stApp { background-color: #0b0e14; overflow: hidden; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    
    /* Header Area */
    h1 { font-size: 24px !important; margin-bottom: 0px !important; padding-bottom: 10px !important; }
    .stSelectbox { margin-bottom: -15px !important; }

    /* Score Box */
    .score-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 20px;
        gap: 20px;
    }
    .score-box {
        background: #1a1e26;
        border: 2px solid #333;
        border-radius: 15px;
        padding: 10px 25px;
        font-size: 80px !important;
        font-weight: 900;
        color: white;
    }
    .reps-label { font-size: 60px; font-weight: 300; color: white; }

    /* POSITIONING THE BUTTONS */
    /* Target buttons by their text '+' and '-' */
    
    /* Giant Green Center Button */
    div.stButton > button[kind="secondary"]:has(div:contains("+")) {
        position: fixed;
        left: 50%;
        top: 60%;
        transform: translate(-50%, -50%);
        width: 240px !important;
        height: 240px !important;
        background-color: #28a745 !important;
        border-radius: 50% !important;
        border: none !important;
        color: white !important;
        font-size: 120px !important;
        box-shadow: 0 10px 40px rgba(40, 167, 69, 0.4);
        z-index: 1000;
    }

    /* Small Orange Undo Button (Bottom Right) */
    div.stButton > button[kind="secondary"]:has(div:contains("-")) {
        position: fixed;
        right: 15%;
        bottom: 10%;
        width: 80px !important;
        height: 80px !important;
        background-color: #ff8a50 !important;
        border-radius: 50% !important;
        border: none !important;
        color: white !important;
        font-size: 40px !important;
        box-shadow: 0 5px 15px rgba(255, 138, 80, 0.3);
        z-index: 1000;
    }
    
    /* Hide the standard button labels and borders */
    div.stButton > button:active { transform: scale(0.9) translate(-50%, -50%) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. APP UI ---
st.title("Judge Clicker")

col1, col2 = st.columns(2)
with col1:
    selected_wod = st.selectbox("WOD:", wod_list, label_visibility="collapsed")
with col2:
    selected_athlete = st.selectbox("Athlete:", athlete_list, label_visibility="collapsed")

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
        <div class="score-container">
            <div class="score-box">{reps}</div>
            <div class="reps-label">REPS</div>
        </div>
    """, unsafe_allow_html=True)

    # Invisible placeholders for fixed buttons
    if st.button("+"):
        ref.update({'reps': reps + 1, 'name': a_name})
        st.rerun()

    if st.button("-"):
        if reps > 0:
            ref.update({'reps': reps - 1})
            st.rerun()
