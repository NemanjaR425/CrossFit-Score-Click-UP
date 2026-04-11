import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="vMix Safe Overlay", layout="wide")
st_autorefresh(interval=3000, key="broadcast_refresh")

# --- 2. FIREBASE KONEKCIJA ---
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

# --- 3. CSS SA SAFE AREA RAZMAKOM ---
st.markdown("""
    <style>
    /* Chroma pozadina */
    .stApp { background-color: #00FF00 !important; }
    [data-testid="stHeader"], footer, .stDeployButton { display: none !important; }
    
    /* Resetovanje Streamlitovog default paddinga */
    .block-container { 
        padding-top: 50px !important;    /* Razmak odozgo */
        padding-left: 60px !important;   /* SAFE AREA sa lijeve strane */
        margin: 0 !important; 
    }

    /* Kontejner za tabelu - FIKSNA ŠIRINA */
    .corner-overlay {
        width: 420px; 
        font-family: 'Arial Black', sans-serif;
    }

    /* Logo - Flat dizajn */
    .logo-block {
        background-color: white;
        color: black;
        padding: 15px;
        text-align: center;
        text-transform: uppercase;
        font-weight: 900;
        font-size: 20px;
        margin-bottom: 5px;
    }

    /* Tabela */
    .header-grid {
        display: grid;
        grid-template-columns: 50px 1fr 80px;
        gap: 2px;
        margin-bottom: 2px;
    }
    .header-cell {
        background-color: black;
        color: white;
        padding: 10px;
        text-align: center;
        font-size: 11px;
    }

    .row-grid {
        display: grid;
        grid-template-columns: 50px 1fr 80px;
        gap: 2px;
        margin-bottom: 2px;
    }
    .pos-cell { background: white; color: black; font-weight: 900; display: flex; align-items: center; justify-content: center; font-size: 18px; }
    .name-cell { background: white; color: black; padding-left: 15px; display: flex; align-items: center; font-weight: bold; font-size: 15px; }
    .reps-cell { background: #1a1e26; color: white; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; }

    /* Sponzori */
    .sponsor-block {
        background-color: white;
        color: black;
        padding: 15px;
        margin-top: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA LOGIKA ---
def get_stream_results():
    try:
        ref = db.reference('competitions')
        data = ref.get()
        if not data: return []
        results = []
        it = enumerate(data) if isinstance(data, list) else data.items()
        for _, athletes in it:
            if athletes:
                a_it = enumerate(athletes) if isinstance(athletes, list) else athletes.items()
                for _, d in a_it:
                    if d and isinstance(d, dict):
                        results.append({"Ime": d.get('name', 'N/A'), "Poeni": d.get('reps', 0)})
        if not results: return []
        df = pd.DataFrame(results).groupby("Ime")["Poeni"].sum().reset_index()
        return df.sort_values(by="Poeni", ascending=False).reset_index(drop=True).head(10).to_dict('records')
    except: return []

# --- 5. RENDER ---
# Ovdje koristimo kolone da bismo tabelu zadržali strogo lijevo
left_col, _ = st.columns([1, 3])

with left_col:
    st.markdown('<div class="corner-overlay">', unsafe_allow_html=True)
    st.markdown('<div class="logo-block">Takmičarski Logo</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="header-grid">
            <div class="header-cell">POZ</div>
            <div class="header-cell">IME I PREZIME</div>
            <div class="header-cell">PON</div>
        </div>
    """, unsafe_allow_html=True)

    leaderboard = get_stream_results()
    for i, row in enumerate(leaderboard):
        st.markdown(f"""
            <div class="row-grid">
                <div class="pos-cell">{i+1}</div>
                <div class="name-cell">{row['Ime']}</div>
                <div class="reps-cell">{row['Poeni']}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sponsor-block">SPONZORI OVDJE</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
