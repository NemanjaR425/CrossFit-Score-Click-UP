import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG & REFRESH ---
st.set_page_config(page_title="HN CrossFit Overall Rankings", layout="wide")
st_autorefresh(interval=5000, key="overall_refresh") # Refresh every 5 seconds

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
        st.error(f"Connection Error: {e}")

# --- 3. UI STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0b0e14; }
    .overall-card {
        background-color: #161b22;
        border-radius: 10px;
        padding: 15px 25px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 10px solid #ffc107; /* Gold accent for overall */
    }
    .name-text { font-size: 30px !important; color: white; font-weight: bold; }
    .total-text { font-size: 40px !important; color: #ffc107; font-weight: 900; }
    .breakdown-text { color: #8b949e; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA PROCESSING ---
st.title("🥇 OVERALL COMPETITION STANDINGS")
st.markdown("### Cumulative Score Across All 6 WODs")

try:
    # Pull the entire competition tree
    root_ref = db.reference('competitions')
    all_data = root_ref.get()

    if all_data:
        # Dictionary to store athlete totals: { name: { 'total': X, 'breakdown': 'WOD1: 10...' } }
        totals = {}
        wods = ["WOD_1", "WOD_2", "WOD_3", "WOD_4", "WOD_5", "WOD_6"]

        for wod_name in wods:
            wod_data = all_data.get(wod_name, {})
            
            # Handle list vs dict from Firebase
            entries = []
            if isinstance(wod_data, dict):
                entries = wod_data.values()
            elif isinstance(wod_data, list):
                entries = [v for v in wod_data if v is not None]

            for entry in entries:
                name = entry.get('name', 'Unknown')
                if "Loading" in name: continue # Skip junk data
                
                reps = entry.get('reps', 0)
                
                if name not in totals:
                    totals[name] = {"total": 0, "details": {}}
                
                totals[name]["total"] += reps
                totals[name]["details"][wod_name] = reps

        # Convert to list for sorting
        leaderboard = []
        for name, data in totals.items():
            # Create a string like "W1: 10 | W2: 15..."
            breakdown = " | ".join([f"{w.replace('_',' ')}: {data['details'].get(w, 0)}" for w in wods])
            leaderboard.append({
                "name": name,
                "total": data["total"],
                "breakdown": breakdown
            })

        # Sort by total reps descending
        df = pd.DataFrame(leaderboard).sort_values(by="total", ascending=False).reset_index(drop=True)

        # --- 5. DISPLAY ---
        for index, row in df.iterrows():
            st.markdown(f"""
                <div class="overall-card">
                    <div>
                        <div class="name-text">#{index + 1} {row['name']}</div>
                        <div class="breakdown-text">{row['breakdown']}</div>
                    </div>
                    <div class="total-text">{row['total']}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No data available across workouts yet.")

except Exception as e:
    st.error(f"Error calculating totals: {e}")
