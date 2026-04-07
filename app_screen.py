import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time

# 1. INIT FIREBASE
if not firebase_admin._apps:
    fb_dict = dict(st.secrets["firebase"])
    cred = credentials.Certificate(fb_dict)
    firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["database"]["url"]})

st.set_page_config(page_title="HN Live Race", layout="wide")
st.title("🔥 HERCEG NOVI LIVE RACE")

TARGET = st.sidebar.number_input("Target Reps", value=50)
REFRESH = st.sidebar.slider("Refresh (sec)", 0.1, 1.0, 0.3)

placeholder = st.empty()

# 2. LIVE LOOP
while True:
    with placeholder.container():
        data = db.reference('live_wod').get()
        if data:
            # Sort by reps descending
            sorted_data = sorted(data.items(), key=lambda x: x[1].get('reps', 0), reverse=True)
            
            for aid, val in sorted_data:
                name = val.get('name', f"Athlete {aid}")
                reps = val.get('reps', 0)
                progress = min(reps / TARGET, 1.0)
                
                col1, col2 = st.columns([1, 4])
                col1.write(f"🏆 **{name}**" if reps >= TARGET else f"**{name}** ({reps})")
                col2.progress(progress)
        else:
            st.info("Waiting for reps...")
    time.sleep(REFRESH)
