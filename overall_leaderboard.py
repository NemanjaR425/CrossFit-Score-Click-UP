import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURACIJA (Fiksni Layout) ---
st.set_page_config(page_title="Stream Overlay", layout="wide", initial_sidebar_state="collapsed")
# Automatsko osvežavanje na 3 sekunde za LIVE rezultate
st_autorefresh(interval=3000, key="broadcast_refresh")

# --- 2. FIREBASE KONEKCIJA (Tvoji secrets) ---
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

# --- 3. CSS ZA FLAT DIZAJN U ĆOŠKU ---
st.markdown("""
    <style>
    /* 1. Pozadina za Chroma Key u vMix-u */
    .stApp {
        background-color: #00FF00 !important;
    }
    
    /* Sakrivanje Streamlit UI elemenata */
    [data-testid="stHeader"], footer, .stDeployButton { display: none !important; }
    .block-container { padding: 0 !important; margin: 0 !important; }

    /* 2. Pozicioniranje i fiksna širina overlay-a u gornjem levom uglu */
    .corner-overlay {
        position: fixed;
        top: 25px;
        left: 25px;
        width: 420px; /* FIKSNA ŠIRINA - ne skališe se */
        font-family: 'Arial Black', Gadget, sans-serif;
        color: white;
        z-index: 9999;
    }

    /* 3. LOGO blok (belo, oštri uglovi) */
    .logo-block {
        background-color: white;
        color: black;
        padding: 15px;
        text-align: center;
        text-transform: uppercase;
        font-weight: 900;
        font-size: 20px;
        margin-bottom: 20px;
        letter-spacing: 1px;
    }

    /* 4. ZAGLAVLJA tabele (crna kockica) */
    .header-grid {
        display: grid;
        grid-template-columns: 60px 1fr 90px;
        gap: 8px;
        margin-bottom: 8px;
        text-transform: uppercase;
        font-size: 13px;
        font-weight: bold;
    }
    .header-cell {
        background-color: black;
        color: white;
        padding: 10px;
        text-align: center;
    }

    /* 5. REDOVI (Flat dizajn, spojeni pravougaonici) */
    .row-grid {
        display: grid;
        grid-template-columns: 60px 1fr 90px;
        gap: 8px; /* Mali razmak između kockica u redu */
        margin-bottom: 8px; /* Mali razmak između redova */
        font-size: 18px;
        font-weight: bold;
    }

    /* 5a. Pozicija (Belo) */
    .pos-cell {
        background-color: white;
        color: black;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
    }

    /* 5b. Ime (BELO SA BELIM OKVIROM - KAO U TEMPLATE) */
    .name-cell {
        background-color: white; /* Belo */
        color: black;
        border: 4px solid white; /* Beli okvir (da se stopi sa belom pozadinom) */
        display: flex;
        align-items: center;
        padding-left: 15px;
    }

    /* 5c. Ponavljanja (TAMNO PLAVA/CRNA kockica) */
    .reps-cell {
        background-color: #1a1e26; /* Tamna boja rezultata */
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
    }

    /* 6. SPONSOR blok (isto kao logo) */
    .sponsor-block {
        background-color: white;
        color: black;
        padding: 25px;
        margin-top: 15px;
        text-align: center;
        font-weight: bold;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA LOGIKA (Firebase) ---
def get_stream_results():
    try:
        ref = db.reference('competitions')
        data = ref.get()
        if not data: return []
        
        results = []
        # Trik za obradu Firebase listi i rečnika
        it = enumerate(data) if isinstance(data, list) else data.items()
        for _, athletes in it:
            if athletes:
                a_it = enumerate(athletes) if isinstance(athletes, list) else athletes.items()
                for _, d in a_it:
                    if d and isinstance(d, dict):
                        results.append({"Ime": d.get('name', 'N/A'), "Poeni": d.get('reps', 0)})
        
        if not results: return []
        df = pd.DataFrame(results).groupby("Ime")["Poeni"].sum().reset_index()
        # Vraćamo samo top 10 radi prostora u ćošku
        return df.sort_values(by="Poeni", ascending=False).reset_index(drop=True).head(10).to_dict('records')
    except: return []

# --- 5. PRIKAZ ---
st.markdown('<div class="corner-overlay">', unsafe_allow_html=True)

# 1. Logo Blok
st.markdown('<div class="logo-block">Takmičarski Logo</div>', unsafe_allow_html=True)

# 2. Zaglavlja (Prevedeno)
st.markdown("""
    <div class="header-grid">
        <div class="header-cell">Poz.</div>
        <div class="header-cell">Takmičar</div>
        <div class="header-cell">Pon.</div>
    </div>
""", unsafe_allow_html=True)

# 3. Dinamički redovi iz Firebase-a
leaderboard = get_stream_results()

if leaderboard:
    for i, row in enumerate(leaderboard):
        html_row = f"""
            <div class="row-grid">
                <div class="pos-cell">{i+1}</div>
                <div class="name-cell">{row['Ime']}</div>
                <div class="reps-cell">{row['Poeni']}</div>
            </div>
        """
        st.markdown(html_row, unsafe_allow_html=True)
else:
    st.markdown("<h4 style='text-align:center; color:white;'>Čekanje...</h4>", unsafe_allow_html=True)

# 4. Sponsor Blok
st.markdown('<div class="sponsor-block">Sponzori ovdje<br>Sponzori ovdje</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
