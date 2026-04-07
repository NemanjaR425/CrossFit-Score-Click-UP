import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="Judge Clicker - Herceg Novi", layout="centered")

# --- 2. FIREBASE CONNECTION SETUP ---
if not firebase_admin._apps:
    try:
        fb_secrets = st.secrets["firebase"]
        fixed_key = fb_secrets["private_key"].replace("\\n", "\n")
        
        cred_dict = {
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
        }
        
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["database"]["url"]})
    except Exception as e:
        st.error(f"Firebase Error: {e}")

# Only show the scoring button if a real athlete is selected
if "Loading" not in selected_athlete and "Check" not in selected_athlete:
    if st.button("➕ SCORE REP"):
        ref.update({'reps': reps + 1, 'name': a_name})
        st.rerun()
else:
    st.warning("Please wait for athletes to load before scoring.")

# --- 3. UI STYLING ---
st.markdown("""
    <style>
    div.stButton > button:first-child { height: 10em; width: 100%; font-size: 45px !important; background-color: #28a745; color: white; border-radius: 20px; font-weight: bold; }
    .stSelectbox label { font-size: 22px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ROBUST GOOGLE SHEETS CONNECTION ---
@st.cache_data(ttl=60)
def get_athlete_data():
    try:
        # We convert the spreadsheet URL to a direct CSV export link. 
        # This is the most reliable way to avoid HTTP 400 errors.
        sheet_id = "1z1ga9p39C0KJDSOK6ZzU0OUSgKM1UbSh9BiMPMSQ1PY"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Athletes"
        df = pd.read_csv(url)
        
        # Create the list for the dropdown
        return [f"{int(row['Athlete_ID'])} - {row['Name']}" for _, row in df.iterrows()]
    except Exception as e:
        return [f"Error: {e}"]

athlete_list = get_athlete_data()

# --- 5. APP INTERFACE ---
st.title("⏱️ Live Score Clicker")

selected_athlete = st.selectbox("Select Athlete on Lane:", athlete_list)

# Safely split the ID and Name
if " - " in selected_athlete:
    a_id = selected_athlete.split(" - ")[0]
    a_name = selected_athlete.split(" - ")[1]
else:
    a_id = "1"
    a_name = "Athlete"

# --- 6. LIVE DATABASE LOGIC ---
try:
    ref = db.reference(f'live_wod/{a_id}')
    current_data = ref.get()
    reps = current_data.get('reps', 0) if current_data else 0
    
    st.metric(label=f"Current Score: {a_name}", value=f"{reps} REPS")

    if st.button("➕ SCORE REP"):
        ref.update({'reps': reps + 1, 'name': a_name})
        st.rerun()

    if st.button("➖ UNDO ERROR"):
        if reps > 0:
            ref.update({'reps': reps - 1})
            st.rerun()
except Exception as e:
    st.error(f"Database Error: {e}")
