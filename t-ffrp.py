import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- KONFIGURATION ---
st.set_page_config(page_title="FF Team-Panel", page_icon="👾", layout="wide")

SHEET_ID = "1TZHjV7RTrE27p-hapfMe11eCUXhS9QFAd53OCQjpeOc"
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyy4XXxcY4-L7iU0X687hxXEluTwzFNv2XWU14cdHr3FEIlkkw-45eawPYA6cy0ICUN/exec"

URL_P = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=P"
URL_B = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=B"

# RÄNGE UND SORTIERUNG
LISTE_RAENGE = [
    "Projektleitung", "Stellv. Projektleitung", "Management", 
    "Teamleitung", "Stellv. Teamleitung", "Administrative Leitung", 
    "Administrator", "Moderator", "Supporter", "Test-Supporter"
]

RANG_ORDNUNG = {rang: i + 1 for i, rang in enumerate(LISTE_RAENGE)}

def load_data(url):
    try:
        df = pd.read_csv(f"{url}&cachebust={datetime.now().timestamp()}")
        if "Rang" in df.columns:
            # Sortierung nach der definierten RANG_ORDNUNG
            df['Sort'] = df['Rang'].map(RANG_ORDNUNG).fillna(99)
            df = df.sort_values('Sort').drop(columns=['Sort'])
        return df
    except:
        return pd.DataFrame()

# --- DATEN LADEN ---
df_personal = load_data(URL_P)
team_liste = df_personal["Name"].dropna().tolist() if not df_personal.empty else ["Lade Fehler..."]

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
# 2. TAB: ADMIN-BEREICH
# ==========================================
with tab_admin:
    st.header("Admin-Verwaltung")
    pw = st.text_input("Passwort", type="password")
    
    if pw == "2504":
        admin_wahl = st.radio("Bereich:", ["Support-Berichte", "Personal-Verwaltung"], horizontal=True)
        
        if admin_wahl == "Support-Berichte":
            st.subheader("Eingegangene Berichte")
            df_b = load_data(URL_B)
            # Editor für Berichte (löschen/korrigieren)
            edited_b = st.data_editor(df_b, use_container_width=True, num_rows="dynamic")
            
            if st.button("Berichte-Änderungen speichern"):
                payload = {"sheet": "B", "action": "update_all", "headers": df_b.columns.tolist(), "rows": edited_b.values.tolist()}
                requests.post(WEBHOOK_URL, data=json.dumps(payload))
                st.success("✅ Berichte aktualisiert!")

        elif admin_wahl == "Personal-Verwaltung":
            st.subheader("Personal verwalten")
            
            # Formular für komplett neue Mitglieder
            with st.expander("➕ Neues Mitglied registrieren"):
                with st.form("new_member"):
                    n_name = st.text_input("Name")
                    n_rang = st.selectbox("Rang", LISTE_RAENGE)
                    n_date = st.date_input("Beitritt", datetime.now())
                    if st.form_submit_button("Speichern"):
                        p_row = [n_name, n_rang, 0, n_date.strftime("%d.%m.%Y")]
                        requests.post(WEBHOOK_URL, data=json.dumps({"sheet": "P", "row": p_row}))
                        st.rerun()

            st.divider()
            
            # DER TABELLEN-EDITOR MIT DROPDOWN FÜR RÄNGE
            edited_p = st.data_editor(
                df_personal, 
                use_container_width=True, 
                num_rows="dynamic",
                column_config={
                    "Rang": st.column_config.SelectboxColumn(
                        "Rang",
                        help="Wähle den offiziellen Rang aus",
                        options=LISTE_RAENGE,
                        required=True,
                    )
                }
            )
            
            if st.button("Personal-Liste speichern"):
                payload = {
                    "sheet": "P", 
                    "action": "update_all", 
                    "headers": df_personal.columns.tolist(), 
                    "rows": edited_p.values.tolist()
                }
                res = requests.post(WEBHOOK_URL, data=json.dumps(payload))
                if res.status_code == 200:
                    st.success("✅ Personal-Datenbank aktualisiert!")
                    st.rerun()
    elif pw != "":
        st.error("Falsches Passwort")
