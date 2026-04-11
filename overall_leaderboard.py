import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --- 1. KONFIGURACIJA I AUTOMATSKO OSVEŽAVANJE ---
st.set_page_config(page_title="Stream Overlay", layout="wide")
# Osvežavanje na 3 sekunde za LIVE rezultate
st_autorefresh(interval=3000, key="stream_refresh")

# --- 2. FIREBASE KONEKCIJA (Obavezno za tvoje secrets) ---
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

# --- 3. MOĆNI CSS ZA KOPIRANJE ŠABLONA ---
st.markdown("""
    <style>
    /* 1. Chroma Key pozadina i sakrivanje UI */
    .stApp {
        background-color: #00FF00 !important;
    }
    [data-testid="stHeader"], footer { visibility: hidden; }

    /* 2. Pozicioniranje grafike u gornji levi ugao */
    .stream-overlay {
        position: fixed;
        top: 20px;
        left: 20px;
        width: 480px; /* Prilagodite širinu prema ekranu */
        font-family: 'Helvetica Neue', Arial, sans-serif;
        color: white;
        z-index: 9999;
    }

    /* 3. Stilovi za LOGO blok (belo sa zaobljenim ivicama) */
    .logo-block {
        background-color: white;
        color: black;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        text-transform: uppercase;
        font-weight: 900;
        font-size: 20px;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }

    /* 4. Stilovi za SPONSOR blok (isto kao logo) */
    .sponsor-block {
        background-color: white;
        color: black;
        border-radius: 15px;
        padding: 30px;
        margin-top: 20px;
        text-align: center;
        font-size: 18px;
    }

    /* 5. Stilovi za ZAGLAVLJA tabele (crna kockica) */
    .table-headers {
        display: grid;
        grid-template-columns: 80px 1fr 120px;
        gap: 15px;
        margin-bottom: 15px;
        text-transform: uppercase;
        font-size: 14px;
        font-weight: bold;
        color: white;
    }
    .header-cell {
        background-color: black;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
    }

    /* 6. Stilovi za REDOVE u tabeli (Chroma zelena kockica za 'NAME') */
    .leaderboard-row {
        display: grid;
        grid-template-columns: 80px 1fr 120px;
        gap: 15px;
        margin-bottom: 15px;
        font-size: 18px;
        font-weight: bold;
    }

    /* 6a. Ćelija za Poziciju (belo) */
    .pos-cell {
        background-color: white;
        color: black;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 15px 0;
    }

    /* 6b. Ćelija za Ime (ZELENA SA BELIM OKVIROM - KAO U TEMPLATE) */
    .name-cell {
        background-color: #00FF00; /* Chroma boja */
        color: white;
        border-radius: 12px;
        border: 4px solid white; /* Beli okvir */
        display: flex;
        align-items: center;
        padding-left: 20px;
    }

    /* 6c. Ćelija za Ponavljanja (TAMNO PLAVA - KAO U TEMPLATE) */
    .reps-cell {
        background-color: #2e2a5e; /* Tamno plava */
        color: white;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKCIJA ZA PODATKE (Otporna na liste i dictove) ---
def get_stream_poredak():
    try:
        ref = db.reference('competitions')
        all_data = ref.get()
        if not all_data: return pd.DataFrame()
        results = []
        # Trik: ako je all_data lista (numerički ključevi), koristimo enumerate, inače .items()
        items = enumerate(all_data) if isinstance(all_data, list) else all_data.items()
        for wod_id, athletes in items:
            if athletes:
                a_items = enumerate(athletes) if isinstance(athletes, list) else athletes.items()
                for a_id, details in a_items:
                    if details and isinstance(details, dict):
                        results.append({
                            "Ime": details.get('name', f"ID: {a_id}"),
                            "Ponavljanja": details.get('reps', 0)
                        })
        df = pd.DataFrame(results)
        if not df.empty:
            summary = df.groupby("Ime")["Ponavljanja"].sum().reset_index()
            summary = summary.sort_values(by="Ponavljanja", ascending=False).reset_index(drop=True)
            summary.insert(0, "Pos", range(1, len(summary) + 1))
            return summary.head(10) # Prikazujemo samo TOP 10 radi prostora
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame({"Greška": [str(e)]})

# --- 5. GENERISANJE ČISTOG HTML-a I PRIKAZ ---
st.markdown('<div class="stream-overlay">', unsafe_allow_html=True)

# 1. Logo Blok (Prevedeno)
st.markdown('<div class="logo-block">Takmičarski<br>Logo</div>', unsafe_allow_html=True)

# 2. Zaglavlja (Prevedeno)
st.markdown("""
    <div class="table-headers">
        <div class="header-cell">Rang</div>
        <div class="header-cell">Ime</div>
        <div class="header-cell">Pon.</div>
    </div>
    """, unsafe_allow_html=True)

# 3. Dinamičko generisanje redova iz Firebase-a
leaderboard_df = get_stream_poredak()

if not leaderboard_df.empty:
    for index, row in leaderboard_df.iterrows():
        # Pravimo HTML string za svaki red posebno
        html_row = f"""
            <div class="leaderboard-row">
                <div class="pos-cell">{row['Pos']}</div>
                <div class="name-cell">{row['Ime']}</div>
                <div class="reps-cell">{row['Ponavljanja']}</div>
            </div>
        """
        st.markdown(html_row, unsafe_allow_html=True)
else:
    st.markdown("<h4 style='text-align:center;'>Čekanje...</h4>", unsafe_allow_html=True)

# 4. Sponsor Blok (Prevedeno)
st.markdown('<div class="sponsor-block">Sponzori ovdje<br>Sponzori ovdje</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
