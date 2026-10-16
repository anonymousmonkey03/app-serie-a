import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
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
# 2. FUNZIONI UTILI & MAPPATURA COMPLEANNI
# ---------------------------------------------------------
def find_column(df, candidates):
    for c in df.columns:
        if c.lower().strip() in candidates:
            return c
    return None

def match_team(team_str, target_key):
    if pd.isna(team_str):
        return False
    team_clean = str(team_str).lower()
    keywords = SERIE_A_MAP.get(target_key, [target_key.lower()])
    return any(kw in team_clean for kw in keywords)

def get_next_birthday_info(dob, today_date):
    """Calcola tra quanti giorni cade il prossimo compleanno."""
    if pd.isna(dob):
        return 999, "N/D", "⚪ Sconosciuto"
    
    try:
        bday_this_year = date(today_date.year, dob.month, dob.day)
    except ValueError:  # Gestione 29 Febbraio negli anni non bisestili
        bday_this_year = date(today_date.year, 3, 1)
        
    if bday_this_year < today_date:
        try:
            bday_next = date(today_date.year + 1, dob.month, dob.day)
        except ValueError:
            bday_next = date(today_date.year + 1, 3, 1)
        days_left = (bday_next - today_date).days
        next_bday_date = bday_next
    else:
        days_left = (bday_this_year - today_date).days
        next_bday_date = bday_this_year
        
    # Assegnazione Stato e Colore
    if days_left == 0:
        status = "🟢 OGGI!"
    elif 1 <= days_left <= 7:
        status = f"🟡 Tra {days_left} giorni (Questa Settimana)"
    elif 8 <= days_left <= 30:
        status = f"🔵 Tra {days_left} giorni (Questo Mese)"
    else:
        status = f"⚪ Tra {days_left} giorni"
        
    return days_left, next_bday_date.strftime("%d/%m"), status

