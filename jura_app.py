import streamlit as st
import pandas as pd
import random

# === 1. Setup ===
st.set_page_config(page_title="Jura Lernapp", page_icon="§")

if 'score' not in st.session_state:
    st.session_state.score = 0
if 'beantwortet' not in st.session_state:
    st.session_state.beantwortet = 0

# === 2. Funktionen ===
def lade_daten(upload):
    try:
        # Wir lesen jetzt auch die Spalte 'fach' mit aus (falls vorhanden)
        df = pd.read_csv(upload, sep=";")
        return df
    except:
        return pd.DataFrame() # Leere Tabelle zurückgeben bei Fehler

def naechste_karte():
    st.session_state.index += 1
    st.session_state.zeige_loesung = False
    
    # Wenn wir am Ende des aktuellen Stapels sind
    if st.session_state.index >= len(st.session_state.lernstapel):
        st.session_state.index = 0
        random.shuffle(st.session_state.lernstapel)
        st.toast("Alle Karten dieses Fachs gelernt! Von vorne...", icon="🔄")

# === 3. Seitenleiste & Filter ===
with st.sidebar:
    st.header("⚙️ Einstellungen")
    
    # Datei Logik
    uploaded_file = st.file_uploader("📂 Fragen hochladen", type="csv")
    datei = uploaded_file if uploaded_file else "fragen.csv"
    
    # Daten laden (als Tabelle/DataFrame)
    df_alle = lade_daten(datei)
    
    if df_alle.empty:
        st.error("Keine Daten gefunden. Bitte CSV prüfen.")
        st.stop()
    
    # --- DER NEUE FILTER ---
    # Wir schauen, ob es eine Spalte "fach" gibt
    if 'fach' in df_alle.columns:
        # Wir suchen alle einzigartigen Fächer (z.B. Strafrecht, Zivilrecht)
        verfuegbare_faecher = list(df_alle['fach'].unique())
        # Wir fügen eine Option "Alle" hinzu
        auswahl = st.multiselect("📚 Fach auswählen:", verfuegbare_faecher, default=verfuegbare_faecher)
        
        # Wir filtern die Tabelle: Nur Zeilen behalten, wo das Fach in der Auswahl ist
        df_gefiltert = df_alle[df_alle['fach'].isin(auswahl)]
    else:
        st.info("Tipp: Füge eine Spalte 'fach' in deine CSV ein, um zu filtern!")
        df_gefiltert = df_alle

    # Score
    st.write("---")
    st.subheader("📊 Statistik")
    if st.session_state.beantwortet > 0:
        quote = (st.session_state.score / st.session_state.beantwortet) * 100
        st.metric("Quote", f"{int(quote)}%", f"{st.session_state.score} / {st.session_state.beantwortet} richtig")
    
    if st.button("🗑️ Reset Score"):
        st.session_state.score = 0
        st.session_state.beantwortet = 0
        st.rerun()

# === 4. Hauptlogik ===
st.title("§ Jura-Trainer")

# Wenn wir den Filter ändern, müssen wir den Lernstapel neu bauen
# Wir machen das, indem wir prüfen, ob wir überhaupt Karten haben
karten_liste = df_gefiltert.to_dict('records')

if not karten_liste:
    st.warning("Keine Karten für diese Auswahl gefunden!")
    st.stop()

# Initialisierung oder Reset bei Filterwechsel
# (Wir merken uns einfach die Länge der Liste, um Änderungen zu erkennen)
if 'letzte_karten_anzahl' not in st.session_state or st.session_state.letzte_karten_anzahl != len(karten_liste):
    random.shuffle(karten_liste)
    st.session_state.lernstapel = karten_liste
    st.session_state.index = 0
    st.session_state.zeige_loesung = False
    st.session_state.letzte_karten_anzahl = len(karten_liste)

# Karte holen
karte = st.session_state.lernstapel[st.session_state.index]

# Fortschritt
fortschritt = (st.session_state.index) / len(st.session_state.lernstapel)
st.progress(fortschritt)

# Fach Badge anzeigen (falls vorhanden)
if 'fach' in karte:
    st.caption(f"Fachgebiet: {karte['fach']}")

# Karte anzeigen
with st.container(border=True):
    st.markdown(f"### {karte.get('frage', 'Fehler')}")
    st.write("")

    if not st.session_state.zeige_loesung:
        if st.button("Lösung anzeigen 👁️", use_container_width=True):
            st.session_state.zeige_loesung = True
            st.rerun()
    else:
        st.info(f"💡 **Antwort:** {karte.get('antwort', 'Fehler')}")
        st.write("---")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("❌ Wiederholen", use_container_width=True):
                st.session_state.beantwortet += 1
                naechste_karte()
                st.rerun()
        with c2:
            if st.button("✅ Gewusst", type="primary", use_container_width=True):
                st.session_state.score += 1
                st.session_state.beantwortet += 1
                naechste_karte()
                st.rerun()
