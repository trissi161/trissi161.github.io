import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timedelta

# --- KONFIGURATION ---
st.set_page_config(page_title="FF Team-Panel", page_icon="👾", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stMetricValue"] { font-size: 1.8rem; }
    .stDataFrame { border: none !important; }
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

def load_data(url):
    try:
        return pd.read_csv(f"{url}&cachebust={datetime.now().timestamp()}")
    except:
        return pd.DataFrame()

def get_status_info(name, df_a):
    """Ermittelt den Status-Typ und die Farbe."""
    if df_a.empty or "Name" not in df_a.columns:
        return "🟢 Anwesend", "#2ecc71"
    
    heute = datetime.now().date()
    suche_name = str(name).strip().lower()
    aktive_abmeldungen = df_a[df_a['Status'].astype(str).str.strip() == 'Akzeptiert'].copy()
    
    for _, row in aktive_abmeldungen.iterrows():
        if str(row['Name']).strip().lower() == suche_name:
            try:
                start = pd.to_datetime(row['Von']).date()
                ende = pd.to_datetime(row['Bis']).date()
                
                if start <= heute <= ende:
                    return "🔴 Abwesend", "#e74c3c"
                elif heute < start <= (heute + timedelta(days=2)):
                    return "🟡 Bald weg", "#f1c40f"
            except:
                continue
    return "🟢 Anwesend", "#2ecc71"

def style_team_table(df, df_a):
    if df.empty: return df
    
    # Status-Daten für alle Zeilen vorbereiten
    status_list = []
    status_colors = []
    for name in df['Name']:
        label, color = get_status_info(name, df_a)
        status_list.append(label)
        status_colors.append(color)
    
    df.insert(0, "Status", status_list)
    
    def apply_styles(row):
        rank = row['Rang']
        rank_color = RANG_CONFIG.get(rank, {}).get('color', '#ffffff')
        
        # Den Status dieser Zeile finden
        label, s_color = get_status_info(row['Name'], df_a)
        
        styles = []
        for col in row.index:
            if col == "Status":
                styles.append(f'color: {s_color}; font-weight: bold;')
            elif col in ['Name', 'Rang']:
                # Wenn abwesend, machen wir den Text etwas blasser
                opacity = "0.5" if "🔴" in label else "1.0"
                styles.append(f'color: {rank_color}; font-weight: bold; opacity: {opacity};')
            elif col == 'Verwarnungen':
                v = int(row['Verwarnungen'])
                v_col = '#2ecc71' if v == 0 else '#f1c40f' if v == 1 else '#e67e22' if v == 2 else '#e74c3c'
                styles.append(f'color: {v_col}; font-weight: bold;')
            else:
                styles.append('color: #d1d1d1;')
        return styles
    
    return df.style.apply(apply_styles, axis=1)

# --- APP ---
df_p = load_data(URL_P)
df_a = load_data(URL_A)
team_liste = df_p["Name"].dropna().tolist() if not df_p.empty else []

tab_support, tab_admin = st.tabs(["📝 Support & Abmeldung", "🔒 High-Team-Bereich"])

with tab_support:
    s_sub1, s_sub2 = st.tabs(["Bericht einreichen", "Abmeldung beantragen"])
    with s_sub1:
        with st.form("f_bericht", clear_on_submit=True):
            n = st.selectbox("Dein Name", team_liste)
            s = st.text_input("Spieler Name")
            p = st.text_area("Vorfall / Problem")
            if st.form_submit_button("Bericht absenden"):
                requests.post(WEBHOOK_URL, data=json.dumps({"sheet":"B", "row":[datetime.now().strftime("%d.%m.%Y %H:%M"), n, s, "", p, "", "", ""]}))
                st.success("Bericht erfolgreich gespeichert!")
    
    with s_sub2:
        with st.form("f_loa", clear_on_submit=True):
            n = st.selectbox("Name", team_liste, key="loa_n")
            g = st.text_area("Grund")
            c1, c2 = st.columns(2)
            v = c1.date_input("Von", datetime.now())
            b = c2.date_input("Bis", datetime.now() + timedelta(days=7))
            if st.form_submit_button("Antrag stellen"):
                requests.post(WEBHOOK_URL, data=json.dumps({"sheet":"A", "row":[datetime.now().strftime("%d.%m.%Y %H:%M"), n, g, str(v), str(b), "", "Offen"]}))
                st.success("Antrag eingereicht! Warte auf Bestätigung.")

with tab_admin:
    pw = st.text_input("Passwort", type="password")
    if pw == "2504":
        t1, t2, t3 = st.tabs(["📊 Team-Status", "✅ Anträge prüfen", "🛠 Editor"])
        
        with t1:
            if not df_p.empty:
                df_p['Sort'] = df_p['Rang'].map(lambda x: RANG_CONFIG.get(x, {}).get('order', 99))
                df_disp = df_p.sort_values('Sort').drop(columns=['Sort'])
                st.dataframe(style_team_table(df_disp, df_a), use_container_width=True, height=500)
                
                with st.expander("🔍 Debug"):
                    st.write("Heute ist:", datetime.now().date())
                    st.write("Daten aus Blatt A:", df_a)

        with t2:
            st.subheader("Offene Abmeldungen")
            df_a_curr = load_data(URL_A)
            offen = df_a_curr[df_a_curr['Status'].astype(str).str.strip() == 'Offen']
            if offen.empty:
                st.info("Keine offenen Anträge.")
            else:
                for i, r in offen.iterrows():
                    if st.button(f"Akzeptiere {r['Name']} ({r['Von']} bis {r['Bis']})", key=f"acc_{i}"):
                        df_a_curr.at[i, 'Status'] = 'Akzeptiert'
                        requests.post(WEBHOOK_URL, data=json.dumps({"sheet":"A", "action":"update_all", "headers":df_a_curr.columns.tolist(), "rows":df_a_curr.values.tolist()}))
                        st.rerun()