@st.cache_data
def load_fallback():
    p_data = [
        {"name": "Paulo Dybala", "current_club_name": "AS Roma", "date_of_birth": "1993-11-15"},
        {"name": "Lorenzo Pellegrini", "current_club_name": "AS Roma", "date_of_birth": "1996-06-19"},
        {"name": "Gianluca Mancini", "current_club_name": "AS Roma", "date_of_birth": "1996-04-17"},
        {"name": "Giocatore Festeggiato", "current_club_name": "AS Roma", "date_of_birth": datetime.now().strftime('%Y-%m-%d')},
        {"name": "Giocatore Prossimo", "current_club_name": "AS Roma", "date_of_birth": (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')},
        {"name": "Dušan Vlahović", "current_club_name": "Juventus FC", "date_of_birth": "2000-01-28"},
        {"name": "Piotr Zieliński", "current_club_name": "FC Internazionale", "date_of_birth": "1994-05-20"},
        {"name": "Romelu Lukaku", "current_club_name": "SSC Napoli", "date_of_birth": "1993-05-13"}
    ]
    t_data = [
        {"player_name": "Paulo Dybala", "from_club_name": "Juventus FC", "to_club_name": "AS Roma"},
        {"player_name": "Gianluca Mancini", "from_club_name": "Atalanta BC", "to_club_name": "AS Roma"},
        {"player_name": "Dušan Vlahović", "from_club_name": "ACF Fiorentina", "to_club_name": "Juventus FC"},
        {"player_name": "Piotr Zieliński", "from_club_name": "SSC Napoli", "to_club_name": "FC Internazionale"},
        {"player_name": "Romelu Lukaku", "from_club_name": "FC Internazionale", "to_club_name": "SSC Napoli"}
    ]
    return pd.DataFrame(p_data), pd.DataFrame(t_data)

# ---------------------------------------------------------
# 3. SIDEBAR & CARICAMENTO DATI
# ---------------------------------------------------------
st.sidebar.title("📁 Database & Filtri")

up_players = st.sidebar.file_uploader("Carica players.csv", type=["csv"])
up_transfers = st.sidebar.file_uploader("Carica transfers.csv", type=["csv"])

df_players, df_transfers = None, None

if up_players is not None:
    df_players = pd.read_csv(up_players)
elif os.path.exists("players.csv"):
    df_players = pd.read_csv("players.csv")

if up_transfers is not None:
    df_transfers = pd.read_csv(up_transfers)
elif os.path.exists("transfers.csv"):
    df_transfers = pd.read_csv("transfers.csv")

is_demo = False
if df_players is None or df_transfers is None:
    demo_p, demo_t = load_fallback()
    df_players = demo_p if df_players is None else df_players
    df_transfers = demo_t if df_transfers is None else df_transfers
    is_demo = True

# Nomi colonne
col_p_name = find_column(df_players, ['name', 'player_name', 'pretty_name']) or df_players.columns[0]
col_p_dob = find_column(df_players, ['date_of_birth', 'dob', 'birth_date'])
col_p_club = find_column(df_players, ['current_club_name', 'club_name', 'squadra', 'current_club'])

col_t_name = find_column(df_transfers, ['player_name', 'name', 'player']) or df_transfers.columns[0]
col_t_from = find_column(df_transfers, ['from_club_name', 'from_club', 'from_team']) or df_transfers.columns[1]
col_t_to = find_column(df_transfers, ['to_club_name', 'to_club', 'to_team']) or df_transfers.columns[2]

df_players['dob_clean'] = pd.to_datetime(df_players[col_p_dob], errors='coerce')

# ---------------------------------------------------------
# 4. DASHBOARD INTERATTIVA CON TAB
# ---------------------------------------------------------
st.title("⚽ Serie A Intelligence Hub")
today_dt = datetime.now().date()
st.caption(f"📅 Data di oggi: **{today_dt.strftime('%d/%m/%Y')}**")

if is_demo:
    st.info("ℹ️ **Modalità Demo Attiva:** Carica i file CSV completi nella barra laterale a sinistra per analizzare tutti i giocatori reali.")

# Creazione delle Schede Interattive
tab_squadra, tab_giornaliera, tab_scontri = st.tabs([
    "🛡️ Analisi Squadra & Compleanni", 
    "📊 Panoramica Oggi", 
    "⚔️ Confronto Matchup Ex"
])

# =========================================================
# TAB 1: ANALISI DETTAGLIATA SQUADRA (La nuova feature!)
# =========================================================
with tab_squadra:
    st.subheader("🔎 Seleziona una Squadra di Serie A")
    
    selected_team = st.selectbox(
        "Scegli la squadra da analizzare:", 
        sorted(list(SERIE_A_MAP.keys())), 
        index=15 # Default: Roma
    )
    
    # Filtra la rosa della squadra selezionata
    roster = df_players[df_players[col_p_club].apply(lambda x: match_team(x, selected_team))].copy()
    
    if not roster.empty:
        # Calcola le info per ogni giocatore
        res_list = []
        for _, p in roster.iterrows():
            dob = p['dob_clean']
            days_left, bday_str, status = get_next_birthday_info(dob, today_dt)
            eta = (today_dt.year - dob.year) if pd.notna(dob) else "N/D"
            
            res_list.append({
                "Giocatore": p[col_p_name],
                "Età": eta,
                "Data Compleanno": bday_str,
                "Giorni Mancanti": days_left,
                "Stato Compleanno": status
            })
            
        df_roster_analysis = pd.DataFrame(res_list).sort_values("Giorni Mancanti")
        
        # KPI Card della Rosa
        c1, c2, c3 = st.columns(3)
        num_oggi = len(df_roster_analysis[df_roster_analysis['Giorni Mancanti'] == 0])
        num_settimana = len(df_roster_analysis[(df_roster_analysis['Giorni Mancanti'] > 0) & (df_roster_analysis['Giorni Mancanti'] <= 7)])
        
        c1.metric("👥 Totale Rosa", len(roster))
        c2.metric("🟢 Compleanni Oggi", num_oggi)
        c3.metric("🟡 Compleanni Questa Settimana", num_settimana)
        
        st.markdown("---")
        st.write(f"### 📋 Rosa **{selected_team}** - Calendario Compleanni Ordinato")
        
        # Evidenziazione Visiva nelle Card
        for _, row in df_roster_analysis.iterrows():
            st_col1, st_col2, st_col3 = st.columns([2, 1, 2])
            
            with st_col1:
                st.write(f"**{row['Giocatore']}** ({row['Età']} anni)")
            with st_col2:
                st.write(f"📅 `{row['Data Compleanno']}`")
            with st_col3:
                if row['Giorni Mancanti'] == 0:
                    st.success(row['Stato Compleanno'])
                elif row['Giorni Mancanti'] <= 7:
                    st.warning(row['Stato Compleanno'])
                elif row['Giorni Mancanti'] <= 30:
                    st.info(row['Stato Compleanno'])
                else:
                    st.write(row['Stato Compleanno'])
                    
    else:
        st.warning(f"Nessun giocatore trovato in rosa per {selected_team}. Assicurati che i file CSV siano caricati correttamente.")

# =========================================================
# TAB 2: PANORAMICA GIORNALIERA
# =========================================================
with tab_giornaliera:
    st.subheader("🎂 Compleanni Generali di Oggi in Serie A")
    
    m, d = today_dt.month, today_dt.day
    df_players['is_today'] = (df_players['dob_clean'].dt.month == m) & (df_players['dob_clean'].dt.day == d)
    bday_today_all = df_players[df_players['is_today']]
    
    if not bday_today_all.empty:
        for _, p in bday_today_all.iterrows():
            club = p[col_p_club] if col_p_club else "N/D"
            eta = today_dt.year - p['dob_clean'].year
            st.success(f"🎉 **{p[col_p_name]}** ({club}) compie **{eta} anni** oggi!")
    else:
        st.info("Nessun festeggiato oggi tra i dati registrati.")

# =========================================================
# TAB 3: CONFRONTO MATCHUP ED EX
# =========================================================
with tab_scontri:
    st.subheader("⚔️ Analisi Scontro Diretto (Ex di Turno)")
    
    col1, col2 = st.columns(2)
    with col1:
        team_a = st.selectbox("Squadra Casa", sorted(list(SERIE_A_MAP.keys())), index=15)
    with col2:
        team_b = st.selectbox("Squadra Trasferta", [t for t in sorted(list(SERIE_A_MAP.keys())) if t != team_a], index=7)
        
    ex_a = df_transfers[
        df_transfers[col_t_from].apply(lambda x: match_team(x, team_b)) & 
        df_transfers[col_t_to].apply(lambda x: match_team(x, team_a))
    ]
    
    ex_b = df_transfers[
        df_transfers[col_t_from].apply(lambda x: match_team(x, team_a)) & 
        df_transfers[col_t_to].apply(lambda x: match_team(x, team_b))
    ]
    
    ca, cb = st.columns(2)
    with ca:
        st.write(f"🔰 **Ex in rosa a {team_a}** (passati da {team_b}):")
        if not ex_a.empty:
            for g in ex_a[col_t_name].unique():
                st.warning(f"🔥 **{g}**")
        else:
            st.write("Nessuno")
            
    with cb:
        st.write(f"✈️ **Ex in rosa a {team_b}** (passati da {team_a}):")
        if not ex_b.empty:
            for g in ex_b[col_t_name].unique():
                st.warning(f"🔥 **{g}**")
        else:
            st.write("Nessuno")
