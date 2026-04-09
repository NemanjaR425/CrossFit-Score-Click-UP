/* STIL ZA PLUS GUMB (Prvo dugme u nizu) */
    div[data-testid="stVerticalBlock"] > div:nth-of-type(1) div.stButton > button {
        width: 300px !important; /* OVDJE MIJENJAJ VELIČINU PLUS GUMBA */
        height: 300px !important;
        background-color: #2da94f !important;
        border-radius: 50% !important;
        border: none !important;
        margin: 20px auto !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0 10px 30px rgba(45, 169, 79, 0.3) !important;
    }

    /* Veličina samog "+" znaka */
    div[data-testid="stVerticalBlock"] > div:nth-of-type(1) div.stButton p {
        font-size: 150px !important;
        color: white !important;
        line-height: 1 !important;
    }

    /* STIL ZA MINUS GUMB (Drugo dugme u nizu) */
    div[data-testid="stVerticalBlock"] > div:nth-of-type(2) div.stButton > button {
        position: fixed !important;
        bottom: 30px !important;
        right: 25px !important;
        width: 80px !important; /* OVDJE MIJENJAJ VELIČINU MINUS GUMBA */
        height: 80px !important;
        background-color: #ff8a50 !important;
        border-radius: 50% !important;
        border: none !important;
        z-index: 9999 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    /* Veličina samog "-" znaka */
    div[data-testid="stVerticalBlock"] > div:nth-of-type(2) div.stButton p {
        font-size: 50px !important;
        color: white !important;
        line-height: 1 !important;
    }
