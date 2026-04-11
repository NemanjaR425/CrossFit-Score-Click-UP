import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURACIJA ---
# Isključujemo padding da bi grafika bila fiksirana uz ivicu
st.set_page_config(page_title="vMix Overlay", layout="wide")
st_autorefresh(interval=3000, key="vmix_refresh")

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

# --- 3. SPECIJALNI BROADCAST CSS ---
st.markdown("""
    <style>
    /* Čista Chroma zelena za pozadinu */
    .stApp { background-color: #00FF00 !important; }
    
    /* Sakrivanje Streamlit UI-ja koji usporava vMix */
    [data-testid="stHeader"], footer, [data-testid="stSidebar"], .stDeployButton { display: none !important; }
    .block-container { padding: 0 !important; margin: 0 !important; }

    .stream-overlay {
        position: absolute;
        top: 30px;
        left: 30px;
        width: 460px;
        font-family: 'Arial Black', Gadget, sans-serif;
    }

    .logo-box {
        background-color: white;
        color: black;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        text-transform: uppercase;
        font-weight: 900;
        font-size: 22px;
        margin-bottom: 15px;
    }

    .header-grid {
        display: grid;
        grid-template-columns: 60px 1fr 100px;
        gap: 10px;
        margin-bottom: 10px;
    }
    .header-cell {
        background: black;
        color: white;
        text-align: center;
        padding: 8px;
        border-radius: 8px;
        font-size: 12px;
    }

    .row-grid {
        display: grid;
        grid-template-columns: 60px 1fr 100px;
        gap: 10px;
        margin-bottom: 8px;
    }
    .cell-pos {
        background: white;
        color: black;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        font-weight: 900;
    }
    .cell-name {
        background: #00FF00; /* Chroma */
        color: white;
        border: 3px solid white;
        border-radius: 10px;
        padding-left: 15px;
        display: flex;
        align-items: center;
        font-size: 18px;
    }
    .cell-reps {
        background: #1a1e26;
        color: white;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
    }

    .sponsor-box {
        background: white;
        color: black;
        border-radius: 12px;
        padding: 20px;
        margin-top: 15px;
        text-align: center;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA LOGIKA ---
def get_data():
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
                        results.append({"Ime": d.get('name', 'N/A'), "Reps": d.get('reps', 0)})
        
        if not results: return []
        df = pd.DataFrame(results).groupby("Ime")["Reps"].sum().reset_index()
        return df.sort_values(by="Reps", ascending=False).reset_index(drop=True).head(10).to_dict('records')
    except: return []

# --- 5. RENDEROVANJE ---
st.markdown('<div class="stream-overlay">', unsafe_allow_html=True)
st.markdown('<div class="logo-box">COMPETITION LOGO</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="header-grid">
        <div class="header-cell">POS</div>
        <div class="header-cell">NAME</div>
        <div class="header-cell">REPS</div>
    </div>
""", unsafe_allow_html=True)

leaderboard = get_data()
for i, row in enumerate(leaderboard):
    st.markdown(f"""
        <div class="row-grid">
            <div class="cell-pos">{i+1}</div>
            <div class="cell-name">{row['Ime']}</div>
            <div class="cell-reps">{row['Reps']}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="sponsor-box">Sponsors Space</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
