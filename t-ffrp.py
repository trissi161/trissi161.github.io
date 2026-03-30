import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- KONFIGURATION ---
st.set_page_config(page_title="FF Team-Panel", page_icon="👾", layout="wide")

# Custom CSS für Gaming-Look & saubere Tabellen
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stMetricValue"] { font-size: 1.8rem; }
    .stDataFrame { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1TZHjV7RTrE27p-hapfMe11eCUXhS9QFAd53OCQjpeOc"
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyB4GeBPncUOdZpAARrzf-EuJa0nqJ5Su5_0MzKg9a30hVhQ7eifQwVqVbRlMtF6y4M/exec" # Prüfe, ob die URL noch aktuell ist!

URL_P = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=P"
URL_B = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=B"

# RÄNGE UND FARBEN
RANG_CONFIG = {
    "Projektleitung": {"order": 1, "color": "#ff4b4b"}, # Hellrot
    "Stellv. Projektleitung": {"order": 2, "color": "#ff4b4b"},
    "Management": {"order": 3, "color": "#ff8c00"}, # Orange
    "Teamleitung": {"order": 4, "color": "#ae81ff"}, # Lila
    "Stellv. Teamleitung": {"order": 5, "color": "#ae81ff"},
    "Administrative Leitung": {"order": 6, "color": "#00aaff"}, # Blau
    "Administrator": {"order": 7, "color": "#00aaff"},
    "Moderator": {"order": 8, "color": "#2ecc71"}, # Grün
    "Supporter": {"order": 9, "color": "#2ecc71"},
    "Test-Supporter": {"order": 10, "color": "#95a5a6"} # Grau
}

# --- STYLING FUNKTIONEN ---
def style_team_table(df):
    if df.empty: return df

    def apply_text_colors(row):
        rank = row['Rang']
        color = RANG_CONFIG.get(rank, {}).get('color', '#ffffff')
        # Färbt den Text für Name und Rang in der Teamfarbe
        styles = []
        for col in row.index:
            if col in ['Name', 'Rang']:
                styles.append(f'color: {color}; font-weight: bold;')
            elif col == 'Verwarnungen':
                v = int(row['Verwarnungen'])
                v_color = '#2ecc71' if v == 0 else '#f1c40f' if v == 1 else '#e67e22' if v == 2 else '#e74c3c'
                styles.append(f'color: {v_color}; font-weight: bold;')
            else:
                styles.append('color: #d1d1d1;')
        return styles

    return df.style.apply(apply_text_colors, axis=1)

def load_data(url):
    try:
        df = pd.read_csv(f"{url}&cachebust={datetime.now().timestamp()}")
        if "Rang" in df.columns:
            df['Sort'] = df['Rang'].map(lambda x: RANG_CONFIG.get(x, {}).get('order', 99))
            df = df.sort_values('Sort').drop(columns=['Sort'])
        return df
    except:
        return pd.DataFrame()

# --- DATEN LADEN ---
df_personal = load_data(URL_P)
team_liste = df_personal["Name"].dropna().tolist() if not df_personal.empty else ["Lade Fehler..."]

tab_bericht, tab_admin = st.tabs(["📝 Support-Bericht", "🔒 High-Team-Bereich"])

# --- SUPPORT BERICHT ---
with tab_bericht:
    st.header("Support-Bericht einreichen")
    with st.form("support_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.selectbox("Dein Name", team_liste)
            spieler = st.text_input("Spieler")
            beteiligte = st.text_area("Andere beteiligte Teamler")
        with c2:
            problem = st.text_area("Problem")
            massnahmen = st.text_area("Maßnahmen")
            begruendung = st.text_area("Begründung")
        clips = st.text_area("Beweise (Clips / Zeugen / Bilder)")
        
        if st.form_submit_button("Bericht absenden"):
            row_data = [datetime.now().strftime("%d.%m.%Y %H:%M"), name, spieler, beteiligte, problem, massnahmen, begruendung, clips]
            requests.post(WEBHOOK_URL, data=json.dumps({"sheet": "B", "row": row_data}))
            st.success("✅ Bericht gespeichert!")

# --- ADMIN BEREICH ---
with tab_admin:
    st.header("Admin-Verwaltung")
    pw = st.text_input("Passwort", type="password")
    
    if pw == "2504":
        admin_sub1, admin_sub2 = st.tabs(["📊 Team-Übersicht", "🛠 Bearbeitungs-Modus"])
        
        with admin_sub1:
            st.subheader("Aktueller Team-Status")
            # Wir nutzen hier st.dataframe für die interaktive Ansicht mit Styling
            st.dataframe(style_team_table(df_personal), use_container_width=True, height=500)
            
            st.divider()
            st.subheader("Letzte Support-Berichte")
            st.dataframe(load_data(URL_B).iloc[::-1], use_container_width=True)

        with admin_sub2:
            st.subheader("Datenbank-Editor")
            
            # Personal Editor
            st.write("Personal bearbeiten:")
            edited_p = st.data_editor(df_personal, use_container_width=True, num_rows="dynamic",
                                      column_config={"Rang": st.column_config.SelectboxColumn("Rang", options=list(RANG_CONFIG.keys()))})
            
            if st.button("Personal-Daten speichern"):
                payload = {"sheet": "P", "action": "update_all", "headers": df_personal.columns.tolist(), "rows": edited_p.values.tolist()}
                res = requests.post(WEBHOOK_URL, data=json.dumps(payload))
                if res.status_code == 200:
                    st.success("✅ Datenbank aktualisiert!")
                    st.rerun()

            st.divider()
            # Berichte Editor
            st.write("Berichte bearbeiten:")
            df_b_edit = load_data(URL_B)
            edited_b = st.data_editor(df_b_edit, use_container_width=True, num_rows="dynamic")
            if st.button("Berichte speichern"):
                payload = {"sheet": "B", "action": "update_all", "headers": df_b_edit.columns.tolist(), "rows": edited_b.values.tolist()}
                requests.post(WEBHOOK_URL, data=json.dumps(payload))
                st.success("✅ Berichte aktualisiert!")
    elif pw != "":
        st.error("Falsches Passwort")
