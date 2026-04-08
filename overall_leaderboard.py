import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & REFRESH ---
st.set_page_config(page_title="Overall Leaderboard", layout="centered")
st_autorefresh(interval=5000, key="overall_refresh")

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

# --- 3. STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    .block-container { padding-top: 1rem !important; max-width: 500px !important; }
    
    .leaderboard-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #1a1e26;
        padding: 12px 15px;
        margin-bottom: 8px;
        border-radius: 10px;
        border-left: 4px solid #ff8a50; /* Orange for Overall */
    }
    
    .rank-name-container { display: flex; align-items: center; gap: 12px; }
    .rank { color: #ff8a50; font-weight: 800; font-size: 16px; min-width: 25px; }
    .athlete-name {
        color: white;
        font-weight: 600;
        font-size: 15px;
        text-transform: uppercase;
    }
    
    .score-container { text-align: right; }
    .total-score { color: #ffffff; font-size: 22px; font-weight: 800; display: block; }
    .score-label { color: #666; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; }

    h1 { color: white !important; font-size: 28px !important; text-align: center; margin-bottom: 25px !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA AGGREGATION LOGIC ---
st.title("🏆 GENERAL STANDINGS")

# We fetch the entire 'competitions' node
ref = db.reference('competitions')
all_data = ref.get()

if all_data:
    # Dictionary to store totals: { athlete_id: {"name": str, "total_reps": int} }
    totals = {}

    for wod_name, athletes in all_data.items():
        if isinstance(athletes, dict):
            for a_id, info in athletes.items():
                if info:
                    name = info.get("name", f"ID: {a_id}")
                    reps = info.get("reps", 0)
                    
                    if a_id not in totals:
                        totals[a_id] = {"name": name, "total_reps": 0}
                    totals[a_id]["total_reps"] += reps
                    
        elif isinstance(athletes, list):
            for idx, info in enumerate(athletes):
                if info:
                    name = info.get("name", f"ID: {idx}")
                    reps = info.get("reps", 0)
                    
                    if str(idx) not in totals:
                        totals[str(idx)] = {"name": name, "total_reps": 0}
                    totals[str(idx)]["total_reps"] += reps

    # Sort by total reps
    sorted_overall = sorted(totals.values(), key=lambda x: x['total_reps'], reverse=True)

    # Render Standings
    for i, entry in enumerate(sorted_overall):
        st.markdown(f"""
            <div class="leaderboard-row">
                <div class="rank-name-container">
                    <span class="rank">#{i+1}</span>
                    <span class="athlete-name">{entry['name']}</span>
                </div>
                <div class="score-container">
                    <span class="total-score">{entry['total_reps']}</span>
                    <span class="score-label">Total Reps</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("Waiting for competition data to sync...")
