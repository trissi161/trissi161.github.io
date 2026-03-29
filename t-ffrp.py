import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- SEITEN-KONFIGURATION ---
st.set_page_config(page_title="RDF Team-Panel", page_icon="📝", layout="wide")

# Verbindung zu Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Verbindung zu Google Sheets fehlgeschlagen. Prüfe deine Secrets!")

# --- DATEN LADEN ---
def load_data(sheet_name):
    # ttl="0" sorgt dafür, dass die Daten bei jedem Laden frisch aus Google Sheets kommen
    return conn.read(worksheet=sheet_name, ttl="0")

# --- NAVIGATION (TABS) ---
tab_bericht, tab_admin = st.tabs(["📝 Support-Bericht", "🔒 Admin-Bereich"])

# ==========================================
# 1. TAB: SUPPORT-BERICHT
# ==========================================
with tab_bericht:
    st.header("Neuen Support-Bericht erstellen")
    st.info("Bitte fülle alle Felder wahrheitsgemäß aus. Der Bericht wird direkt in die Datenbank übertragen.")

    # Mitarbeiterliste laden für das Auswahlmenü
    try:
        df_personal = load_data("Personal")
        team_liste = df_personal["Name"].tolist()
    except:
        team_liste = ["Fehler: Personal-Liste nicht gefunden"]

    with st.form("support_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Beteiligte")
            dein_name = st.selectbox("Dein Name (Ersteller)", team_liste)
            betroffener_spieler = st.text_input("Betroffene:r Spieler:in (Name/ID)")
            beteiligte_mitglieder = st.text_area("Weitere beteiligte Teammitglieder")

        with col2:
            st.subheader("Details")
            problem = st.text_area("Geschildertes Problem der/des Spieler:in")
            massnahmen = st.text_area("Durchgeführte Maßnahmen")
            begruendung = st.text_area("Begründung für diese Maßnahmen")
        
        st.divider()
        clips = st.text_area("Vorhandene Clips/Fotos (Links & kurze Beschreibung)")
        
        submit = st.form_submit_button("Bericht absenden")

        if submit:
            if betroffener_spieler and problem:
                # Daten für Google Sheets vorbereiten
                neuer_eintrag = pd.DataFrame([{
                    "Zeitpunkt": datetime.now().strftime("%d.%m.%Y %H:%M"),
                    "Ersteller": dein_name,
                    "Spieler": betroffener_spieler,
                    "Beteiligte": beteiligte_mitglieder,
                    "Problem": problem,
                    "Massnahmen": massnahmen,
                    "Begruendung": begruendung,
                    "Beweise": clips
                }])
                
                # Bestehende Berichte laden und neuen anhängen
                try:
                    df_berichte_alt = load_data("Berichte")
                    df_gesamt = pd.concat([df_berichte_alt, neuer_eintrag], ignore_index=True)
                    conn.update(worksheet="Berichte", data=df_gesamt)
                    st.success("✅ Bericht wurde erfolgreich gespeichert!")
                except Exception as e:
                    st.error(f"Fehler beim Speichern: {e}")
            else:
                st.warning("⚠️ Bitte mindestens den Spielernamen und das Problem angeben!")

# ==========================================
# 2. TAB: ADMIN-BEREICH
# ==========================================
with tab_admin:
    st.header("Interner Management-Bereich")
    
    passwort = st.text_input("Admin-Passwort", type="password")
    
    if passwort == "2504":
        st.success("Willkommen in der Verwaltung.")
        
        # Unter-Menü für Admins
        admin_wahl = st.radio("Bereich wählen:", ["Eingegangene Berichte", "Personalverwaltung"], horizontal=True)
        
        if admin_wahl == "Eingegangene Berichte":
            st.subheader("Alle Support-Berichte (Übersicht)")
            df_berichte = load_data("Berichte")
            # Zeigt die neuesten Berichte oben an
            st.dataframe(df_berichte.iloc[::-1], use_container_width=True)
            
        elif admin_wahl == "Personalverwaltung":
            st.subheader("Mitarbeiterliste & Verwarnungen")
            df_personal = load_data("Personal")
            
            st.info("Hier kannst du Mitarbeiter hinzufügen, entfernen oder Verwarnungen anpassen.")
            edited_df = st.data_editor(df_personal, num_rows="dynamic", use_container_width=True)
            
            if st.button("Änderungen in Datenbank speichern"):
                try:
                    conn.update(worksheet="Personal", data=edited_df)
                    st.success("✅ Personal-Datenbank aktualisiert!")
                except Exception as e:
                    st.error(f"Fehler beim Speichern: {e}")
                    
    elif passwort != "":
        st.error("❌ Falsches Passwort!")
