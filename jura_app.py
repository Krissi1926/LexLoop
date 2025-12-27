import streamlit as st
import pandas as pd
import random

# === 1. Setup ===
st.set_page_config(page_title="Jura Lernapp", page_icon="§")

# Session State
if 'score' not in st.session_state: st.session_state.score = 0
if 'beantwortet' not in st.session_state: st.session_state.beantwortet = 0

# === 2. Robuste Lade-Funktion ===
def lade_daten(upload):
    try:
        # Trick: Wir lassen Python das Trennzeichen raten (sep=None)
        df = pd.read_csv(upload, sep=None, engine='python')
        
        # Wir machen alle Spaltennamen klein (Frage -> frage), damit Schreibfehler egal sind
        df.columns = [c.lower() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Fehler beim Lesen: {e}")
        return pd.DataFrame()

def naechste_karte():
    st.session_state.index += 1
    st.session_state.zeige_loesung = False
    if st.session_state.index >= len(st.session_state.lernstapel):
        st.session_state.index = 0
        random.shuffle(st.session_state.lernstapel)
        st.toast("Stapel neu gemischt!", icon="🔄")

# === 3. Seitenleiste ===
with st.sidebar:
    st.header("⚙️ Einstellungen")
    uploaded_file = st.file_uploader("📂 Fragen hochladen", type="csv")
    datei = uploaded_file if uploaded_file else "fragen.csv"
    
    df_alle = lade_daten(datei)
    
    if df_alle.empty:
        st.warning("Warte auf Datei...")
        st.stop()
        
    # Filter-Logik (Robust)
    # Wir schauen, ob irgendeine Spalte so ähnlich wie "fach" oder "gebiet" heißt
    fach_col = None
    for col in df_alle.columns:
        if "fach" in col or "gebiet" in col:
            fach_col = col
            break
            
    if fach_col:
        faecher = list(df_alle[fach_col].unique())
        auswahl = st.multiselect("📚 Fach auswählen:", faecher, default=faecher)
        df_gefiltert = df_alle[df_alle[fach_col].isin(auswahl)]
    else:
        st.info("Keine Spalte 'fach' gefunden - zeige alle Fragen.")
        df_gefiltert = df_alle

    # Score Reset
    st.write("---")
    if st.button("🗑️ Score Reset"):
        st.session_state.score = 0
        st.session_state.beantwortet = 0
        st.rerun()

# === 4. Hauptteil ===
st.title("§ Jura-Trainer")

karten_liste = df_gefiltert.to_dict('records')

if not karten_liste:
    st.error("Keine Karten in der Auswahl.")
    st.stop()

# Initialisierung bei Änderungen
if 'letzte_karten_anzahl' not in st.session_state or st.session_state.letzte_karten_anzahl != len(karten_liste):
    random.shuffle(karten_liste)
    st.session_state.lernstapel = karten_liste
    st.session_state.index = 0
    st.session_state.zeige_loesung = False
    st.session_state.letzte_karten_anzahl = len(karten_liste)

# Karte holen
karte = st.session_state.lernstapel[st.session_state.index]

# Fortschritt
st.progress((st.session_state.index) / len(st.session_state.lernstapel))

# Anzeige
with st.container(border=True):
    # Falls Spaltennamen komisch sind, suchen wir die passenden
    frage_key = next((k for k in karte.keys() if 'frag' in k), None)
    antwort_key = next((k for k in karte.keys() if 'antw' in k), None)
    
    if not frage_key or not antwort_key:
        st.error(f"Konnte Spalten 'frage' und 'antwort' nicht finden. Deine Spalten heißen: {list(karte.keys())}")
        st.stop()

    st.markdown(f"### {karte[frage_key]}")
    st.write("")

    if not st.session_state.zeige_loesung:
        if st.button("Lösung anzeigen 👁️", use_container_width=True):
            st.session_state.zeige_loesung = True
            st.rerun()
    else:
        st.info(f"💡 {karte[antwort_key]}")
        st.write("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("❌ Wiederholen", use_container_width=True):
                naechste_karte()
                st.rerun()
        with c2:
            if st.button("✅ Gewusst", type="primary", use_container_width=True):
                st.session_state.score += 1
                st.session_state.beantwortet += 1
                naechste_karte()
                st.rerun()
