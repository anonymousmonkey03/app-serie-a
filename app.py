import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ---------------------------------------------------------
# 1. CONFIGURAZIONE PAGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Serie A Intelligence - Soft Stats",
    page_icon="⚽",
    layout="wide"
)

# Squadre ufficiali Serie A 2024/2025 - 2025/2026
SERIE_A_CLUBS = [
    "Atalanta", "Bologna", "Cagliari", "Como", "Empoli",
    "Fiorentina", "Genoa", "Inter", "Juventus", "Lazio",
    "Lecce", "Milan", "Monza", "Napoli", "Parma",
    "Roma", "Torino", "Udinese", "Venezia", "Verona"
]

# ---------------------------------------------------------
# 2. CARICAMENTO DATI (CSV O FALLBACK)
# ---------------------------------------------------------
@st.cache_data
def load_fallback_data():
    """Dataset di esempio per evitare crash se i CSV non sono ancora caricati."""
    players_demo = [
        {"player_id": 1, "name": "Paulo Dybala", "current_club_name": "Roma", "date_of_birth": "1993-11-15"},
        {"player_id": 2, "name": "Federico Chiesa", "current_club_name": "Liverpool", "date_of_birth": "1997-10-25"},
        {"player_id": 3, "name": "Dušan Vlahović", "current_club_name": "Juventus", "date_of_birth": "2000-01-28"},
        {"player_id": 4, "name": "Piotr Zieliński", "current_club_name": "Inter", "date_of_birth": "1994-05-20"},
        {"player_id": 5, "name": "Romelu Lukaku", "current_club_name": "Napoli", "date_of_birth": "1993-05-13"},
        {"player_id": 6, "name": "Giocatore Test Compleanno", "current_club_name": "Roma", "date_of_birth": f"1998-{datetime.now().strftime('%m-%d')}"}
    ]
    transfers_demo = [
        {"player_id": 1, "player_name": "Paulo Dybala", "from_club_name": "Juventus", "to_club_name": "Roma"},
        {"player_id": 2, "player_name": "Federico Chiesa", "from_club_name": "Fiorentina", "to_club_name": "Juventus"},
        {"player_id": 3, "player_name": "Dušan Vlahović", "from_club_name": "Fiorentina", "to_club_name": "Juventus"},
        {"player_id": 4, "player_name": "Piotr Zieliński", "from_club_name": "Napoli", "to_club_name": "Inter"},
        {"player_id": 5, "player_name": "Romelu Lukaku", "from_club_name": "Inter", "to_club_name": "Roma"},
        {"player_id": 5, "player_name": "Romelu Lukaku", "from_club_name": "Roma", "to_club_name": "Napoli"},
        {"player_id": 6, "player_name": "Giocatore Test Compleanno", "from_club_name": "Lazio", "to_club_name": "Roma"}
    ]
    
    df_p = pd.DataFrame(players_demo)
    df_t = pd.DataFrame(transfers_demo)
    df_p['date_of_birth'] = pd.to_datetime(df_p['date_of_birth'])
    return df_p, df_t

def get_data(uploaded_players=None, uploaded_transfers=None):
    """Carica i dati dai file caricati, dai CSV locali o usa il fallback."""
    if uploaded_players is not None and uploaded_transfers is not None:
        df_players = pd.read_csv(uploaded_players)
        df_transfers = pd.read_csv(uploaded_transfers)
        source = "File caricati manualmente"
    elif os.path.exists("players.csv") and os.path.exists("transfers.csv"):
        df_players = pd.read_csv("players.csv")
        df_transfers = pd.read_csv("transfers.csv")
        source = "File CSV del Repository GitHub"
    else:
        df_players, df_transfers = load_fallback_data()
        source = "Dataset Demo Integrato (Carica i file CSV per i dati reali)"

    # Normalizzazione colonne
    p_cols = {c.lower(): c for c in df_players.columns}
    t_cols = {c.lower(): c for c in df_transfers.columns}

    # Identifica colonna nome e data nascita
    name_col = p_cols.get('name', p_cols.get('player_name', 'name'))
    dob_col = p_cols.get('date_of_birth', p_cols.get('dob', 'date_of_birth'))
    club_col = p_cols.get('current_club_name', p_cols.get('squadra', 'current_club_name'))

    df_players['date_of_birth_dt'] = pd.to_datetime(df_players[dob_col], errors='coerce')
    
    return df_players, df_transfers, source, name_col, club_col

# ---------------------------------------------------------
# 3. SIDEBAR DI CONFIGURAZIONE
# ---------------------------------------------------------
st.sidebar.title("⚽ Configurazione Dati")
st.sidebar.info("Puoi caricare qui i file `players.csv` e `transfers.csv` scaricati da Kaggle se non li hai inviati su GitHub.")

up_players = st.sidebar.file_uploader("Carica players.csv", type=["csv"])
up_transfers = st.sidebar.file_uploader("Carica transfers.csv", type=["csv"])

df_players, df_transfers, data_source, name_col, club_col = get_data(up_players, up_transfers)

st.sidebar.write("---")
st.sidebar.caption(f"**Fonte Dati Attuale:** {data_source}")

# ---------------------------------------------------------
# 4. DASHBOARD PRINCIPALE
# ---------------------------------------------------------
st.title("⚽ Serie A Intelligence: Compleanni & Ex di Turno")
today = datetime.now()
st.markdown(f"**Data di oggi:** `{today.strftime('%d/%m/%Y')}`")

st.markdown("---")

# --- SEZIONE 1: COMPLEANNI DI OGGI ---
st.subheader("🎂 Compleanni di Oggi")

today_month = today.month
today_day = today.day

#
