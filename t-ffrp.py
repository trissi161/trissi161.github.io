import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- KONFIGURATION ---
st.set_page_config(page_title="RDF Team-Panel", page_icon="📝", layout="wide")

# DEINE TABELLEN-URL (Die ID aus deinem Link)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1TZHjV7RTrE27p-hapfMe11eCUXhS9QFAd53OCQjpeOc"

# Verbindung herstellen
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Verbindung fehlgeschlagen: {e}")

# Funktion zum Laden (jetzt mit direkter URL-Übergabe)
def load_data(sheet_name):
    try:
        # Wir übergeben die URL hier JEDES MAL direkt mit
        return conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
    except Exception as e:
        st.error(f"⚠️ Fehler beim Zugriff auf Blatt '{sheet_name}': {e}")
        return pd.DataFrame()

# --- DATEN LADEN ---
df_personal = load_data("P")
df_berichte = load_data("B")

# Fallback für die Namensliste
if not df_personal.empty and "Name" in df_personal.columns:
    team_liste = df_personal["Name"].dropna().tolist()
else:
    team_liste = ["Kein Personal gefunden (Check Blatt 'P')"]

# --- TABS ---
tab_bericht, tab_admin = st.tabs(["📝 Support-Bericht", "🔒 Admin-Bereich"])

with tab_bericht:
    st.header("Support-Bericht erstellen")
    
    with st.form("support_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            dein_name = st.selectbox("Dein Name", team_liste)
            spieler = st.text_input("Betroffener Spieler")
            mitglieder = st.text_area("Weitere Beteiligte")
        with col2:
            problem = st.text_area("Problem")
            massnahmen = st.text_area("Maßnahmen")
            begruendung = st.text_area("Begründung")
        
        clips = st.text_area("Clips/Beweise")
        
        if st.form_submit_button("Bericht absenden"):
            if spieler and problem:
                neuer_eintrag = pd.DataFrame([{
                    "Zeitpunkt": datetime.now().strftime("%d.%m.%Y %H:%M"),
                    "Ersteller": dein_name,
                    "Spieler": spieler,
                    "Beteiligte": mitglieder,
                    "Problem": problem,
                    "Massnahmen": massnahmen,
                    "Begruendung": begruendung,
                    "Beweise": clips
                }])
                
                try:
                    # WICHTIG: Hier laden wir "B" neu und speichern zurück
                    df_alt = load_data("B")
                    df_neu = pd.concat([df_alt, neuer_eintrag], ignore_index=True)
                    conn.update(spreadsheet=SHEET_URL, worksheet="B", data=df_neu)
                    st.success("✅ Gespeichert!")
                except Exception as e:
                    st.error(f"Fehler: {e}")

with tab_admin:
    pw = st.text_input("Admin-Passwort", type="password")
    if pw == "2504":
        wahl = st.radio("Bereich:", ["Berichte", "Personal"], horizontal=True)
        
        if wahl == "Berichte":
            st.dataframe(load_data("B"), use_container_width=True)
        else:
            df_p = load_data("P")
            edited = st.data_editor(df_p, num_rows="dynamic", use_container_width=True)
            if st.button("Personal speichern"):
                conn.update(spreadsheet=SHEET_URL, worksheet="P", data=edited)
                st.success("Aktualisiert!")
