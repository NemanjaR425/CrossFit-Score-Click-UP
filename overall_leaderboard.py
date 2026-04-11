import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- 1. KONTROLA ŠIRINE I RAZMAKA ---
TABELA_SIRINA = "360px"    
SIRINA_POZICIJA = "45px"   
SIRINA_POENI = "75px"      
LEVA_MARGINA = "60px"      
GORNJA_MARGINA = "50px"    

# --- 2. KONFIGURACIJA STRANICE ---
st.set_page_config(page_title="vMix Clean Overlay", layout="wide")
st_autorefresh(interval=3000, key="broadcast_refresh")

# --- 3. FIREBASE KONEKCIJA ---
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

# --- 4. CSS ZA TOTALNO UKLANJANJE IKONICA ---
# Koristimo opšte selektore koji ciljaju sve Streamlit komponente interfejsa
st.markdown(f"""
    <style>
    /* 1. Chroma pozadina */
    .stApp {{ 
        background-color: #00FF00 !important; 
    }}
    
    /* 2. SAKRIVANJE SVIH SISTEMSKIH ELEMENATA */
    /* Sakriva Header, Footer, Meni dugme, Deploy dugme i Toolbar */
    header, footer, #MainMenu, .stDeployButton, [data-testid="stHeader"], 
    [data-testid="stToolbar"], [data-testid="stStatusWidget"], 
    [data-testid="stDecoration"], .viewerBadge_container__1QSob {{
        visibility: hidden !important;
        display: none !important;
    }}
    
    /* Dodatno sakrivanje bilo kakvog plutajućeg elementa u uglovima */
    iframe[title="Streamlit App Support"] {{ display: none !important; }}
    
    /* Postavljanje Safe Area */
    .block-container {{ 
        padding-top: {GORNJA_MARGINA} !important;    
        padding-left: {LEVA_MARGINA} !important; 
        margin: 0 !important; 
    }}

    /* Tvoja tabela */
    .corner-overlay {{
        width: {TABELA_SIRINA}; 
        font-family: 'Arial Black', sans-serif;
    }}

    .logo-block {{
        background-color: white; color: black; padding: 15px;
        text-align: center; text-transform: uppercase;
        font-weight: 900; font-size: 20px; margin-bottom: 5px;
    }}

    .header-grid, .row-grid {{
        display: grid;
        grid-template-columns: {SIRINA_POZICIJA} 1fr {SIRINA_POENI};
        gap: 2px; margin-bottom: 2px;
    }}

    .header-cell {{ 
        background-color: black; color: white; padding: 10px; 
        text-align: center; font-size: 11px; text-transform: uppercase;
    }}

    .pos-cell {{ background: white; color: black; font-weight: 900; display: flex; align-items: center; justify-content: center; font-size: 18px; }}
    .name-cell {{ background: white; color: black; padding-left: 15px; display: flex; align-items: center; font-weight: bold; font-size: 15px; overflow: hidden; white-space: nowrap; }}
    .reps-cell {{ background: #1a1e26; color: white; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; }}

    .sponsor-block {{
        background-color: white; color: black; padding: 15px;
        margin-top: 10px; text-align: center; font-weight: bold;
        font-size: 14px; text-transform: uppercase;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 5. DATA LOGIKA ---
def get_stream_results():
    try:
        ref = db.reference('competitions')
        data = ref.get()
        if not data: return []
        results = []
        
        # Ispravna obrada podataka iz Firebase-a
        it = enumerate(data) if isinstance(data, list) else data.items()
        for _, athletes in it:
            if athletes:
                a_it = enumerate(athletes) if isinstance(athletes, list) else athletes.items()
                for _, d in a_it:
                    if d and isinstance(d, dict):
                        # Osiguravamo da su poeni broj (integer)
                        reps = d.get('reps', 0)
                        results.append({"Ime": d.get('name', 'N/A'), "Poeni": int(reps)})
        
        if not results: return []
        
        # Grupisanje i sumiranje
        df = pd.DataFrame(results).groupby("Ime")["Poeni"].sum().reset_index()
        return df.sort_values(by="Poeni", ascending=False).reset_index(drop=True).head(10).to_dict('records')
    except Exception:
        return []

# --- 6. RENDER ---
left_col, _ = st.columns([1, 4])

with left_col:
    st.markdown('<div class="corner-overlay">', unsafe_allow_html=True)
    st.markdown('<div class="logo-block">Logo Takmičenja</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="header-grid">
            <div class="header-cell">POZ</div>
            <div class="header-cell">TAKMIČAR</div>
            <div class="header-cell">PON</div>
        </div>
    """, unsafe_allow_html=True)

    leaderboard = get_stream_results()
    if leaderboard:
        for i, row in enumerate(leaderboard):
            # Formiranje redova koristeći sigurne varijable
            pos = i + 1
            name = row['Ime']
            score = row['Poeni']
            
            st.markdown(f"""
                <div class="row-grid">
                    <div class="pos-cell">{pos}</div>
                    <div class="name-cell">{name}</div>
                    <div class="reps-cell">{score}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='color:white; text-align:center;'>Čekanje na rezultate...</div>", unsafe_allow_html=True)

    st.markdown('<div class="sponsor-block">SPONZORI OVDJE</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
