import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="HN CrossFit Judge", layout="centered")

# --- 1. FIREBASE CONNECTION ---
if not firebase_admin._apps:
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

# --- 2. UI STYLING ---
st.markdown("""
    <style>
    div.stButton > button:first-child { height: 12em; width: 100%; font-size: 40px !important; background-color: #28a745; color: white; border-radius: 20px; font-weight: bold; }
    .undo button { height: 4em !important; background-color: #6c757d !important; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Pulling the spreadsheet directly using the ID from Secrets
    df = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], worksheet="Athletes", ttl=0)
    athlete_list = [f"{int(row['Athlete_ID'])} - {row['Name']}" for _, row in df.iterrows()]
except Exception as e:
    st.error(f"Waiting for Sheet: {e}")
    athlete_list = ["1 - Check Sheet Name/Permissions"]

# --- 4. INTERFACE ---
st.title("⏱️ Live Score Clicker")
selected_athlete = st.selectbox("Select Athlete:", athlete_list)

a_id = selected_athlete.split(" - ")[0]
a_name = selected_athlete.split(" - ")[1] if " - " in selected_athlete else "Athlete"

ref = db.reference(f'live_wod/{a_id}')
current_data = ref.get()
reps = current_data.get('reps', 0) if current_data else 0

st.metric(label=f"Current Reps: {a_name}", value=f"{reps} REPS")

if st.button("➕ SCORE REP"):
    ref.update({'reps': reps + 1, 'name': a_name})
    st.rerun()

st.markdown('<div class="undo">', unsafe_allow_html=True)
if st.button("➖ UNDO ERROR"):
    if reps > 0:
        ref.update({'reps': reps - 1})
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
