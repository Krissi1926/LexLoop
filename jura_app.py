import streamlit as st
import pandas as pd
import random

# === 1. Setup ===
st.set_page_config(page_title="Jura Lernapp", page_icon="§")

# Session State Initialisierung (Variablen fürs Gedächtnis)
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'beantwortet' not in st.session_state:
    st.session_state.beantwortet = 0

# === 2. Funktionen ===
def lade_daten(upload):
    try:
        df = pd.read_csv(upload, sep=";")
        return df.to_dict('records')
    except:
        return []

def naechste_karte():
    st.session_state.index += 1
    st.session_state.zeige_loesung = False
    # Wenn wir am Ende sind, mischen wir neu
    if st.session_state.index >= len(st.session_state.lernstapel):
        st.session_state.index = 0
        random.shuffle(st.session_state.lernstapel)
        st.toast("Stapel durch! Wir fangen von vorne an.")

# === 3. Seitenleiste ===
with st.sidebar:
    st.header("📊 Dein Status")
    # Score Anzeige
    if st.session_state.beantwortet > 0:
        quote = (st.session_state.score / st.session_state.beantwortet) * 100
        st.metric("Erfolgsquote", f"{int(quote)}%", f"{st.session_state.score} von {st.session_state.beantwortet}")
    else:
        st.write("Noch keine Fragen beantwortet.")
    
    st.write("---")
    uploaded_file = st.file_uploader("📂 Fragen hochladen", type="csv")
    if st.button("🔄 Reset & Neu mischen"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

# === 4. Hauptlogik ===
st.title("§ Jura-Trainer")

# Laden & Mischen (nur beim ersten Start)
if 'lernstapel' not in st.session_state:
    datei = uploaded_file if uploaded_file else "fragen.csv"
    daten = lade_daten(datei)
    
    if not daten:
        st.warning("Bitte lade eine 'fragen.csv' hoch!")
        st.stop()
        
    random.shuffle(daten)
    st.session_state.lernstapel = daten
    st.session_state.index = 0
    st.session_state.zeige_loesung = False

# Karte holen
karte = st.session_state.lernstapel[st.session_state.index]

# Fortschrittsbalken
fortschritt = (st.session_state.index) / len(st.session_state.lernstapel)
st.progress(fortschritt)

# Container für die Karte
with st.container(border=True):
    st.subheader(f"Frage {st.session_state.index + 1}:")
    st.markdown(f"### {karte.get('frage', 'Fehler')}")
    st.write("")

    if not st.session_state.zeige_loesung:
        if st.button("Lösung anzeigen 👁️", use_container_width=True):
            st.session_state.zeige_loesung = True
            st.rerun()
    else:
        st.info(f"💡 **Antwort:** {karte.get('antwort', 'Fehler')}")
        st.write("---")
        st.write("**Wusstest du es?**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("❌ Nein (Wiederholen)", use_container_width=True):
                st.session_state.beantwortet += 1
                naechste_karte()
                st.rerun()
        with col2:
            if st.button("✅ Ja (Gewusst)", type="primary", use_container_width=True):
                st.session_state.score += 1
                st.session_state.beantwortet += 1
                st.balloons()
                naechste_karte()
                st.rerun()
