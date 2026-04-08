import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & REFRESH ---
# We use st.empty() as a hack to force the page to reload when the refresh key changes
st.set_page_config(page_title="Judge Clicker - Herceg Novi", layout="centered", initial_sidebar_state="collapsed")
st_autorefresh(interval=3000, key="datarefresh") # Keep the local rep count synced with DB

# --- 2. FIREBASE CONNECTION SETUP ---
# (Keep this exact block; the logic is perfect)
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
        st.error(f"Firebase Setup Error: {e}")

# --- 3. ATHLETE & WOD DATA (Caching for speed) ---
# (Keep this exact block for efficient GSheet reading)
@st.cache_data(ttl=60)
def get_athlete_list():
    try:
        sheet_id = "1z1ga9p39C0KJDSOK6ZzU0OUSgKM1UbSh9BiMPMSQ1PY"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Athletes"
        df = pd.read_csv(url).dropna(subset=['Athlete_ID', 'Name'])
        return [f"{int(row['Athlete_ID'])}-{row['Name']}" for _, row in df.iterrows()]
    except Exception as e:
        return ["1-Loading Athletes..."]

athlete_list = get_athlete_list()
# Standard list of your 6 WODs
wod_list = ["WOD 1", "WOD 2", "WOD 3", "WOD 4", "WOD 5", "WOD 6"]

# --- 4. ADVANCED AESTHETICS (The UX Overhaul) ---
st.markdown("""
    <style>
    /* Dark Theme Enforcement */
    .stApp { background-color: #0b0e14 !important; color: white; }
    
    /* Header (WOD and Athlete Selectors) */
    .stSelectbox label { font-size: 18px !important; color: #888 !important; }
    .stSelectbox div[data-baseweb="select"] { background-color: #1a1e26 !important; border-color: #2a313e !important; color: white !important; }

    /* The main interface container */
    .clicker-interface {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        height: 75vh;
        margin-top: 20px;
    }

    /* The Large 'REPS' Display */
    .score-display {
        font-size: 130px !important;
        font-weight: 900 !important;
        color: white;
        text-align: center;
        margin-top: -30px;
        line-height: 1;
    }
    .score-display-label { font-size: 40px !important; color: #888; text-transform: uppercase; }

    /* The Giant Green Pulsing Up Button */
    /* Target the first (Up) button precisely */
    div[data-testid="stColumn"][aria-labelledby="up_button"] > div > div > button {
        border-radius: 50% !important;
        width: 250px !important;
        height: 250px !important;
        background-color: #28a745 !important;
        font-size: 150px !important;
        line-height: 1 !important;
        color: white !important;
        border: none !important;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 10px 30px rgba(40, 167, 69, 0.4) !important;
        transition: transform 0.1s ease-in-out;
        z-index: 5;
    }
    div[data-testid="stColumn"][aria-labelledby="up_button"] > div > div > button:active { transform: scale(0.95); }

    /* The Smaller Orange Down Button */
    /* Target the second (Down) button precisely */
    div[data-testid="stColumn"][aria-labelledby="down_button"] > div > div > button {
        border-radius: 50% !important;
        width: 70px !important;
        height: 70px !important;
        background-color: #ff9f43 !important;
        font-size: 50px !important;
        line-height: 1 !important;
        color: #fff !important;
        border: none !important;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 5px 15px rgba(255, 159, 67, 0.3) !important;
        z-index: 5;
    }

    /* Column layouts for button placement */
    .row-widget.stHorizontal > div { gap: 0px; }
    [data-testid="stMarkdownContainer"] { text-align: center; }
    
    </style>
    """, unsafe_allow_html=True)

# --- 5. DATA LOGIC & UI LAYOUT ---
st.header("Judge Clicker")

# Stacked Selectors at the top
selected_wod = st.selectbox("Select WOD:", wod_list)
selected_athlete = st.selectbox("Select Athlete:", athlete_list)

# Parse IDs and Names
if "-" in selected_athlete:
    a_id = selected_athlete.split("-")[0]
    a_name = selected_athlete.split("-")[1]
else:
    a_id = "0"
    a_name = "None"

if a_id != "0":
    try:
        # Define the DB path based on selected WOD
        db_path = f'competitions/{selected_wod.replace(" ", "_")}/{a_id}'
        ref = db.reference(db_path)
        current_data = ref.get()
        reps = current_data.get('reps', 0) if current_data else 0

        # Start the focused clicker interface container
        st.markdown('<div class="clicker-interface">', unsafe_allow_html=True)

        # 1. The big score display
        st.markdown(f'<div class="score-display">{reps} <span class="score-display-label">REPS</span></div>', unsafe_allow_html=True)

        # 2. The button layout: Giant green center, smaller orange offset
        col_main, col_spacer, col_undo = st.columns([6, 1, 1.5])
        
        # This wrapper identifies this column as the Up button container for CSS
        with col_main:
            st.markdown('<div aria-labelledby="up_button">', unsafe_allow_html=True)
            if "Loading" not in selected_athlete:
                if st.button("+"):
                    ref.update({
                        'reps': reps + 1,
                        'name': a_name,
                        'last_update': str(pd.Timestamp.now())
                    })
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Spacer column to separate buttons
        with col_spacer:
             st.empty()

        # This wrapper identifies this column as the Down button container for CSS
        with col_undo:
            st.markdown('<div aria-labelledby="down_button" style="margin-top: auto; margin-bottom: 20px;">', unsafe_allow_html=True)
            if "Loading" not in selected_athlete:
                if st.button("-"):
                    if reps > 0:
                        ref.update({'reps': reps - 1})
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True) # End interface container

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("Please select an athlete to begin.")

# Final clean signature
st.divider()
st.caption("HN CrossFit - Live Results")
