import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time

# 1. INIT FIREBASE
if not firebase_admin._apps:
    # Build the credential dictionary manually from secrets
    # This avoids any 'Streamlit-specific' extra data causing the ValueError
    cred_dict = {
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
    }
    
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': st.secrets["database"]["url"]
    })

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
