import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- 1. INITIALIZE CONNECTIONS ---
# Firebase for Live Speed
if not firebase_admin._apps:
    cred = credentials.Certificate("your-firebase-key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://your-project-id.firebaseio.com/' # Replace with your URL
    })

# Google Sheets for Athlete Names
sheet_conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. LOAD ATHLETE NAMES ---
try:
    athlete_df = sheet_conn.read(worksheet="Athletes")
    athlete_map = {str(row['Athlete_ID']): row['Name'] for _, row in athlete_df.iterrows()}
    athlete_options = [f"{k} - {v}" for k, v in athlete_map.items()]
except:
    athlete_options = ["1 - Loading..."]

# --- 3. JUDGE INTERFACE ---
st.set_page_config(page_title="LIVE Judge Clicker", layout="centered")

# Huge Button Styling
st.markdown("""
    <style>
    div.stButton > button:first-child {
        height: 12em;
        font-size: 40px !important;
        background-color: #28a745;
        color: white;
        border-radius: 20px;
    }
    .undo-btn button {
        height: 3em !important;
        background-color: #dc3545 !important;
    }
    </style>
    """, unsafe_allow_html=True)

selected = st.selectbox("Assign Judge to Athlete:", athlete_options)
a_id = selected.split(" - ")[0]
a_name = selected.split(" - ")[1]

# Connect to this specific athlete's "Live Slot"
ref = db.reference(f'live_wod/{a_id}')

# Get current state
data = ref.get()
current_reps = data.get('reps', 0) if data else 0

st.write(f"### Judging: **{a_name}**")
st.metric("Total Reps", current_reps)

# --- 4. THE CLICKER BUTTONS ---
if st.button("➕ COUNT REP", use_container_width=True):
    new_total = current_reps + 1
    ref.update({
        'reps': new_total,
        'name': a_name,
        'last_update': datetime.now().isoformat()
    })
    st.rerun()

st.markdown('<div class="undo-btn">', unsafe_allow_html=True)
if st.button("➖ UNDO ERROR"):
    if current_reps > 0:
        ref.update({'reps': current_reps - 1})
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
