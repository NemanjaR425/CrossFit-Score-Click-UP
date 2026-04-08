import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd

st.set_page_config(page_title="HN CrossFit Judge", layout="centered")

# --- 1. FIREBASE SETUP ---
if not firebase_admin._apps:
    try:
        fb_secrets = st.secrets["firebase"]
        fixed_key = fb_secrets["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate({
            "type": fb_secrets["type"],
            "project_id": fb_secrets["project_id"],
            "private_key_id": fb_secrets["private_key_id"],
            "private_key": fixed_key,
            "client_email": fb_secrets["client_email"],
            "client_id": fb_secrets["client_id"],
            "auth_uri": fb_secrets["auth_uri"],
            "token_uri": fb_secrets["token_uri"],
            "auth_provider_x509_cert_url": fb_secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": fb_secrets["client_x509_cert_url"],
        })
        firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["database"]["url"]})
    except Exception as e:
        st.error(f"Firebase Error: {e}")

# --- 2. ATHLETE & WOD CONFIG ---
@st.cache_data(ttl=60)
def get_athletes():
    try:
        sheet_id = "1z1ga9p39C0KJDSOK6ZzU0OUSgKM1UbSh9BiMPMSQ1PY"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Athletes"
        df = pd.read_csv(url).dropna(subset=['Athlete_ID', 'Name'])
        return [f"{int(row['Athlete_ID'])} - {row['Name']}" for _, row in df.iterrows()]
    except:
        return ["1 - Loading..."]

# List of your 6 WODs
wod_list = ["WOD 1", "WOD 2", "WOD 3", "WOD 4", "WOD 5", "WOD 6"]

# --- 3. UI ---
st.title("⏱️ Judge Clicker")

# Two columns for setup
col1, col2 = st.columns(2)
with col1:
    selected_wod = st.selectbox("Select WOD:", wod_list)
with col2:
    athlete_options = get_athletes()
    selected_athlete = st.selectbox("Select Athlete:", athlete_options)

# Parsing
a_id = selected_athlete.split(" - ")[0] if " - " in selected_athlete else "0"
a_name = selected_athlete.split(" - ")[1] if " - " in selected_athlete else "Athlete"

# --- 4. SCORING LOGIC ---
if a_id != "0":
    # Dynamic path based on selected WOD
    db_path = f'competitions/{selected_wod.replace(" ", "_")}/{a_id}'
    ref = db.reference(db_path)
    
    current_data = ref.get()
    reps = current_data.get('reps', 0) if current_data else 0

    st.metric(label=f"{selected_wod}: {a_name}", value=f"{reps} REPS")

    # Styling for buttons
    st.markdown("""<style>
        div.stButton > button:first-child { height: 8em; width: 100%; font-size: 40px !important; background-color: #28a745; color: white; }
        .undo button { height: 3em !important; background-color: #6c757d !important; margin-top: 10px; }
    </style>""", unsafe_allow_html=True)

    if "Loading" not in selected_athlete:
        if st.button("➕ SCORE REP"):
            ref.update({'reps': reps + 1, 'name': a_name})
            st.rerun()

        st.markdown('<div class="undo">', unsafe_allow_html=True)
        if st.button("➖ UNDO ERROR"):
            if reps > 0:
                ref.update({'reps': reps - 1})
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
