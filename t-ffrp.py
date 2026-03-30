import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timedelta

# --- KONFIGURATION ---
st.set_page_config(page_title="FF Team-Panel", page_icon="👾", layout="wide")

# Custom CSS
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

# --- HILFSFUNKTIONEN ---
def load_data(url):
    try:
        # Cache-Busting sorgt dafür, dass immer die neuesten Daten geladen werden
        df = pd.read_csv(f"{url}&cachebust={datetime.now().timestamp()}")
        return df
    except:
        return pd.DataFrame()

def get_status_info(name, df_a):
    """Prüft den Abmeldestatus einer Person."""
    if df_a.empty or "Name" not in df_a.columns:
        return "Aktiv", None
    
    # Heutiges Datum (nur Datumsteil)
    heute = datetime.now().date()
    
    # Namen bereinigen für den Vergleich (trimmt Leerzeichen)
    suche_name = str(name).strip().lower()
    
    # Filtern: Name passt & Status ist Akzeptiert
    # Wir machen alles kleingeschrieben und ohne Leerzeichen für maximale Sicherheit
    abmeldungen = df_a[
        (df_a['Name'].astype(str).str.strip().str.lower() == suche_name) & 
        (df_a['Status'].astype(str).str.strip() == 'Akzeptiert')
    ]
    
    for _, row in abmeldungen.iterrows():
        try:
            # Datums-Konvertierung (YYYY-MM-DD aus deinem Screenshot)
            von = pd.to_datetime(row['Von']).date()
            bis = pd.to_datetime(row['Bis']).date()
            
            # 1. Aktuell abgemeldet
            if von <= heute <= bis:
                return "Abgemeldet", f" (Bis {bis.strftime('%d.%m.')})"
            # 2. Abmeldung steht kurz bevor (in den nächsten 2 Tagen)
            elif heute < von <= (heute + timedelta(days=2)):
                return "Abmeldung nah", f" (Ab {von.strftime('%d.%m.')})"
        except:
            continue
            
    return "Aktiv", None

def style_team_table(df, df_a):
    if df.empty: return df
    
    def apply_styles(row):
        rank = row['Rang']
        color = RANG_CONFIG.get(rank, {}).get('color', '#ffffff')
        status, info = get_status_info(row['Name'], df_a)
        
        styles = []
        for col in row.index:
            if col in ['Name', 'Rang']:
                base = f'color: {color}; font-weight: bold;'
                if status == "Abgemeldet":
                    base += "text-decoration: line-through; opacity: 0.5;"
                elif status == "Abmeldung nah":
                    base += "border-bottom: 2px dashed #f1c40f;"
                styles.append(base)
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
df_a = load_data(URL_A)
team_liste = df_p["Name"].dropna().tolist() if not df_p.empty else []

tab_main, tab_admin = st.tabs(["📝 Support & Abmeldung", "🔒 High-Team-Bereich"])

# --- SUPPORT BEREICH ---
with tab_main:
    sub1, sub2 = st.tabs(["Bericht schreiben", "Abmeldung einreichen"])
    with sub1:
        st.header("Support-Bericht")
        with st.form("f_bericht", clear_on_submit=True):
            n = st.selectbox("Dein Name", team_liste)
            s = st.text_input("Spieler")
            p = st.text_area("Problem")
            if st.form_submit_button("Senden"):
                requests.post(WEBHOOK_URL, data=json.dumps({"sheet":"B", "row":[datetime.now().strftime("%d.%m.%Y %H:%M"), n, s, "", p, "", "", ""]}))
                st.success("Gesendet!")
    
    with sub2:
        st.header("Abmeldung (LOA)")
        with st.form("f_loa", clear_on_submit=True):
            n = st.selectbox("Name", team_liste)
            g = st.text_area("Grund")
            c1, c2 = st.columns(2)
            v = c1.date_input("Von", datetime.now())
            b = c2.date_input("Bis", datetime.now() + timedelta(days=7))
            if st.form_submit_button("Beantragen"):
                requests.post(WEBHOOK_URL, data=json.dumps({"sheet":"A", "row":[datetime.now().strftime("%d.%m.%Y %H:%M"), n, g, str(v), str(b), "", "Offen"]}))
                st.success("Beantragt!")

# --- ADMIN BEREICH ---
with tab_admin:
    pw = st.text_input("Passwort", type="password")
    if pw == "2504":
        t1, t2, t3 = st.tabs(["📊 Übersicht", "✅ Abmeldungen", "🛠 Editor"])
        
        with t1:
            if not df_p.empty:
                # Sortierung
                df_p['Sort'] = df_p['Rang'].map(lambda x: RANG_CONFIG.get(x, {}).get('order', 99))
                df_disp = df_p.sort_values('Sort').drop(columns=['Sort'])
                st.dataframe(style_team_table(df_disp, df_a), use_container_width=True)
                
                # DIAGNOSE-HILFE (Nur sichtbar wenn Admin eingeloggt)
                with st.expander("🔍 Debug-Info (Warum ist jemand nicht durchgestrichen?)"):
                    st.write("Heute ist:", datetime.now().date())
                    st.write("Geladene Abmeldungen (Akzeptiert):")
                    st.write(df_a[df_a['Status'] == 'Akzeptiert'])

        with t2:
            st.subheader("Offene Anträge")
            df_a_curr = load_data(URL_A)
            offen = df_a_curr[df_a_curr['Status'] == 'Offen']
            if offen.empty: st.info("Alles erledigt.")
            else:
                for i, r in offen.iterrows():
                    if st.button(f"Akzeptiere {r['Name']} ({r['Von']} bis {r['Bis']})", key=f"btn_{i}"):
                        df_a_curr.at[i, 'Status'] = 'Akzeptiert'
                        requests.post(WEBHOOK_URL, data=json.dumps({"sheet":"A", "action":"update_all", "headers":df_a_curr.columns.tolist(), "rows":df_a_curr.values.tolist()}))
                        st.rerun()
