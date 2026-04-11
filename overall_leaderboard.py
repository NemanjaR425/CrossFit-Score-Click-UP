import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import os

# --- 1. FIREBASE KONEKCIJA ---
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

# --- 2. FUNKCIJA ZA GENERISANJE HTML-a ---
def generate_vmix_html(df):
    rows_html = ""
    for i, row in df.iterrows():
        rows_html += f"""
        <div style="display: flex; gap: 10px; margin-bottom: 8px; font-family: Arial; font-weight: bold;">
            <div style="width: 50px; background: white; color: black; border-radius: 8px; text-align: center; padding: 10px;">{i+1}</div>
            <div style="flex-grow: 1; background: transparent; border: 3px solid white; color: white; border-radius: 8px; padding: 10px;">{row['Ime']}</div>
            <div style="width: 80px; background: #1a1e26; color: white; border-radius: 8px; text-align: center; padding: 10px;">{row['Poeni']}</div>
        </div>
        """
    
    full_html = f"""
    <html>
        <body style="background-color: #00FF00; margin: 20px; overflow: hidden;">
            <div style="width: 400px;">
                <div style="background: white; color: black; padding: 10px; border-radius: 8px; text-align: center; font-weight: 900; margin-bottom: 15px;">LEADERBOARD</div>
                {rows_html}
            </div>
        </body>
    </html>
    """
    # Čuvamo fajl lokalno
    with open("vmix_overlay.html", "w", encoding="utf-8") as f:
        f.write(full_html)

# --- 3. GLAVNA PETLJA ---
st.title("vMix Signal Generator")
st.write("Ova aplikacija generiše 'vmix_overlay.html' u tvom folderu.")

# Uzmi podatke iz Firebase
try:
    ref = db.reference('competitions')
    data = ref.get()
    if data:
        results = []
        it = enumerate(data) if isinstance(data, list) else data.items()
        for _, athletes in it:
            if athletes:
                a_it = enumerate(athletes) if isinstance(athletes, list) else athletes.items()
                for _, d in a_it:
                    if d and isinstance(d, dict):
                        results.append({"Ime": d.get('name', 'N/A'), "Poeni": d.get('reps', 0)})
        
        if results:
            df = pd.DataFrame(results).groupby("Ime")["Poeni"].sum().reset_index()
            df = df.sort_values(by="Poeni", ascending=False).reset_index(drop=True).head(10)
            generate_vmix_html(df)
            st.success("HTML generisan! Uvezi 'vmix_overlay.html' u vMix.")
            st.table(df)
except Exception as e:
    st.error(f"Greška: {e}")

# Automatsko osvežavanje same skripte
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=3000, key="generator")
