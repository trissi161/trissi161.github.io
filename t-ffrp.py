import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- KONFIGURATION ---
st.set_page_config(page_title="FF Team-Panel", page_icon="👾", layout="wide")

SHEET_ID = "1TZHjV7RTrE27p-hapfMe11eCUXhS9QFAd53OCQjpeOc"
WEBHOOK_URL = "DEINE_KOPIERTE_WEB_APP_URL_HIER" # Deine URL einfügen!

URL_P = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=P"
URL_B = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=B"

def load_data(url):
    try:
        return pd.read_csv(f"{url}&cachebust={datetime.now().timestamp()}")
    except:
        return pd.DataFrame()

# --- DATEN LADEN ---
df_personal = load_data(URL_P)

# Sicherstellen, dass die Liste aktuell ist
if not df_personal.empty and "Name" in df_personal.columns:
    team_liste = df_personal["Name"].dropna().tolist()
else:
    team_liste = ["Lade Fehler..."]

tab_bericht, tab_admin = st.tabs(["📝 Support-Bericht", "🔒 Admin-Bereich"])

# ==========================================
# 1. TAB: SUPPORT-BERICHT
# ==========================================
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

# ==========================================
# 2. TAB: ADMIN-BEREICH (Personal-Management)
# ==========================================
with tab_admin:
    st.header("Admin-Verwaltung")
    pw = st.text_input("Passwort", type="password")
    
    if pw == "2504":
        admin_wahl = st.radio("Bereich:", ["Support-Berichte", "Personal-Verwaltung"], horizontal=True)
        
        if admin_wahl == "Support-Berichte":
            st.subheader("Eingegangene Berichte")
            st.dataframe(load_data(URL_B).iloc[::-1], use_container_width=True)
            
        elif admin_wahl == "Personal-Verwaltung":
            st.subheader("Neues Teammitglied hinzufügen")
            
            # Formular für neues Personal
            with st.expander("➕ Neues Mitglied registrieren", expanded=False):
                with st.form("new_member_form", clear_on_submit=True):
                    new_name = st.text_input("Vollständiger Name")
                    new_rank = st.selectbox("Rang", ["Projektleitung", "Management", "Administrator", "Moderator", "Supporter", "Guide"])
                    # Beitrittsdatum standardmäßig auf HEUTE gesetzt
                    new_date = st.date_input("Beitrittsdatum", datetime.now())
                    
                    if st.form_submit_button("Mitglied speichern"):
                        if new_name:
                            # Daten für Blatt "P" vorbereiten
                            # Reihenfolge: Name, Rang, Verwarnungen (0), Beitrittsdatum
                            p_row = [new_name, new_rank, 0, new_date.strftime("%d.%m.%Y")]
                            payload_p = {"sheet": "P", "row": p_row}
                            
                            res = requests.post(WEBHOOK_URL, data=json.dumps(payload_p))
                            if res.status_code == 200:
                                st.success(f"✅ {new_name} wurde als {new_rank} hinzugefügt!")
                                st.rerun() # Seite neu laden, um Dropdowns zu aktualisieren
                        else:
                            st.warning("Bitte einen Namen eingeben.")

            st.divider()
            st.subheader("Aktuelle Team-Liste")
            st.dataframe(df_personal, use_container_width=True)
            st.info("💡 Verwarnungen oder Namensänderungen bitte aktuell noch direkt im Google Sheet anpassen.")
            
    elif pw != "":
        st.error("Falsches Passwort")
