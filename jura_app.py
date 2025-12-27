import streamlit as st
import pandas as pd
import random # <--- Das ist unser Zufalls-Helfer

# === 1. Setup & Design ===
st.set_page_config(page_title="Jura Lernapp", page_icon="§")
st.title("§ Meine Jura-App")

# === 2. Funktion zum Laden und Mischen ===
def lade_daten(datei_pfad_oder_upload):
    try:
        df = pd.read_csv(datei_pfad_oder_upload, sep=";")
        karten_liste = df.to_dict('records')
        # Hier passiert die Magie: Wir mischen die Liste zufällig!
        random.shuffle(karten_liste)
        return karten_liste
    except Exception as e:
        return None

# === 3. Seitenleiste ===
with st.sidebar:
    st.header("Einstellungen")
    uploaded_file = st.file_uploader("📂 Eigene Fragen hochladen", type="csv")
    
    # Button zum Neu-Mischen
    if st.button("🔄 Karten neu mischen"):
        # Wir löschen den aktuellen Stapel, damit er unten neu geladen wird
        if 'lernstapel' in st.session_state:
            del st.session_state['lernstapel']
        if 'index' in st.session_state:
            st.session_state.index = 0
        st.rerun()

# === 4. Logik: Daten verwalten ===

# Wir prüfen: Haben wir schon einen gemischten Stapel im Gedächtnis?
if 'lernstapel' not in st.session_state:
    # Nein? Dann müssen wir laden und mischen.
    
    if uploaded_file is not None:
        # A) Aus Upload
        neue_karten = lade_daten(uploaded_file)
    else:
        # B) Aus Standard-Datei
        neue_karten = lade_daten("fragen.csv")

    if neue_karten:
        st.session_state.lernstapel = neue_karten
        st.session_state.index = 0 # Immer bei Frage 1 starten
        st.session_state.zeige_loesung = False
        # Kleiner Hinweis für dich
        st.toast("Karten wurden neu gemischt!")
    else:
        st.error("Konnte keine Fragen laden. Prüfe deine CSV-Datei!")
        st.stop()

# Ab hier arbeiten wir nur noch mit dem gemischten Stapel aus dem Speicher
karteikarten = st.session_state.lernstapel

# Sicherheitscheck (falls Stapel leer ist)
if not karteikarten:
    st.warning("Keine Karten vorhanden.")
    st.stop()

# Aktuelle Karte holen
aktuelle_karte = karteikarten[st.session_state.index]

# Fortschrittsanzeige
st.progress((st.session_state.index + 1) / len(karteikarten))
st.caption(f"Frage {st.session_state.index + 1} von {len(karteikarten)}")

# === 5. Anzeige der Karte ===
container = st.container(border=True)
with container:
    frage_text = aktuelle_karte.get("frage", "Frage fehlt")
    antwort_text = aktuelle_karte.get("antwort", "Antwort fehlt")

    st.markdown(f"### ❓ {frage_text}")
    st.write("") 
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Lösung anzeigen", use_container_width=True):
            st.session_state.zeige_loesung = True
            
    with col2:
        if st.button("Nächste Frage ➡️", type="primary", use_container_width=True):
            if st.session_state.index < len(karteikarten) - 1:
                st.session_state.index += 1
            else:
                st.session_state.index = 0
                st.balloons()
                st.toast("Durchgang beendet! Wir mischen neu...")
                random.shuffle(st.session_state.lernstapel) # Am Ende automatisch neu mischen
            
            st.session_state.zeige_loesung = False
            st.rerun()

    if st.session_state.zeige_loesung:
        st.divider()
        st.info(f"💡 **Antwort:** {antwort_text}")