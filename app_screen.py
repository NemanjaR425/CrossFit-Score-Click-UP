import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Page Configuration for Big Screens
st.set_page_config(page_title="HN CrossFit Live Screen", layout="wide")

# 2. Auto-Refresh (Updates every 2 seconds)
st_autorefresh(interval=2000, key="leaderboard_refresh")

# 3. Firebase Setup
if not firebase_admin._apps:
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

# 4. Custom CSS for "TV Style" Leaderboard
st.markdown("""
    <style>
    /* Dark background for maximum contrast */
    .main { background-color: #000000; }
    
    .leaderboard-container {
        font-family: 'Arial Black', Gadget, sans-serif;
    }
    
    .entry-card {
        background-color: #1a1a1a;
        border-radius: 10px;
        padding: 15px 30px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 15px solid #28a745; /* Green accent */
    }
    
    .name-text {
        font-size: 45px !important;
        color: white;
        text-transform: uppercase;
    }
    
    .score-text {
        font-size: 60px !important;
        color: #28a745;
        font-weight: 900;
    }
    
    .rank-text {
        color: #555;
        font-size: 30px;
        margin-right: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 5. Header
st.title("🏆 HERCEG NOVI LIVE LEADERBOARD")
st.markdown("---")

# 6. Fetch and Display Data
try:
    # Ensure we point to the correct node in Firebase
    ref = db.reference('live_wod')
    data = ref.get()

    if data:
        leaderboard_data = []
        for key, val in data.items():
            # Use .get() to prevent KeyError if a field is missing
            name = val.get('name', f"Athlete {key}")
            reps = val.get('reps', 0)
            leaderboard_data.append({"name": name, "reps": reps})
        
        df = pd.DataFrame(leaderboard_data).sort_values(by="reps", ascending=False).reset_index(drop=True)

        for index, row in df.iterrows():
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
        st.warning("🏆 Waiting for the first rep... Ready for Herceg Novi!")

except Exception as e:
    # This will now show you the actual error if it's not a secret issue
    st.error(f"Connection status: {e}")

st.caption("Real-time results powered by Streamlit & Firebase")
