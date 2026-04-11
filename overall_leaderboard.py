import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="vMix Leaderboard", layout="wide")
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

# --- 3. CSS (Popravljen da izbjegne totalni mrak) ---
st.markdown("""
    <style>
    /* Ako vidiš zeleno, aplikacija radi ali vMix još nije 'skinuo' boju */
    .stApp {
        background-color: #00FF00 !important;
    }

    [data-testid="stHeader"], footer { visibility: hidden; }

    .leaderboard-wrapper {
        background-color: rgba(0, 0, 0, 0.85); /* Skoro crna pozadina tabele */
        padding: 40px;
        border-radius: 25px;
        border: 4px solid white; /* Bijeli okvir da bi bio siguran da vidiš tabelu */
        margin: 50px auto;
        max-width: 900px;
        color: white;
    }

    .title {
        font-size: 50px;
        font-weight: 900;
        text-align: center;
        text-transform: uppercase;
        margin-bottom: 30px;
        color: #2da94f; /* Zeleni naslov */
    }

    /* Stilizacija same tabele */
    table {
        width: 100%;
        font-size: 32px !important;
        color: white !important;
    }
    th { background-color: #333 !important; padding: 10px !important; }
    td { padding: 15px !important; border-bottom: 1px solid #444 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKCIJA KOJA NE SMIJE DA PUKNE ---
def get_safe_results():
    try:
        ref = db.reference('competitions')
        data = ref.get()
        
        if not data:
            return pd.DataFrame(columns=["Rang", "Takmičar", "Ponavljanja"])

        results = []
        # Trik za obradu Firebase listi i rečnika istovremeno
        items = enumerate(data) if isinstance(data, list) else data.items()
        
        for wod_id, athletes in items:
            if athletes:
                a_items = enumerate(athletes) if isinstance(athletes, list) else athletes.items()
                for a_id, details in a_items:
                    if details and isinstance(details, dict):
                        results.append({
                            "Takmičar": details.get('name', f"ID: {a_id}"),
                            "Ponavljanja": details.get('reps', 0)
                        })

        df = pd.DataFrame(results)
        if not df.empty:
            summary = df.groupby("Takmičar")["Ponavljanja"].sum().reset_index()
            summary = summary.sort_values(by="Ponavljanja", ascending=False).reset_index(drop=True)
            summary.insert(0, "Rang", range(1, len(summary) + 1))
            return summary
            
        return pd.DataFrame(columns=["Rang", "Takmičar", "Ponavljanja"])
    except Exception as e:
        # Ako se desi greška, ispiši je direktno na ekranu da je vidiš u vMix-u
        return pd.DataFrame({"Greška": [str(e)]})

# --- 5. PRIKAZ ---
st.markdown('<div class="leaderboard-wrapper">', unsafe_allow_html=True)
st.markdown('<div class="title">TOP 10 POREDAK</div>', unsafe_allow_html=True)

df = get_safe_results()

if not df.empty:
    st.table(df.head(10)) # Prikazujemo samo top 10 radi preglednosti
else:
    st.markdown("<h2 style='text-align:center;'>NEMA PODATAKA</h2>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
