import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- KONFIGURATION ---
st.set_page_config(page_title="FF Team-Panel", page_icon="👾", layout="wide")

# Custom CSS für den Gaming-Look (Dark Mode Optimierung)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1b1f27;
        border-radius: 5px 5px 0px 0px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #ff4b4b !important; }
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1TZHjV7RTrE27p-hapfMe11eCUXhS9QFAd53OCQjpeOc"
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyy4XXxcY4-L7iU0X687hxXEluTwzFNv2XWU14cdHr3FEIlkkw-45eawPYA6cy0ICUN/exec"

URL_P = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=P"
URL_B = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=B"

# RÄNGE, SORTIERUNG UND FARBEN
RANG_CONFIG = {
    "Projektleitung": {"order": 1, "color": "#ff4b4b"},
    "Stellv. Projektleitung": {"order": 2, "color": "#ff4b4b"},
    "Management": {"order": 3, "color": "#ff8c00"},
    "Teamleitung": {"order": 4, "color": "#ae81ff"},
    "Stellv. Teamleitung": {"order": 5, "color": "#ae81ff"},
    "Administrative Leitung": {"order": 6, "color": "#00aaff"},
    "Administrator": {"order": 7, "color": "#00aaff"},
    "Moderator": {"order": 8, "color": "#2ecc71"},
    "Supporter": {"order": 9, "color": "#2ecc71"},
    "Test-Supporter": {"order": 10, "color": "#95a5a6"}
}

LISTE_RAENGE = list(RANG_CONFIG.keys())

# --- STYLING FUNKTIONEN ---
def color_verwarnungen(val):
    try:
        v = int(val)
        if v == 0: color = '#2ecc71' # Grün
        elif v == 1: color = '#f1c40f' # Gelb
        elif v == 2: color = '#e67e22' # Orange
        else: color = '#e74c3c' # Rot
        return f'color: {color}; font-weight: bold; font-size: 1.1em;'
    except:
        return ''

def style_team_table(df):
    if df.empty: return df
    
    def apply_row_style(row):
        rank = row['Rang']
        color = RANG_CONFIG.get(rank, {}).get('color', '#ffffff')
        # Erstellt einen farbigen Glow-Effekt am linken Rand der Zeile
        return [f'border-left: 6px solid {color}; background-color: rgba(255,255,255,0.02);' for _ in row]

    styled = df.style.apply(apply_row_style, axis=1)
    if "Verwarnungen" in df.columns:
        styled = styled.applymap(color_verwarnungen, subset=['Verwarnungen'])
    return styled

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
            beteiligte = st.text_area("Andere beteiligte Teamler")
        with c2:
            problem = st.text_area("Problem")
            massnahmen = st.text_area("Maßnahmen")
            begruendung = st.text_area("Begründung")
        clips = st.text_area("Beweise (Clips / Zeugen / Bilder)")
        
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
        # Unter-Tabs für bessere Übersicht
        admin_sub_tab1, admin_sub_tab2 = st.tabs(["📊 Team-Übersicht", "🛠 Bearbeitungs-Modus"])
        
        with admin_sub_tab1:
            st.subheader("Aktueller Team-Status")
            # Anzeige der gestylten Tabelle
            st.table(style_team_table(df_personal))
            
            st.divider()
            st.subheader("Support-Berichte (Letzte zuerst)")
            df_b = load_data(URL_B)
            st.dataframe(df_b.iloc[::-1], use_container_width=True)

        with admin_sub_tab2:
            st.subheader("Datenbank-Editor")
            
            # Bereich für neues Personal
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
            
            # Editor für Personal
            st.write("Personal-Liste bearbeiten:")
            edited_p = st.data_editor(
                df_personal, 
                use_container_width=True, 
                num_rows="dynamic",
                column_config={
                    "Rang": st.column_config.SelectboxColumn("Rang", options=LISTE_RAENGE, required=True),
                    "Verwarnungen": st.column_config.NumberColumn("Verwarnungen", min_value=0, max_value=5)
                }
            )
            
            if st.button("Änderungen an Personal-Liste speichern"):
                payload = {"sheet": "P", "action": "update_all", "headers": df_personal.columns.tolist(), "rows": edited_p.values.tolist()}
                res = requests.post(WEBHOOK_URL, data=json.dumps(payload))
                if res.status_code == 200:
                    st.success("✅ Personal-Datenbank aktualisiert!")
                    st.rerun()
            
            st.divider()
            st.write("Berichte bearbeiten/löschen:")
            df_b_edit = load_data(URL_B)
            edited_b = st.data_editor(df_b_edit, use_container_width=True, num_rows="dynamic")
            
            if st.button("Änderungen an Berichten speichern"):
                payload = {"sheet": "B", "action": "update_all", "headers": df_b_edit.columns.tolist(), "rows": edited_b.values.tolist()}
                requests.post(WEBHOOK_URL, data=json.dumps(payload))
                st.success("✅ Berichte aktualisiert!")

    elif pw != "":
        st.error("❌ Falsches Passwort")
