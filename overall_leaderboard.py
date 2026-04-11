import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- 1. OSNOVNA PODEŠAVANJA ---
st.set_page_config(page_title="vMix Overlay", layout="wide")
st_autorefresh(interval=3000, key="vmix_refresh")

# --- 2. FIREBASE (Standardno) ---
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

# --- 3. SPECIJALNI CSS ZA VMIX (Transparentnost umjesto Chrome Key-a) ---
st.markdown("""
    <style>
    /* Ključno: Postavljamo jarko zelenu koja je 'standard' za vMix */
    .stApp {
        background-color: #00FF00 !important;
    }

    /* Potpuno uklanjanje Streamlit elemenata koji guše pretraživač */
    [data-testid="stHeader"], footer, [data-testid="stSidebar"] { display: none !important; }
    .block-container { padding: 0 !important; }

    .stream-wrapper {
        position: fixed;
        top: 20px;
        left: 20px;
        width: 450px;
    }

    .box-white {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        color: black;
        font-weight: 800;
        text-align: center;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .table-row {
        display: flex;
        gap: 10px;
        margin-bottom: 8px;
    }

    .cell-pos { width: 60px; background: white; color: black; border-radius: 8px; text-align: center; font-weight: bold; padding: 10px 0; }
    .cell-name { flex-grow: 1; background: #00FF00; border: 3px solid white; color: white; border-radius: 8px; padding: 10px; font-weight: bold; }
    .cell-reps { width: 90px; background: #1a1e26; color: white; border-radius: 8px; text-align: center; font-weight: bold; padding: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# --- 4. LOGIKA PODATAKA ---
def get_data():
    try:
        ref = db.reference('competitions')
        data = ref.get()
        if not data: return []
        
        results = []
        # Fleksibilna obrada listi/dictova
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
data_list = get_data()

st.markdown('<div class="stream-wrapper">', unsafe_allow_html=True)
st.markdown('<div class="box-white">Leaderboard Live</div>', unsafe_allow_html=True)

for i, row in enumerate(data_list):
    st.markdown(f"""
        <div class="table-row">
            <div class="cell-pos">{i+1}</div>
            <div class="cell-name">{row['Ime']}</div>
            <div class="cell-reps">{row['Poeni']}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
