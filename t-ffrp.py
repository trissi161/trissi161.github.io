import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- KONFIGURATION ---
st.set_page_config(page_title="FFRP Team-Panel", page_icon="👾", layout="wide")

# DEINE DATEN (HIER ANPASSEN!)
SHEET_ID = "1TZHjV7RTrE27p-hapfMe11eCUXhS9QFAd53OCQjpeOc"
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyy4XXxcY4-L7iU0X687hxXEluTwzFNv2XWU14cdHr3FEIlkkw-45eawPYA6cy0ICUN/exec" 

URL_P = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=P"
URL_B = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=B"

def load_data(url):
    try:
        return pd.read_csv(f"{url}&cachebust={datetime.now().timestamp()}")
    except:
        return pd.DataFrame()

# --- DATEN LADEN ---
df_personal = load_data(URL_P)
team_liste = df_personal["Name"].dropna().tolist() if not df_personal.empty else ["Lade Fehler..."]

tab_bericht, tab_admin = st.tabs(["📝 Support-Bericht", "🔒 Admin-Bereich"])

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
            # Daten für den Postboten vorbereiten
            row_data = [
                datetime.now().strftime("%d.%m.%Y %H:%M"),
                name, spieler, beteiligte, problem, massnahmen, begruendung, clips
            ]
            payload = {"sheet": "B", "row": row_data}
            
            # Senden an Google Apps Script
            response = requests.post(WEBHOOK_URL, data=json.dumps(payload))
            if response.status_code == 200:
                st.success("✅ Bericht erfolgreich gespeichert!")
            else:
                st.error("Fehler beim Senden an Google.")

with tab_admin:
    pw = st.text_input("Passwort", type="password")
    if pw == "2504":
        st.subheader("Alle Berichte")
        st.dataframe(load_data(URL_B).iloc[::-1], use_container_width=True)
        
        st.subheader("Personal (Nur lesen)")
        st.dataframe(df_personal, use_container_width=True)
        st.info("Hinweis: Personal-Änderungen bitte direkt im Google Sheet machen, da der Schreibzugriff hier gesperrt ist.")
