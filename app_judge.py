import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from streamlit_gsheets import GSheetsConnection

# 1. INIT FIREBASE
if not firebase_admin._apps:
    # Use .get() to safely pull secrets
    fb_secrets = st.secrets["firebase"]
    
    # THE FIX: Strip whitespace and handle double-escaped backslashes
    clean_key = fb_secrets["private_key"].strip().replace("\\n", "\n")
    
    cred_dict = {
        "type": fb_secrets["type"],
        "project_id": fb_secrets["project_id"],
        "private_key_id": fb_secrets["private_key_id"],
        "private_key": clean_key,
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

# 2. INIT GOOGLE SHEETS (For Names)
sheet_conn = st.connection("gsheets", type=GSheetsConnection)

st.set_page_config(page_title="Judge Clicker", layout="centered")

# 3. STYLING (Huge Green Button)
st.markdown("""
    <style>
    div.stButton > button:first-child {
        height: 12em; width: 100%; font-size: 45px !important;
        background-color: #28a745; color: white; border-radius: 20px;
    }
    .undo button { height: 4em !important; background-color: #6c757d !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. DATA LOADING
try:
    df = sheet_conn.read(worksheet="Athletes", ttl=600)
    athletes = [f"{r['Athlete_ID']} - {r['Name']}" for _, r in df.iterrows()]
except:
    athletes = ["1 - Loading..."]

# 5. UI
selected = st.selectbox("Assign Athlete:", athletes)
a_id, a_name = selected.split(" - ")

ref = db.reference(f'live_wod/{a_id}')
current = ref.get().get('reps', 0) if ref.get() else 0

st.metric(f"Judging: {a_name}", f"{current} Reps")

if st.button("➕ SCORE"):
    ref.update({'reps': current + 1, 'name': a_name})
    st.rerun()

st.markdown('<div class="undo">', unsafe_allow_html=True)
if st.button("➖ UNDO ERROR"):
    if current > 0:
        ref.update({'reps': current - 1})
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
