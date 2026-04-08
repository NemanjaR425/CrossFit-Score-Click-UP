import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & REFRESH ---
st.set_page_config(page_title="Live Track", layout="centered")
st_autorefresh(interval=2000, key="screen_refresh") # Faster refresh for live feel

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

# --- 3. MOBILE STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    .block-container { padding-top: 1rem !important; max-width: 500px !important; }
    
    /* Live Status Card */
    .live-card {
        background: #1a1e26;
        border-radius: 20px;
        padding: 30px 20px;
        text-align: center;
        border: 2px solid #333;
        margin-top: 20px;
    }
    
    .athlete-label {
        color: #888;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }
    
    .athlete-name {
        color: white;
        font-size: 28px;
        font-weight: 800;
        margin-bottom: 25px;
        line-height: 1.2;
    }
    
    .score-circle {
        width: 150px;
        height: 150px;
        border: 8px solid #2da94f;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin: 0 auto;
        background: #0b0e14;
        box-shadow: 0 0 30px rgba(45, 169, 79, 0.2);
    }
    
    .live-reps {
        color: white;
        font-size: 60px;
        font-weight: 900;
        line-height: 1;
    }
    
    .reps-label {
        color: #2da94f;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
    }

    h1 { color: white !important; font-size: 22px !important; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 4. DISPLAY LOGIC ---
st.title("⏱️ LIVE PERFORMANCE")

# Selectors stay at the top for easy switching
selected_wod = st.selectbox("Event", ["WOD 1", "WOD 2", "WOD 3", "WOD 4", "WOD 5", "WOD 6"])

# Fetch specific athlete to track
db_path = f'competitions/{selected_wod.replace(" ", "_")}'
ref = db.reference(db_path)
data = ref.get()

if data:
    # Get a list of names for the search box
    names = []
    if isinstance(data, dict):
        names = [info.get("name", "Unknown") for info in data.values() if info]
    elif isinstance(data, list):
        names = [info.get("name", "Unknown") for info in data if info]
    
    target_athlete = st.selectbox("Track Athlete:", sorted(list(set(names))))

    # Find the specific score
    current_reps = 0
    athlete_items = data.items() if isinstance(data, dict) else enumerate(data)
    
    for _, info in athlete_items:
        if info and info.get("name") == target_athlete:
            current_reps = info.get("reps", 0)
            break

    # RENDER LIVE CARD
    st.markdown(f"""
        <div class="live-card">
            <div class="athlete-label">Currently Tracking</div>
            <div class="athlete-name">{target_athlete}</div>
            <div class="score-circle">
                <div class="live-reps">{current_reps}</div>
                <div class="reps-label">Reps</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.info("Waiting for live data...")
