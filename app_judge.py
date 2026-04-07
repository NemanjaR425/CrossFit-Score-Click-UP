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
        st.error(f"Firebase Setup Error: {e}")

# --- 3. UI STYLING ---
st.markdown("""
    <style>
    /* Large green button for high-intensity scoring */
    div.stButton > button:first-child {
        height: 10em; 
        width: 100%; 
        font-size: 45px !important;
        background-color: #28a745; 
        color: white; 
        border-radius: 20px;
        font-weight: bold;
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

# --- 4. ROBUST ATHLETE FETCHING ---
@st.cache_data(ttl=60)
def get_athlete_list():
    try:
        # Using direct CSV export to bypass GSheets Connection 400/404 errors
        sheet_id = "1z1ga9p39C0KJDSOK6ZzU0OUSgKM1UbSh9BiMPMSQ1PY"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Athletes"
        df = pd.read_csv(url)
        # Drop empty rows and format names
        df = df.dropna(subset=['Athlete_ID', 'Name'])
        return [f"{int(row['Athlete_ID'])} - {row['Name']}" for _, row in df.iterrows()]
    except Exception as e:
        return ["1 - Loading Athletes..."]

athlete_list = get_athlete_list()

# --- 5. APP INTERFACE ---
st.title("⏱️ Live Score Clicker")

selected_athlete = st.selectbox("Select Athlete on Lane:", athlete_list)

# Safety check: Parse ID and Name
if " - " in selected_athlete:
    a_id = selected_athlete.split(" - ")[0]
    a_name = selected_athlete.split(" - ")[1]
else:
    a_id = "0"
    a_name = "None"

# --- 6. LIVE DATABASE LOGIC ---
if a_id != "0":
    try:
        ref = db.reference(f'live_wod/{a_id}')
        current_data = ref.get()
        reps = current_data.get('reps', 0) if current_data else 0

        st.divider()
        st.metric(label=f"Current Reps for {a_name}", value=f"{reps} REPS")

        # SAFETY: Only allow scoring if it's a real athlete
        if "Loading" not in selected_athlete:
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
        else:
            st.warning("Please wait for athletes to load...")

    except Exception as e:
        st.error(f"Database Error: {e}")
else:
    st.info("Please select an athlete to begin scoring.")

st.divider()
st.caption("CrossFit Herceg Novi - Live Results System")
