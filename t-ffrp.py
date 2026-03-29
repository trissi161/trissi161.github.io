import streamlit as st
import pandas as pd
from datetime import datetime

# --- KONFIGURATION ---
st.set_page_config(page_title="RDF Team-Panel", page_icon="📝", layout="wide")

# Deine ID und Links (Basierend auf deinem erfolgreichen Test)
SHEET_ID = "1TZHjV7RTrE27p-hapfMe11eCUXhS9QFAd53OCQjpeOc"
URL_P = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=P"
URL_B = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=B"

# --- FUNKTIONEN ---
def load_data(url):
    try:
        # Erwingt das Neuladen durch einen Zeitstempel-Parameter (verhindert Cache-Probleme)
        return pd.read_csv(f"{url}&cachebust={datetime.now().timestamp()}")
    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")
        return pd.DataFrame()

# --- DATEN LADEN ---
df_personal = load_data(URL_P)

# Personal-Liste für Dropdown vorbereiten
if not df_personal.empty and "Name" in df_personal.columns:
    team_liste = df_personal["Name"].dropna().tolist()
else:
    team_liste = ["Liste konnte nicht geladen werden"]

# --- TABS ---
tab_bericht, tab_admin = st.tabs(["📝 Support-Bericht", "🔒 Admin-Bereich"])

# ==========================================
# 1. TAB: SUPPORT-BERICHT
# ==========================================
with tab_bericht:
    st.header("Support-Bericht einreichen")
    
    with st.form("support_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.selectbox("Dein Name (Teammitglied)", team_liste)
            spieler = st.text_input("Betroffene:r Spieler:in")
            beteiligte = st.text_area("Beteiligte Teammitglieder")
        with c2:
            problem = st.text_area("Geschildertes Problem")
            massnahmen = st.text_area("Durchgeführte Maßnahmen")
            begruendung = st.text_area("Begründung")
        
        clips = st.text_area("Clips / Fotos / Beweise (Links & Beschreibung)")
        
        submit = st.form_submit_button("Bericht absenden")
        
        if submit:
            if spieler and problem:
                # Da das Schreiben über CSV-Links nicht geht, nutzen wir hier 
                # wieder die GSheets Verbindung NUR für den Schreibbefehl.
                from streamlit_gsheets import GSheetsConnection
                try:
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    
                    neuer_eintrag = pd.DataFrame([{
                        "Zeitpunkt": datetime.now().strftime("%d.%m.%Y %H:%M"),
                        "Ersteller": name,
                        "Spieler": spieler,
                        "Beteiligte": beteiligte,
                        "Problem": problem,
                        "Massnahmen": massnahmen,
                        "Begruendung": begruendung,
                        "Beweise": clips
                    }])
                    
                    # Bestehende Berichte laden (zum Anhängen)
                    df_berichte_alt = load_data(URL_B)
                    df_gesamt = pd.concat([df_berichte_alt, neuer_eintrag], ignore_index=True)
                    
                    # Speichern
                    conn.update(worksheet="B", data=df_gesamt)
                    st.success("✅ Bericht erfolgreich in Datenbank gespeichert!")
                except Exception as e:
                    st.error(f"Schreibfehler: {e}. Prüfe, ob das Blatt in Google Sheets wirklich 'B' heißt!")
            else:
                st.warning("Bitte fülle mindestens 'Spieler' und 'Problem' aus.")

# ==========================================
# 2. TAB: ADMIN-BEREICH
# ==========================================
with tab_admin:
    st.header("Admin-Verwaltung")
    pw = st.text_input("Passwort", type="password")
    
    if pw == "2504":
        admin_wahl = st.radio("Ansicht:", ["Berichte einsehen", "Personal verwalten"], horizontal=True)
        
        if admin_wahl == "Berichte einsehen":
            df_b = load_data(URL_B)
            st.dataframe(df_b.iloc[::-1], use_container_width=True) # Neueste oben
            
        elif admin_wahl == "Personal verwalten":
            st.info("Hier kannst du Namen, Ränge und Verwarnungen ändern.")
            # Editor für die Personal-Tabelle
            edited_df = st.data_editor(df_personal, num_rows="dynamic", use_container_width=True)
            
            if st.button("Personal-Änderungen speichern"):
                from streamlit_gsheets import GSheetsConnection
                try:
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    conn.update(worksheet="P", data=edited_df)
                    st.success("✅ Personal-Datenbank aktualisiert!")
                    st.rerun() # Seite neu laden, damit Dropdown aktuell ist
                except Exception as e:
                    st.error(f"Fehler beim Speichern: {e}")
    elif pw != "":
        st.error("Falsches Passwort")
