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
    
    /* Center the logo container */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        margin-bottom: 10px;
    }

    .leaderboard-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #1a1e26;
        padding: 12px 15px;
        margin-bottom: 8px;
        border-radius: 10px;
        border-left: 4px solid #ff8a50;
    }
    
    .info-container { display: flex; flex-direction: column; gap: 4px; }
    .rank-name { display: flex; align-items: center; gap: 10px; }
    .rank { color: #ff8a50; font-weight: 800; font-size: 16px; }
    .athlete-name { color: white; font-weight: 600; font-size: 15px; text-transform: uppercase; }
    .breakdown { color: #666; font-size: 11px; font-family: monospace; }
    .score-container { text-align: right; }
    .total-score { color: #ffffff; font-size: 22px; font-weight: 800; display: block; line-height: 1; }
    .score-label { color: #444; font-size: 9px; text-transform: uppercase; font-weight: bold; }

    h1 { color: white !important; font-size: 26px !important; text-align: center; margin-top: 0px !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. TOP LOGO SECTION ---
# Change LOGO_SIZE to adjust the width in pixels
LOGO_SIZE = 150

try:
    # We use 'width' instead of 'use_container_width' to control scaling
    st.image("logo.png", width=LOGO_SIZE) 
except:
    st.title("🏆 GENERAL STANDINGS")

# --- 5. DATA AGGREGATION ---
ref = db.reference('competitions')
all_data = ref.get()

if all_data:
    totals = {}
    for wod_key, athletes in all_data.items():
        display_wod = wod_key.replace("WOD_", "W") 
        athlete_items = athletes.items() if isinstance(athletes, dict) else enumerate(athletes)
        
        for a_id, info in athlete_items:
            if info:
                a_id_str = str(a_id)
                name = info.get("name", f"ID: {a_id_str}")
                reps = info.get("reps", 0)
                
                if a_id_str not in totals:
                    totals[a_id_str] = {"name": name, "total": 0, "breakdown": {}}
                
                totals[a_id_str]["total"] += reps
                totals[a_id_str]["breakdown"][display_wod] = reps

    sorted_overall = sorted(totals.values(), key=lambda x: x['total'], reverse=True)

    # --- 6. RENDER ---
    for i, entry in enumerate(sorted_overall):
        b_list = [f"{k}:{v}" for k, v in sorted(entry['breakdown'].items())]
        breakdown_str = " • ".join(b_list)

        st.markdown(f"""
            <div class="leaderboard-row">
                <div class="info-container">
                    <div class="rank-name">
                        <span class="rank">#{i+1}</span>
                        <span class="athlete-name">{entry['name']}</span>
                    </div>
                    <div class="breakdown">{breakdown_str}</div>
                </div>
                <div class="score-container">
                    <span class="total-score">{entry['total']}</span>
                    <span class="score-label">Total Reps</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("Syncing competition data...")
