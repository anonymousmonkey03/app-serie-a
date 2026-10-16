import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione della pagina
st.set_page_config(
    page_title="Serie A - Soft Stats Intelligence",
    page_icon="⚽",
    layout="wide"
)

# ---------------------------------------------------------
# 1. DATASET DI ESEMPIO (Sostituibile con i tuoi CSV)
# ---------------------------------------------------------
@st.cache_data
def load_data():
    # Anagrafica e storia giocatori
    players_data = [
        {"nome": "Paulo Dybala", "squadra": "Roma", "data_nascita": "1993-11-15", "ex_squadre": ["Juventus", "Palermo"]},
        {"nome": "Federico Chiesa", "squadra": "Liverpool", "data_nascita": "1997-10-25", "ex_squadre": ["Fiorentina", "Juventus"]},
        {"nome": "Dušan Vlahović", "squadra": "Juventus", "data_nascita": "2000-01-28", "ex_squadre": ["Fiorentina"]},
        {"nome": "Piotr Zieliński", "squadra": "Inter", "data_nascita": "1994-05-20", "ex_squadre": ["Napoli", "Empoli", "Udinese"]},
        {"nome": "Romelu Lukaku", "squadra": "Napoli", "data_nascita": "1993-05-13", "ex_squadre": ["Inter", "Roma"]},
        # Aggiungi qui un giocatore con la data di oggi per testare l'alert compleanno
        {"nome": "Giocatore Test Compleanno", "squadra": "Roma", "data_nascita": f"1998-{datetime.now().strftime('%m-%d')}", "ex_squadre": ["Lazio"]}
    ]
    
    # Partite in programma oggi
    fixtures_today = [
        {"casa": "Roma", "trasferta": "Juventus"},
        {"casa": "Inter", "trasferta": "Napoli"},
        {"casa": "Fiorentina", "trasferta": "Lazio"}
    ]
    
    df_players = pd.DataFrame(players_data)
    df_players['data_nascita'] = pd.to_datetime(df_players['data_nascita'])
    
    return df_players, fixtures_today

df_players, fixtures = load_data()

# ---------------------------------------------------------
# 2. LOGICA DI ANALISI
# ---------------------------------------------------------
today = datetime.now()
current_month_day = (today.month, today.day)

# Filtro Compleanni di Oggi
df_players['is_birthday'] = df_players['data_nascita'].apply(
    lambda x: (x.month, x.day) == current_month_day
)
birthdays_today = df_players[df_players['is_birthday']]

# Filtro Legge dell'Ex per le partite di oggi
ex_alerts = []
for fixture in fixtures:
    squadra_casa = fixture['casa']
    squadra_trasferta = fixture['trasferta']
    
    # Cerca giocatori della squadra di CASA che hanno giocato nella TRASFERTA
    ex_casa = df_players[
        (df_players['squadra'] == squadra_casa) & 
        (df_players['ex_squadre'].apply(lambda x: squadra_trasferta in x))
    ]
    for _, player in ex_casa.iterrows():
        ex_alerts.append({
            "giocatore": player['nome'],
            "squadra_attuale": squadra_casa,
            "avversario_ex": squadra_trasferta,
            "partita": f"{squadra_casa} vs {squadra_trasferta}"
        })
        
    # Cerca giocatori della squadra in TRASFERTA che hanno giocato nella CASA
    ex_trasferta = df_players[
        (df_players['squadra'] == squadra_trasferta) & 
        (df_players['ex_squadre'].apply(lambda x: squadra_casa in x))
    ]
    for _, player in ex_trasferta.iterrows():
        ex_alerts.append({
            "giocatore": player['nome'],
            "squadra_attuale": squadra_trasferta,
            "avversario_ex": squadra_casa,
            "partita": f"{squadra_casa} vs {squadra_trasferta}"
        })

# ---------------------------------------------------------
# 3. INTERFACCIA STREAMLIT
# ---------------------------------------------------------
st.title("⚽ Serie A Soft Stats Dashboard")
st.write(f"**Data di oggi:** {today.strftime('%d/%m/%Y')}")

st.markdown("---")

# Sezione 1: Partite del giorno
st.subheader("📅 Partite in programma oggi")
col_fixtures = st.columns(len(fixtures))
for idx, match in enumerate(fixtures):
    with col_fixtures[idx]:
        st.info(f"**{match['casa']}** 🆚 **{match['trasferta']}**")

st.markdown("---")

# Layout a due colonne per gli Alert
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎂 Compleanni di Oggi")
    if not birthdays_today.empty:
        for _, player in birthdays_today.iterrows():
            st.success(f"🎉 **{player['nome']}** ({player['squadra']}) compie oggi **{today.year - player['data_nascita'].year} anni**!")
    else:
        st.write("Nessun giocatore festeggia il compleanno oggi.")

with col2:
    st.subheader("⚔️ La Legge dell'Ex")
    if ex_alerts:
        for alert in ex_alerts:
            st.warning(
                f"🔥 **{alert['giocatore']}** ({alert['squadra_attuale']}) gioca oggi contro la sua ex squadra **{alert['avversario_ex']}**! \n\n"
                f"*Partita:* `{alert['partita']}`"
            )
    else:
        st.write("Nessun ex di turno identificato per le partite di oggi.")

st.markdown("---")

# Sezione 3: Tabella di ricerca rapida
with st.expander("🔍 Esplora l'intero Database Giocatori"):
    st.dataframe(df_players[['nome', 'squadra', 'data_nascita', 'ex_squadre']], use_container_width=True)
