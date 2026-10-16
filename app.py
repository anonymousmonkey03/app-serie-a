import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# ---------------------------------------------------------
# 1. CONFIGURAZIONE PAGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Serie A Intelligence - Soft Stats",
    page_icon="⚽",
    layout="wide"
)

SERIE_A_MAP = {
    "Atalanta": ["atalanta"],
    "Bologna": ["bologna"],
    "Cagliari": ["cagliari"],
    "Como": ["como"],
    "Empoli": ["empoli"],
    "Fiorentina": ["fiorentina"],
    "Genoa": ["genoa"],
    "Inter": ["inter", "internazionale"],
    "Juventus": ["juventus"],
    "Lazio": ["lazio"],
    "Lecce": ["lecce"],
    "Milan": ["milan"],
    "Monza": ["monza"],
    "Napoli": ["napoli"],
    "Parma": ["parma"],
    "Roma": ["roma"],
    "Torino": ["torino"],
    "Udinese": ["udinese"],
    "Venezia": ["venezia"],
    "Verona": ["verona", "hellas"]
}

# ---------------------------------------------------------
# 2. FUNZIONI DI SUPPORTO E CARICAMENTO
# ---------------------------------------------------------
def find_column(df, candidates):
    """Trova la colonna corretta provando vari nomi possibili."""
    for c in df.columns:
        if c.lower().strip() in candidates:
            return c
    return None

def match_team(team_str, target_key):
    """Controlla se il nome nel CSV corrisponde alla squadra selezionata."""
    if pd.isna(team_str):
        return False
    team_clean = str(team_str).lower()
    keywords = SERIE_A_MAP.get(target_key, [target_key.lower()])
    return any(kw in team_clean for kw in keywords)

@st.cache_data
def load_fallback():
    p_data = [
        {"name": "Paulo Dybala", "current_club_name": "AS Roma", "date_of_birth": "1993-11-15"},
        {"name": "Dušan Vlahović", "current_club_name": "Juventus FC", "date_of_birth": "2000-01-28"},
        {"name": "Piotr Zieliński", "current_club_name": "FC Internazionale", "date_of_birth": "1994-05-20"},
        {"name": "Romelu Lukaku", "current_club_name": "SSC Napoli", "date_of_birth": "1993-05-13"},
        {"name": "Giocatore Test", "current_club_name": "AS Roma", "date_of_birth": datetime.now().strftime('%Y-%m-%d')}
    ]
    t_data = [
        {"player_name": "Paulo Dybala", "from_club_name": "Juventus FC", "to_club_name": "AS Roma"},
        {"player_name": "Dušan Vlahović", "from_club_name": "ACF Fiorentina", "to_club_name": "Juventus FC"},
        {"player_name": "Piotr Zieliński", "from_club_name": "SSC Napoli", "to_club_name": "FC Internazionale"},
        {"player_name": "Romelu Lukaku", "from_club_name": "FC Internazionale", "to_club_name": "AS Roma"},
        {"player_name": "Romelu Lukaku", "from_club_name": "AS Roma", "to_club_name": "SSC Napoli"}
    ]
    return pd.DataFrame(p_data), pd.DataFrame(t_data)

# ---------------------------------------------------------
# 3. SIDEBAR - GESTIONE CARICAMENTO CSV
# ---------------------------------------------------------
st.sidebar.title("📁 Caricamento Database")

up_players = st.sidebar.file_uploader("1. Carica players.csv", type=["csv"])
up_transfers = st.sidebar.file_uploader("2. Carica transfers.csv", type=["csv"])

df_players = None
df_transfers = None

# Lettura Players
if up_players is not None:
    df_players = pd.read_csv(up_players)
    st.sidebar.success(f"✅ `players.csv`: {len(df_players):,} righe")
elif os.path.exists("players.csv"):
    df_players = pd.read_csv("players.csv")
    st.sidebar.success(f"✅ `players.csv` (da repo): {len(df_players):,} righe")

# Lettura Transfers
if up_transfers is not None:
    df_transfers = pd.read_csv(up_transfers)
    st.sidebar.success(f"✅ `transfers.csv`: {len(df_transfers):,} righe")
elif os.path.exists("transfers.csv"):
    df_transfers = pd.read_csv("transfers.csv")
    st.sidebar.success(f"✅ `transfers.csv` (da repo): {len(df_transfers):,} righe")

# Se mancano i dati, carica il fallback informando l'utente
is_using_demo = False
if df_players is None or df_transfers is None:
    demo_p, demo_t = load_fallback()
    if df_players is None:
        df_players = demo_p
    if df_transfers is None:
        df_transfers = demo_t
    is_using_demo = True
    st.sidebar.warning("⚠️ Carica entrambi i file CSV per attivare il database completo.")

# ---------------------------------------------------------
# 4. NORMALIZZAZIONE ED ESTRAZIONE COLONNE
# ---------------------------------------------------------
col_p_name = find_column(df_players, ['name', 'player_name', 'pretty_name']) or df_players.columns[0]
col_p_dob = find_column(df_players, ['date_of_birth', 'dob', 'birth_date'])
col_p_club = find_column(df_players, ['current_club_name', 'club_name', 'squadra', 'current_club'])

