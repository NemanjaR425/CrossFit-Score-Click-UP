import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & REFRESH ---
st.set_page_config(page_title="Live Leaderboard", layout="centered")
st_autorefresh(interval=2000, key="live_refresh") # Fast 2s refresh

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

# --- 3. MOBILE GRID STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    .block-container { padding-top: 1rem !important; max-width: 600px !important; }
    
    /* Grid Container */
    .live-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr); /* 2 columns on mobile */
        gap: 10px;
        margin-top: 15px;
    }
    
    /* Athlete Score Card */
    .athlete-card {
        background: #1a1e26;
        border-radius: 12px;
        padding: 15px 10px;
        text-align: center;
        border: 1px solid #333;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .athlete-name {
        color: #aaa;
        font-size: 13px;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 5px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .athlete-score {
        color: #2da94f;
        font-size: 38px;
        font-weight: 900;
        line-height: 1;
    }
    
    .reps-label {
        color: #555;
        font-size: 9px;
        text-transform: uppercase;
        margin-top: 2px;
    }

    h1 { color: white !important; font-size: 22px !important; text-align: center; margin-bottom: 0 !important; }
    .stSelectbox { margin-bottom: 20px !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. DISPLAY LOGIC (FIXED) ---
st.title("⚡ LIVE WOD TRACKER")

selected_wod = st.selectbox("Select Event", ["WOD 1", "WOD 2", "WOD 3", "WOD 4", "WOD 5", "WOD 6"])

db_path = f'competitions/{selected_wod.replace(" ", "_")}'
ref = db.reference(db_path)
data = ref.get()

if data:
    athletes_list = []
    if isinstance(data, dict):
        athletes_list = [info for info in data.values() if info]
    elif isinstance(data, list):
        athletes_list = [info for info in data if info]

    athletes_list = sorted(athletes_list, key=lambda x: x.get('reps', 0), reverse=True)

    # Start building the string
    grid_html = '<div class="live-grid">'
    for athlete in athletes_list:
        name = athlete.get('name', 'Unknown')
        reps = athlete.get('reps', 0)
        
        grid_html += f"""
            <div class="athlete-card">
                <div class="athlete-name">{name}</div>
                <div class="athlete-score">{reps}</div>
                <div class="reps-label">Reps</div>
            </div>
        """
    grid_html += '</div>'
    
    # CRITICAL FIX: Added unsafe_allow_html=True
    st.markdown(grid_html, unsafe_allow_html=True) 
else:
    st.info("No live athletes in this heat yet.")
