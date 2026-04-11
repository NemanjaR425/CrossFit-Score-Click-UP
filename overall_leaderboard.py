import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURACIJA STRANICE ---
st.set_page_config(
    page_title="LIVE Leaderboard", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Automatsko osvježavanje svake 3 sekunde za rezultate uživo
st_autorefresh(interval=3000, key="broadcast_refresh")

# --- 2. FIREBASE KONEKCIJA ---
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

# --- 3. SPECIJALNI VMIX CSS (CHROMA KEY) ---
st.markdown("""
    <style>
    /* Zelena pozadina za Chroma Key u vMix-u */
    .stApp {
        background-color: #00FF00 !important;
    }

    /* Sakrivanje svih Streamlit elemenata koji kvare grafiku */
    [data-testid="stHeader"], footer, #MainMenu {
        visibility: hidden;
    }

    /* Kontejner za tabelu - tamna i polunapravidna za bolji kontrast */
    .leaderboard-container {
        background-color: rgba(11, 14, 20, 0.9);
        padding: 30px;
        border-radius: 20px;
        border: 2px solid #333;
        margin-top: 50px;
    }

    /* Stilizacija naslova */
    .title-text {
        color: white;
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 5px;
        margin-bottom: 20px;
    }

    /* Tabela dizajna */
    .stTable {
        width: 100%;
        color: white !important;
        font-size: 28px !important;
    }
    
    /* Povećanje redova u tabeli za bolju čitljivost na TV-u */
    table {
        border-collapse: collapse;
        width: 100%;
    }
    
    th {
        background-color: #2da94f !important;
        color: white !important;
        text-align: left !important;
        padding: 15px !important;
        font-size: 22px;
    }
    
    td {
        padding: 15px !important;
        border-bottom: 1px solid #444 !important;
    }

    /* Isticanje prvog mjesta */
    tr:nth-child(1) {
        background-color: rgba(255, 215, 0, 0.2) !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIKA ZA POVLAČENJE PODATAKA ---
def get_all_results():
    try:
        ref = db.reference('competitions')
        all_data = ref.get()
        
        results = []
        if all_data:
            for wod_name, athletes in all_data.items():
                for athlete_id, details in athletes.items():
                    results.append({
                        "Takmičar": details.get('name', 'Neznato'),
                        "WOD": wod_name.replace("_", " "),
                        "Ponavljanja": details.get('reps', 0)
                    })
        
        df = pd.DataFrame(results)
        
        # Agregacija - sabiranje ponavljanja kroz sve WOD-ove za ukupni poredak
        if not df.empty:
            summary = df.groupby("Takmičar")["Ponavljanja"].sum().reset_index()
            summary = summary.sort_values(by="Ponavljanja", ascending=False).reset_index(drop=True)
            summary.index += 1  # Rangiranje od 1
            return summary
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Greška: {e}")
        return pd.DataFrame()

# --- 5. PRIKAZ ZA BROADCAST ---
st.markdown('<div class="leaderboard-container">', unsafe_allow_html=True)
st.markdown('<div class="title-text">Ukupni Poredak - Live</div>', unsafe_allow_html=True)

leaderboard_df = get_all_results()

if not leaderboard_df.empty:
    # Prikaz tabele
    st.table(leaderboard_df)
else:
    st.markdown("<h3 style='text-align:center; color:white;'>Čekanje na rezultate...</h3>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
