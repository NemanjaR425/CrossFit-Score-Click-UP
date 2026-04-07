# On the Big Screen Laptop
import streamlit as st
from firebase_admin import db

st.title("🔥 LIVE RACE STATUS")

# This creates a loop that checks Firebase every 0.5 seconds
while True:
    scores = db.reference('live_scores').get()
    
    if scores:
        for aid, data in scores.items():
            name = data.get('name', aid)
            count = data.get('reps', 0)
            target = 100 # Example: First to 100 reps wins
            
            progress = min(count / target, 1.0)
            st.write(f"**Athlete {name}**: {count} / {target}")
            st.progress(progress)
            
    st.empty() # Clears the screen for the next millisecond update
