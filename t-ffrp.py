import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- KONFIGURATION ---
st.set_page_config(page_title="FF Team-Panel", page_icon="👾", layout="wide")

SHEET_ID = "1TZHjV7RTrE27p-hapfMe11eCUXhS9QFAd53OCQjpeOc"
# Stelle sicher, dass dies deine aktuelle Web-App-URL ist!
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyy4XXxcY4-L7iU0X687hxXEluTwzFNv2XWU14cdHr3FEIlkkw-45eawPYA6cy0ICUN/exec"

URL_P = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=P"
URL_B = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=B"

# RANG-SORTIERUNG DEFINIEREN
RANG_ORDNUNG = {
    "Projektleitung": 1,
    "Stellv. Projektleitung": 2,
    "Management": 3,
    "Teamleitung": 4,
    "Stellv. Teamleitung": 5,
    "Administrative Leitung": 6,
    "Administrator": 7,
    "Moderator": 8,
    "Supporter": 9,
    "Test-Supporter": 10
}

def load_data(url):
    try:
        df = pd.read_csv(f"{url}&cachebust={datetime.now().timestamp()}")
        # Sortierung anwenden, falls es die Personal-Liste ist
        if "Rang" in df.columns:
            df['Sort'] = df['Rang'].map(RANG_ORDNUNG).fillna(99)
            df = df.sort_values('Sort').drop(columns=['Sort'])
        return df
    except:
        return pd.DataFrame()

# --- DATEN LADEN ---
df_personal = load_data(URL_P)
team_liste = df_personal["Name"].dropna().tolist() if not df_personal.empty else ["Lade Fehler..."]

tab_bericht, tab_admin = st.tabs(["📝 Support-Bericht", "🔒 Admin-Bereich"])

# --- SUPPORT BERICHT (Bleibt gleich) ---
with tab_bericht:
    st.header("Support-Bericht einreichen")
    with st.form("support_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.selectbox("Dein Name", team_liste)
            spieler = st.text_input("Spieler")
            beteiligte = st.text_area("Beteiligte")
        with c2:
            problem = st.text_area("Problem")
            massnahmen = st.text_area("Maßnahmen")
            begruendung = st.text_area("Begründung")
        clips = st.text_area("Beweise")
        
        if st.form_submit_button("Bericht absenden"):
            row_data = [datetime.now().strftime("%d.%m.%Y %H:%M"), name, spieler, beteiligte, problem, massnahmen, begruendung, clips]
            payload = {"sheet": "B", "row": row_data}
            requests.post(WEBHOOK_URL, data=json.dumps(payload))
            st.success("✅ Bericht gespeichert!")

# --- ADMIN BEREICH (NEU MIT EDIT-FUNKTION) ---
with tab_admin:
    st.header("Admin-Verwaltung")
    pw = st.text_input("Passwort", type="password")
    
    if pw == "2504":
        admin_wahl = st.radio("Bereich:", ["Support-Berichte", "Personal-Verwaltung"], horizontal=True)
        
        if admin_wahl == "Support-Berichte":
            st.subheader("Eingegangene Berichte")
            df_b = load_data(URL_B)
            # Hier nutzen wir den Editor, damit man Berichte korrigieren oder löschen kann
            edited_b = st.data_editor(df_b, use_container_width=True, num_rows="dynamic")
            
            if st.button("Berichte-Änderungen speichern"):
                payload = {
                    "sheet": "B",
                    "action": "update_all",
                    "headers": df_b.columns.tolist(),
                    "rows": edited_b.values.tolist()
                }
                requests.post(WEBHOOK_URL, data=json.dumps(payload))
                st.success("✅ Berichte aktualisiert!")

        elif admin_wahl == "Personal-Verwaltung":
            st.subheader("Personal verwalten")
            st.info("💡 Du kannst Namen, Ränge oder Verwarnungen direkt in der Tabelle ändern und neue Zeilen unten hinzufügen.")
            
            # Der Editor erlaubt direktes Bearbeiten
            edited_p = st.data_editor(df_personal, use_container_width=True, num_rows="dynamic")
            
            if st.button("Personal-Liste speichern"):
                payload = {
                    "sheet": "P",
                    "action": "update_all",
                    "headers": df_personal.columns.tolist(),
                    "rows": edited_p.values.tolist()
                }
                res = requests.post(WEBHOOK_URL, data=json.dumps(payload))
                if res.status_code == 200:
                    st.success("✅ Personal-Datenbank erfolgreich aktualisiert!")
                    st.rerun()
    elif pw != "":
        st.error("Falsches Passwort")
