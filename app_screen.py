import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & REFRESH ---
st.set_page_config(page_title="HN CrossFit Leaderboard", layout="wide")

# Refresh the screen every 3 seconds to show live score changes
st_autorefresh(interval=3000, key="screen_refresh")

# --- 2. FIREBASE SETUP ---
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
        st.error(f"Secret/Connection Error: {e}")

# --- 3. UI STYLING (TV STYLE) ---
st.markdown("""
    <style>
    .main { background-color: #000000; }
    .entry-card {
        background-color: #1a1a1a;
        border-radius: 12px;
        padding: 20px 40px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 15px solid #28a745;
    }
    .name-text { font-size: 40px !important; color: white; font-weight: bold; text-transform: uppercase; }
    .score-text { font-size: 55px !important; color: #28a745; font-weight: 900; }
    .rank-text { color: #666; font-size: 30px; margin-right: 25px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HEADER & WOD SELECTOR ---
st.title("🏆 WOD Rezulat")

# This allows you to toggle the screen between the 6 different workouts
target_wod = st.selectbox(
    "Select Workout to Display:", 
    ["WOD 1", "WOD 2", "WOD 3", "WOD 4", "WOD 5", "WOD 6"]
)
st.markdown("---")

# --- 5. DATA FETCHING ---
try:
    # Use the same path format as the Judge app
    db_path = f'competitions/{target_wod.replace(" ", "_")}'
    ref = db.reference(db_path)
    data = ref.get()

    if data:
        leaderboard_list = []
        
        # Robust handling for both Dictionary and List returns from Firebase
        if isinstance(data, dict):
            for key, val in data.items():
                if val and isinstance(val, dict):
                    leaderboard_list.append({
                        "name": val.get('name', f"Athlete {key}"),
                        "reps": val.get('reps', 0)
                    })
        elif isinstance(data, list):
            for index, val in enumerate(data):
                if val and isinstance(val, dict):
                    leaderboard_list.append({
                        "name": val.get('name', f"Athlete {index}"),
                        "reps": val.get('reps', 0)
                    })

        if leaderboard_list:
            # Sort: Higher reps = higher rank
            df = pd.DataFrame(leaderboard_list).sort_values(by="reps", ascending=False).reset_index(drop=True)

            for index, row in df.iterrows():
                # Filter out the "Loading Athletes..." junk if it exists in DB
                if "Loading" not in str(row['name']):
                    st.markdown(f"""
                        <div class="entry-card">
                            <div>
                                <span class="rank-text">#{index + 1}</span>
                                <span class="name-text">{row['name']}</span>
                            </div>
                            <div class="score-text">{row['reps']}</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info(f"No scores recorded yet for {target_wod}")
    else:
        st.warning(f"Waiting for judges to start {target_wod}...")

except Exception as e:
    st.error(f"Screen Connection Error: {e}")

st.caption("CrossFit Herceg Novi Real-Time Scoring")
