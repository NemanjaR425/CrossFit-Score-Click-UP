import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# 1. Setup Firebase Connection
if not firebase_admin._apps:
    # Use the JSON file you downloaded in Step 1
    cred = credentials.Certificate("your-firebase-key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://your-project-id.firebaseio.com/'
    })

st.set_page_config(page_title="LIVE Clicker", layout="centered")

# 2. Select Athlete to Track
# (In a real event, each judge would have one specific athlete)
athlete_id = st.selectbox("Select Athlete you are Judging:", ["A1", "A2", "A3", "A4"])

st.write("---")

# 3. The Live Counter Logic
ref = db.reference(f'live_scores/{athlete_id}')

# Get current reps from Firebase
current_data = ref.get()
reps = current_data.get('reps', 0) if current_data else 0

col1, col2 = st.columns([3, 1])

with col1:
    if st.button("➕ SCORE REP", use_container_width=True):
        reps += 1
        ref.update({'reps': reps, 'name': athlete_id, 'timestamp': str(datetime.now())})
        st.rerun()

with col2:
    if st.button("➖ UNDO", use_container_width=True):
        if reps > 0:
            reps -= 1
            ref.update({'reps': reps})
            st.rerun()

st.metric(label="Current Count", value=reps)
