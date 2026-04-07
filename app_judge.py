import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="Judge Clicker - Herceg Novi", layout="centered")

# --- 2. FIREBASE CONNECTION SETUP ---
if not firebase_admin._apps:
    try:
        fb_secrets = st.secrets["firebase"]
        # Handle the common private key formatting issue for Streamlit Cloud
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
        firebase_admin.initialize_app(cred, {
            'databaseURL': st.secrets["database"]["url"]
        })
    except Exception as e:
        st.error(f"Firebase Certificate Error: {e}")

# --- 3. UI STYLING ---
st.markdown("""
    <style>
    /* Large green button for high-intensity scoring */
    div.stButton > button:first-child {
        height: 12em; 
        width: 100%; 
        font-size: 45px !important;
        background-color: #28a745; 
        color: white; 
        border-radius: 20px;
        font-weight: bold;
        border: 2px solid #1e7e34;
    }
    /* Smaller grey button for undoing mistakes */
    .undo-container button { 
        height: 4em !important; 
        background-color: #6c757d !important; 
        font-size: 20px !important;
        margin-top: 15px;
    }
    .stSelectbox label { font-size: 22px !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. GOOGLE SHEETS CONNECTION ---
# This pulls the athlete list from your shared spreadsheet
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    df = conn.read(
        spreadsheet=sheet_url,
        worksheet="Athletes",
        ttl=0  # Force refresh to get latest athlete names
    )
    
    # Cleaning the data: ensure headers are correct and drop empty rows
    df = df.dropna(subset=['Athlete_ID', 'Name'])
    athlete_list = [f"{int(row['Athlete_ID'])} - {row['Name']}" for _, row in df.iterrows()]
except Exception as e:
    st.warning("Connecting to Athlete List...")
    athlete_list = ["1 - Loading Athletes..."]

# --- 5. APP INTERFACE ---
st.title("⏱️ Live Score Clicker")

# Athlete Selection
selected_athlete = st.selectbox("Select Athlete on Lane:", athlete_list)

# Split ID and Name for Firebase storage
try:
    a_id = selected_athlete.split(" - ")[0]
    a_name = selected_athlete.split(" - ")[1]
except IndexError:
    a_id = "1"
    a_name = "Athlete"

# --- 6. LIVE DATABASE LOGIC ---
ref = db.reference(f'live_wod/{a_id}')
current_data = ref.get()
reps = current_data.get('reps', 0) if current_data else 0

# Display Current Score
st.divider()
st.metric(label=f"Current Reps for {a_name}", value=f"{reps} REPS")

# Scoring Buttons
if st.button("➕ SCORE REP"):
    ref.update({
        'reps': reps + 1,
        'name': a_name,
        'last_update': str(pd.Timestamp.now())
    })
    st.rerun()

st.markdown('<div class="undo-container">', unsafe_allow_html=True)
if st.button("➖ UNDO ERROR"):
    if reps > 0:
        ref.update({'reps': reps - 1})
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.caption("CrossFit Herceg Novi - Live Results System")
