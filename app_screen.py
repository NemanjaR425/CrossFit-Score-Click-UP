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
