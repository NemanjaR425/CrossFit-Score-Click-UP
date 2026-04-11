import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- 1. KONTROLA ŠIRINE I RAZMAKA (Lako za prilagođavanje) ---
TABELA_SIRINA = "360px"    # Ukupna širina grafike
SIRINA_POZICIJA = "45px"   # Širina prve kolone (broj)
SIRINA_POENI = "75px"      # Širina zadnje kolone (rezultat)
LEVA_MARGINA = "60px"      # "Breathing space" sa leve strane
GORNJA_MARGINA = "50px"    # Razmak od vrha ekrana

# --- 2. KONFIGURACIJA STRANICE ---
st.set_page_config(page_title="vMix Clean Overlay", layout="wide")
# Automatsko osvežavanje na svake 3 sekunde za rezultate uživo
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

# --- 4. CSS ZA ČISTU GRAFIKU I SKRIVANJE UI ELEMENATA ---
st.markdown(f"""
    <style>
    /* Zelena pozadina za Chroma Key */
    .stApp {{ 
        background-color: #00FF00 !important; 
    }}
    
    /* SAKRIVANJE STREAMLIT IKONICA (Toolbar, Meni, Deploy dugme) */
    [data-testid="stHeader"], 
    footer, 
    .stDeployButton, 
    [data-testid="stToolbar"], 
    #MainMenu, 
    [data-testid="stStatusWidget"] {{ 
        display: none !important; 
        visibility: hidden !important; 
    }}
    
    /* Postavljanje Safe Area razmaka */
    .block-container {{ 
        padding-top: {GORNJA_MARGINA} !important;    
        padding-left: {LEVA_MARGINA} !important; 
        margin: 0 !important; 
    }}

    /* Glavni kontejner tabele */
    .corner-overlay {{
        width: {TABELA_SIRINA}; 
        font-family: 'Arial Black', Gadget, sans-serif;
    }}

    /* Stil za Gornji Logo */
    .logo-block {{
        background-color: white;
        color: black;
        padding: 15px;
        text-align: center;
        text-transform: uppercase;
        font-weight: 900;
        font-size: 20px;
        margin-bottom: 5px;
    }}

    /* Grid sistem za poravnanje kolona */
    .header-grid, .row-grid {{
        display: grid;
        grid-template-columns: {SIRINA_POZICIJA} 1fr {SIRINA_POENI};
        gap: 2px;
        margin-bottom: 2px;
    }}

    /* Stilovi za zaglavlje */
    .header-cell {{ 
        background-color: black; 
        color: white; 
        padding: 10px; 
        text-align: center; 
        font-size: 11px; 
        text-transform: uppercase;
    }}

    /* Stilovi za redove sa rezultatima */
    .pos-cell {{ 
        background: white; 
        color: black; 
        font-weight: 900; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        font-size: 18px; 
    }}
    
    .name-cell {{ 
        background: white; 
        color: black; 
        padding-left: 15px; 
        display: flex; 
        align-items: center; 
        font-weight: bold; 
        font-size: 15px; 
        overflow: hidden; 
        white-space: nowrap; 
    }}
    
    .reps-cell {{ 
        background: #1a1e26; 
        color: white; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        font-size: 20px; 
        font-weight: bold; 
    }}

    /* Stil za Sponzore */
    .sponsor-block {{
        background-color: white;
        color: black;
        padding: 15px;
        margin-top: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 14px;
        text-transform: uppercase;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 5. POVLAČENJE PODATAKA IZ FIREBASE-A ---
def get_stream_results():
    try:
        ref = db.reference('competitions')
        data = ref.get()
        if not data: return []
        
        results = []
        # Rukovanje podacima bez obzira da li su lista ili rečnik
        it = enumerate(data) if isinstance(data, list) else data.items()
        for _, athletes in it:
            if athletes:
                a_it = enumerate(athletes) if isinstance(athletes, list) else athletes.items()
                for _, d in a_it:
                    if d and isinstance(d, dict):
                        results.append({"Ime": d.get('name', 'N/A'), "Poeni": d.get('reps', 0)})
        
        if not results: return []
        
        # Grupisanje po imenu i sumiranje rezultata
        df = pd.DataFrame(results).groupby("Ime")["Poeni"].sum().reset_index()
        return df.sort_values(by="Poeni", ascending=False).reset_index(drop=True).head(10).to_dict('records')
    except Exception:
        return []

# --- 6. PRIKAZ NA EKRANU ---
# Koristimo kolone da bi desnih 80% ekrana ostalo potpuno prazno (zeleno)
left_col, _ = st.columns([1, 4])

with left_col:
    st.markdown('<div class="corner-overlay">', unsafe_allow_html=True)
    
    # Natpis na vrhu
    st.markdown('<div class="logo-block">Logo Takmičenja</div>', unsafe_allow_html=True)
    
    # Zaglavlje tabele
    st.markdown("""
        <div class="header-grid">
            <div class="header-cell">POZ</div>
            <div class="header-cell">TAKMIČAR</div>
            <div class="header-cell">PON</div>
        </div>
    """, unsafe_allow_html=True)

    # Dinamičko generisanje redova
    leaderboard = get_stream_results()
    if leaderboard:
        for i, row in enumerate(leaderboard):
            st.markdown(f"""
                <div class="row-grid">
                    <div class="pos-cell">{i+1}</div>
                    <div class="name-cell">{row['Ime']}</div>
                    <div class="reps-cell">{row['Poeni']}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='color:white; text-align:center; padding: 20px;'>Čekanje na podatke...</div>", unsafe_allow_html=True)

    # Donji blok za sponzore
    st.markdown('<div class="sponsor-block">SPONZORI OVDJE</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