col_t_name = find_column(df_transfers, ['player_name', 'name', 'player']) or df_transfers.columns[0]
col_t_from = find_column(df_transfers, ['from_club_name', 'from_club', 'from_team']) or df_transfers.columns[1]
col_t_to = find_column(df_transfers, ['to_club_name', 'to_club', 'to_team']) or df_transfers.columns[2]

# Converti le date
if col_p_dob:
    df_players['dob_clean'] = pd.to_datetime(df_players[col_p_dob], errors='coerce')
else:
    df_players['dob_clean'] = pd.NaT

# ---------------------------------------------------------
# 5. DASHBOARD PRINCIPALE
# ---------------------------------------------------------
st.title("⚽ Serie A Intelligence - Soft Stats")
today = datetime.now()
st.markdown(f"**Data di oggi:** `{today.strftime('%d/%m/%Y')}`")

if is_using_demo:
    st.info("ℹ️ **Modalità Demo Attiva:** Stai visualizzando i dati di test. Usa la barra laterale a sinistra per caricare i file CSV scaricati da Kaggle.")

st.markdown("---")

# --- SEZIONE COMPLEANNI ---
st.subheader("🎂 Compleanni di Oggi e Imminenti")

if col_p_dob:
    m = today.month
    d = today.day
    
    # Compleanni Oggi
    df_players['is_bday_today'] = (df_players['dob_clean'].dt.month == m) & (df_players['dob_clean'].dt.day == d)
    bdays_today = df_players[df_players['is_bday_today']]
    
    # Compleanni Prossimi 3 giorni
    next_3_days = [(today + timedelta(days=i)).strftime('%m-%d') for i in range(1, 4)]
    df_players['md_str'] = df_players['dob_clean'].dt.strftime('%m-%d')
    bdays_soon = df_players[df_players['md_str'].isin(next_3_days)]

    if not bdays_today.empty:
        st.write("🎉 **Compleanni di OGGI:**")
        cols = st.columns(min(len(bdays_today), 3))
        for idx, (_, p) in enumerate(bdays_today.iterrows()):
            eta = today.year - p['dob_clean'].year
            club = p[col_p_club] if col_p_club else "N/D"
            with cols[idx % 3]:
                st.success(f"🎂 **{p[col_p_name]}** ({club})\n\nCompie **{int(eta)} anni** oggi!")
    else:
        st.info("Nessun calciatore nel database compie gli anni nella data di oggi.")

    if not bdays_soon.empty:
        with st.expander("🎈 Compleanni nei prossimi 3 giorni"):
            for _, p in bdays_soon.iterrows():
                data_b = p['dob_clean'].strftime('%d/%m')
                club = p[col_p_club] if col_p_club else "N/D"
                st.write(f"- **{p[col_p_name]}** ({club}) ➔ {data_b}")
else:
    st.error("Colonna data di nascita non rilevata nel file dei giocatori.")

st.markdown("---")

# --- SEZIONE LEGGE DELL'EX ---
st.subheader("⚔️ La Legge dell'Ex - Analisi Sfida")

list_teams = sorted(list(SERIE_A_MAP.keys()))
col_c, col_t = st.columns(2)

with col_c:
    casa = st.selectbox("Squadra in CASA", list_teams, index=15) # Roma

with col_t:
    opzioni_t = [t for t in list_teams if t != casa]
    trasferta = st.selectbox("Squadra in TRASFERTA", opzioni_t, index=7) # Inter/Juventus

st.markdown(f"### Match: **{casa}** vs **{trasferta}**")

# Filtra i trasferimenti con matching flessibile
ex_casa = df_transfers[
    df_transfers[col_t_from].apply(lambda x: match_team(x, trasferta)) & 
    df_transfers[col_t_to].apply(lambda x: match_team(x, casa))
]

ex_trasferta = df_transfers[
    df_transfers[col_t_from].apply(lambda x: match_team(x, casa)) & 
    df_transfers[col_t_to].apply(lambda x: match_team(x, trasferta))
]

res_col1, res_col2 = st.columns(2)

with res_col1:
    st.markdown(f"🔰 **Ex di turno sponda {casa}** *(hanno giocato a {trasferta})*:")
    if not ex_casa.empty:
        giocatori_unici = ex_casa[col_t_name].unique()
        for g in giocatori_unici:
            st.warning(f"🔥 **{g}**")
    else:
        st.write("Nessun ex trovato.")

with res_col2:
    st.markdown(f"✈️ **Ex di turno sponda {trasferta}** *(hanno giocato a {casa})*:")
    if not ex_trasferta.empty:
        giocatori_unici = ex_trasferta[col_t_name].unique()
        for g in giocatori_unici:
            st.warning(f"🔥 **{g}**")
    else:
        st.write("Nessun ex trovato.")

st.markdown("---")

# --- SEZIONE ANTEPRIMA DATI ---
with st.expander("🔍 Anteprima e Verifica Dati Caricati"):
    st.write("### Prime 10 righe Giocatori")
    st.dataframe(df_players.head(10), use_container_width=True)
    st.write("### Prime 10 righe Trasferimenti")
    st.dataframe(df_transfers.head(10), use_container_width=True)
