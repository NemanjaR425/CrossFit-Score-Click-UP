import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from streamlit_gsheets import GSheetsConnection

# --- FIREBASE SETUP ---
if not firebase_admin._apps:
    fb_secrets = st.secrets["firebase"]
    # Build clean dictionary for Firebase
    cred_dict = {
        "type": fb_secrets["type"],
        "project_id": fb_secrets["project_id"],
        "private_key_id": fb_secrets["private_key_id"],
        "private_key": fb_secrets["private_key"].replace("\\n", "\n"),
        "client_email": fb_secrets["client_email"],
        "client_id": fb_secrets["client_id"],
        "auth_uri": fb_secrets["auth_uri"],
        "token_uri": fb_secrets["token_uri"],
        "auth_provider_x509_cert_url": fb_secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": fb_secrets["client_x509_cert_url"],
    }
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["database"]["url"]})

st.set_page_config(page_title="Judge Clicker", layout="centered")

# --- UI STYLING ---
st.markdown("""
    <style>
    div.stButton > button:first-child {
        height: 10em; width: 100%; font-size: 40px !important;
        background-color: #28a745; color: white; border-radius: 15px;
    }
    .undo button { height: 3em !important; background-color: #6c757d !important; margin-top: 10px;}
    </style>
    """, unsafe_allow_html=True)

# --- GOOGLE SHEETS FOR ATHLETE NAMES ---
conn = st.connection("gsheets", type=GSheetsConnection)
try:
    df = conn.read(worksheet="Athletes", ttl=300)
    athlete_list = [f"{row['Athlete_ID']} - {row['Name']}" for _, row in df.iterrows()]
except:
    athlete_list = ["1 - Loading Athletes..."]

st.title("⏱️ Live Score")
selected_athlete = st.selectbox("Select Athlete:", athlete_list)
a_id = selected_athlete.split(" - ")[0]
a_name = selected_athlete.split(" - ")[1]

# --- LIVE LOGIC ---
ref = db.reference(f'live_wod/{a_id}')
current_data = ref.get()
reps = current_data.get('reps', 0) if current_data else 0

st.metric(label=f"Athlete: {a_name}", value=f"{reps} Reps")

if st.button("➕ SCORE REP"):
    ref.update({'reps': reps + 1, 'name': a_name})
    st.rerun()

st.markdown('<div class="undo">', unsafe_allow_html=True)
if st.button("➖ UNDO ERROR"):
    if reps > 0:
        ref.update({'reps': reps - 1})
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
