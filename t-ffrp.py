import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timedelta

# --- KONFIGURATION ---
st.set_page_config(page_title="FF Team-Panel", page_icon="👾", layout="wide")

# Custom CSS für Gaming-Look & Status-Farben
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .status-active { color: #2ecc71; font-weight: bold; }
    .status-away { color: #f1c40f; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1TZHjV7RTrE27p-hapfMe11eCUXhS9QFAd53OCQjpeOc"
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyB4GeBPncUOdZpAARrzf-EuJa0nqJ5Su5_0MzKg9a30hVhQ7eifQwVqVbRlMtF6y4M/exec" 

URL_P = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=P"
URL_B = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=B"
URL_V = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=V"
URL_A = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=A"

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

# --- FUNKTIONEN ---
def load_data(url):
    try:
        df = pd.read_csv(f"{url}&cachebust={datetime.now().timestamp()}")
        return df
    except:
        return pd.DataFrame()

def get_abmeldungs_status(name, df_abmeldungen):
    if df_abmeldungen.empty: return "Aktiv", ""
    now = datetime.now()
    # Nur akzeptierte Abmeldungen für diesen Nutzer
    user_a = df_abmeldungen[(df_abmeldungen['Name'] == name) & (df_abmeldungen['Status'] == 'Akzeptiert')]
    
    for _, row in user_a.iterrows():
        try:
            start = datetime.strptime(row['Von'], "%Y-%m-%d")
            ende = datetime.strptime(row['Bis'], "%Y-%m-%d")
            # Markierung kurz davor (2 Tage vorher)
            if start - timedelta(days=2) <= now <= start:
                return "Abmeldung nah", f" (Ab {start.strftime('%d.%m.')})"
            # Aktuell abgemeldet
            if start <= now <= ende + timedelta(days=1):
                return "Abgemeldet", f" (Bis {ende.strftime('%d.%m.')})"
        except: continue
    return "Aktiv", ""

def style_team_table(df, df_a):
    def apply_styles(row):
        rank = row['Rang']
        color = RANG_CONFIG.get(rank, {}).get('color', '#ffffff')
        status, info = get_abmeldungs_status(row['Name'], df_a)
        
        styles = []
        for col in row.index:
            if col in ['Name', 'Rang']:
                # Wenn abgemeldet, Name kursiv und info dazu
                s = f'color: {color}; font-weight: bold;'
                if status == "Abgemeldet": s += "text-decoration: line-through; opacity: 0.6;"
                styles.append(s)
            elif col == 'Verwarnungen':
                v = int(row['Verwarnungen'])
                v_col = '#2ecc71' if v == 0 else '#f1c40f' if v == 1 else '#e67e22' if v == 2 else '#e74c3c'
                styles.append(f'color: {v_col}; font-weight: bold;')
            else:
                styles.append('color: #d1d1d1;')
        return styles
    return df.style.apply(apply_styles, axis=1)

# --- DATEN LADEN ---
df_p = load_data(URL_P)
df_a_raw = load_data(URL_A)
team_liste = df_p["Name"].dropna().tolist() if not df_p.empty else []

tab_support, tab_admin = st.tabs(["📝 Support & Abmeldung", "🔒 High-Team-Bereich"])

# ==========================================
# 1. TAB: SUPPORT & ABMELDUNG
# ==========================================
with tab_support:
    sub_tab_bericht, sub_tab_abmelden = st.tabs(["Bericht einreichen", "Abmeldung einreichen"])
    
    with sub_tab_bericht:
        with st.form("support_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.selectbox("Dein Name", team_liste, key="sb_name")
                spieler = st.text_input("Spieler (Discord Username)")
            with c2:
                problem = st.text_area("Problem")
                massnahmen = st.text_area("Maßnahmen")
            if st.form_submit_button("Bericht absenden"):
                row = [datetime.now().strftime("%d.%m.%Y %H:%M"), name, spieler, "", problem, massnahmen, "", ""]
                requests.post(WEBHOOK_URL, data=json.dumps({"sheet": "B", "row": row}))
                st.success("✅ Bericht gespeichert!")

    with sub_tab_abmelden:
        st.subheader("Team-Abmeldung (LOA)")
        with st.form("abmeldung_form", clear_on_submit=True):
            a_name = st.selectbox("Dein Name", team_liste, key="ab_name")
            a_grund = st.text_area("Grund der Abmeldung")
            c1, c2 = st.columns(2)
            with c1: a_von = st.date_input("Von", datetime.now())
            with c2: a_bis = st.date_input("Bis", datetime.now() + timedelta(days=7))
            a_zusatz = st.text_input("Zusatzinfos (z.B. Erreichbarkeit)")
            
            if st.form_submit_button("Abmeldung beantragen"):
                # Status ist standardmäßig "Offen"
                row = [datetime.now().strftime("%d.%m.%Y %H:%M"), a_name, a_grund, str(a_von), str(a_bis), a_zusatz, "Offen"]
                requests.post(WEBHOOK_URL, data=json.dumps({"sheet": "A", "row": row}))
                st.success("✅ Abmeldung eingereicht. Bitte auf Freigabe durch High-Team warten.")

# ==========================================
# 2. TAB: ADMIN
# ==========================================
with tab_admin:
    pw = st.text_input("Passwort", type="password")
    if pw == "2504":
        t1, t2, t3, t4 = st.tabs(["📊 Übersicht", "✅ Abmeldungen prüfen", "⚠️ Verwarnungen", "🛠 Editor"])
        
        with t1:
            st.subheader("Team-Status")
            # Sortierung nach Rang einfügen
            df_p['Sort'] = df_p['Rang'].map(lambda x: RANG_CONFIG.get(x, {}).get('order', 99))
            df_display = df_p.sort_values('Sort').drop(columns=['Sort'])
            st.dataframe(style_team_table(df_display, df_a_raw), use_container_width=True)

        with t2:
            st.subheader("Offene Abmeldungen")
            offene_a = df_a_raw[df_a_raw['Status'] == 'Offen']
            if offene_a.empty:
                st.info("Keine neuen Abmeldungen vorhanden.")
            else:
                for idx, row in offene_a.iterrows():
                    with st.expander(f"Abmeldung von {row['Name']} ({row['Von']} bis {row['Bis']})"):
                        st.write(f"**Grund:** {row['Grund']}")
                        st.write(f"**Zusatz:** {row['Zusatz']}")
                        if st.button(f"Akzeptieren##{idx}"):
                            df_a_raw.at[idx, 'Status'] = 'Akzeptiert'
                            payload = {"sheet": "A", "action": "update_all", "headers": df_a_raw.columns.tolist(), "rows": df_a_raw.values.tolist()}
                            requests.post(WEBHOOK_URL, data=json.dumps(payload))
                            st.rerun()
