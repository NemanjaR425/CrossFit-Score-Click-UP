import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time

if not firebase_admin._apps:
    cred = credentials.Certificate("your-firebase-key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://your-project-id.firebaseio.com/'
    })

st.set_page_config(page_title="Live Leaderboard", layout="wide")
st.title("🔥 HERCEG NOVI LIVE RACE")

TARGET_REPS = st.sidebar.number_input("Target Reps to Finish", value=50)

# Create a placeholder we can overwrite in the loop
placeholder = st.empty()

while True:
    with placeholder.container():
        all_data = db.reference('live_wod').get()
        
        if all_data:
            # Sort by most reps first
            sorted_athletes = sorted(all_data.items(), key=lambda x: x[1].get('reps', 0), reverse=True)
            
            for aid, val in sorted_athletes:
                name = val.get('name', f"Athlete {aid}")
                reps = val.get('reps', 0)
                
                # Calculate progress
                progress = min(reps / TARGET_REPS, 1.0)
                
                col1, col2 = st.columns([1, 4])
                col1.write(f"**{name}** ({reps})")
                col2.progress(progress)
        else:
            st.info("Waiting for judges to start...")
            
    time.sleep(0.5) # Refresh every half-second
