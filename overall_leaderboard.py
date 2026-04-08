import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & REFRESH ---
st.set_page_config(page_title="Leaderboard", layout="centered")
st_autorefresh(interval=5000, key="leaderboard_refresh")

# --- 2. FIREBASE CONNECTION ---
if not firebase_admin._apps:
    fb_secrets = st.secrets["firebase"]
    fixed_key = fb_secrets["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate({
        "type": fb_secrets["type"], "project_id": fb_secrets["project_id"],
        "private_key_id": fb_secrets["private_key_id"], "private_key": fixed_key,
        "client_email": fb_secrets["client_email"], "client_id": fb_secrets["client_id"],
        "auth_uri": fb_secrets["auth_uri"], "token_uri": fb_secrets["token_uri"],
        "auth_provider_x509_cert_url": fb_secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": fb_secrets["client_x509_cert_url"],
    })
    firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["database"]["url"]})

# --- 3. STYLING (The Mobile Redesign) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    .block-container { padding-top: 1rem !important; max-width: 500px !important; }
    
    /* Compact Row Styling */
    .leaderboard-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #1a1e26;
        padding: 10px 15px;
        margin-bottom: 6px;
        border-radius: 8px;
        border-left: 4px solid #2da94f;
    }
    
    .rank-name-container {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .rank {
        color: #888;
        font-weight: 800;
        font-size: 14px;
        min-width: 20px;
    }
    
    .athlete-name {
        color: white;
        font-weight: 500;
        font-size: 16px; /* Shrunk from your previous version */
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .score-container {
        text-align: right;
    }
    
    .score-value {
        color: #2da94f;
        font-size: 20px;
        font-weight: 800;
        display: block;
    }
    
    .score-label {
        color: #666;
        font-size: 10px;
        text-transform: uppercase;
    }

    h1 { color: white !important; font-size: 24px !important; margin-bottom: 20px !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA LOGIC ---
st.title("🏆 Leaderboard")

selected_wod = st.selectbox("Select Event", ["WOD 1", "WOD 2", "WOD 3", "WOD 4", "WOD 5", "WOD 6"])
db_path = f'competitions/{selected_wod.replace(" ", "_")}'
ref = db.reference(db_path)
data = ref.get()

if data:
    # Convert Firebase dict to a sorted list
    leaderboard_list = []
    for athlete_id, info in data.items():
        leaderboard_list.append({
            "name": info.get("name", f"ID: {athlete_id}"),
            "reps": info.get("reps", 0)
        })
    
    # Sort by reps descending
    sorted_data = sorted(leaderboard_list, key=lambda x: x['reps'], reverse=True)

    # Render as custom Mobile Cards
    for i, entry in enumerate(sorted_data):
        st.markdown(f"""
            <div class="leaderboard-row">
                <div class="rank-name-container">
                    <span class="rank">{i+1}</span>
                    <span class="athlete-name">{entry['name']}</span>
                </div>
                <div class="score-container">
                    <span class="score-value">{entry['reps']}</span>
                    <span class="score-label">Reps</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("No data recorded for this WOD yet.")
