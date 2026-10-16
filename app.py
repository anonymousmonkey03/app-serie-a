import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Serie A - Soft Stats", page_icon="⚽", layout="wide")

@st.cache_data
def load_real_data():
    # Legge i dati caricati nel repository
    players = pd.read_csv('players.csv')
    transfers = pd.read_csv('transfers.csv')
    
    # Seleziona solo i giocatori di Serie A (competizione 'IT1')
    # o filtra per le squadre di Serie A
    serie_a_clubs = [
        "Inter", "AC Milan", "Juventus FC", "SS Lazio", "AS Roma", 
        "SSC Napoli", "Atalanta BC", "ACF Fiorentina", "Bologna FC 1909",
        "Torino FC", "Udinese Calcio", "Genoa CFC", "AC Monza",
        "Hellas Verona", "Cagliari Calcio", "Empoli FC", "Parma Calcio 1913",
        "Como 1907", "Venezia FC", "US Lecce"
    ]
    
    players['date_of_birth'] = pd.to_datetime(players['date_of_birth'], errors='coerce')
    
    return players, transfers, serie_a_clubs

players_df, transfers_df, serie_a_clubs = load_real_data()

st.title("⚽ Serie A - Compleanni ed Ex di Turno")
today = datetime.now()
st.write(f"**Data di oggi:** {today.strftime('%d/%m/%Y')}")

# --- 1. SEZIONE COMPLEANNI ---
st.subheader("🎂 Compleanni di Oggi")
today_month = today.month
today_day = today.day

birthdays = players_df[
    (players_df['date_of_birth'].dt.month == today_month) & 
    (players_df['date_of_birth'].dt.day == today_day)
]

if not birthdays.empty:
    for _, player in birthdays.iterrows():
        eta = today.year - player['date_of_birth'].year
        st.success(f"🎉 **{player['name']}** compie oggi **{eta} anni**!")
else:
    st.info("Nessun giocatore festeggia il compleanno oggi.")

# --- 2. SEZIONE PARTITE DEL GIORNO ---
st.subheader("📅 Seleziona la Partita di Oggi")
squadra_casa = st.selectbox("Squadra in Casa", serie_a_clubs, index=0)
squadra_trasferta = st.selectbox("Squadra in Trasferta", serie_a_clubs, index=1)

if squadra_casa and squadra_trasferta:
    st.markdown(f"### Analisi: **{squadra_casa}** vs **{squadra_trasferta}**")
    
    # Cerca ex tra le trasferte
    # Un ex è un giocatore la cui squadra attuale è 'squadra_casa' e in passato ha giocato per 'squadra_trasferta'
    ex_giocatori = transfers_df[
        (transfers_df['from_club_name'] == squadra_trasferta) & 
        (transfers_df['to_club_name'] == squadra_casa)
    ]
    
    if not ex_giocatori.empty:
        st.warning(f"🔥 Trovati **{len(ex_giocatori)} ex giocatori** per questa sfida!")
        for _, ex in ex_giocatori.iterrows():
            st.write(f"- **{ex['player_name']}**: passato da {squadra_trasferta} a {squadra_casa}")
    else:
        st.write("Nessun ex di turno rilevato tra queste due squadre.")
