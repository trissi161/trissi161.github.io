import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timedelta

# --- KONFIGURATION ---
st.set_page_config(page_title="FF Team-Panel", page_icon="👾", layout="wide")

# Custom CSS für Gaming-Look
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

# RÄNGE UND FARBEN
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

def get_status_info(name, df_a):
    """Ermittelt Label und Farbe für den Anwesenheitsstatus."""
    if df_a.empty: return "🟢 Anwesend", "#2ecc71"
    
    now = datetime.now().date()
    suche_name = str(name).strip().lower()
    
    # Filter für akzeptierte Abmeldungen
    aktive_a = df_a[(df_a['Status'].astype(str).str.strip() == 'Akzeptiert')].copy()
    
    for _, row in aktive_a.iterrows():
        if str(row['Name']).strip().lower() == suche_name:
            try:
                # Flexible Datumskonvertierung für Google Sheets Format
                start = pd.to_datetime(row['Von']).date()
                ende = pd.to_datetime(row['Bis']).date()
                
                if start <= now <= ende:
                    return "🔴 Abwesend", "#e74c3c"
                elif now < start <= (now + timedelta(days=2)):
                    return "🟡 Bald weg", "#f1c40f"
            except:
                continue
    return "🟢 Anwesend", "#2ecc71"

def style_team_table(df, df_a):
    if df.empty: return df
    
    # 1. Status-Daten vorab generieren
    labels = []
    colors = []
    for n in df['Name']:
        l, c = get_status_info(n, df_a)
        labels.append(l)
        colors.append(c)
    
    # 2. Status-Spalte ganz vorne einfügen
    df.insert(0, "Status", labels)
    
    def apply_row_styles(row):
        rank = row['Rang']
        rank_color = RANG_CONFIG.get(rank, {}).get('color', '#ffffff')
        # Status für diese Zeile ermitteln
        st_label, st_color = get_status_info(row['Name'], df_a)
        
        styles = []
        for col in row.index:
            if col == "Status":
                styles.append(f'color: {st_color}; font-weight: bold;')
            elif col in ['Name', 'Rang']:
                # Blasser bei Abwesenheit, aber nicht durchgestrichen
                opacity = "0.4" if "🔴" in st_label else "1.0"
                styles.append(f'color: {rank_color}; font-weight: bold; opacity: {opacity};')
            elif col == 'Verwarnungen':
                v = int(row['Verwarnungen'])
                v_c = '#2ecc71' if v == 0 else '#f1c40f' if v == 1 else '#e67e22' if v == 2 else '#e74c3c'
                styles.append(f'color: {v_c}; font-weight: bold;')
            else:
                styles.append('color: #d1d1d1;')
        return styles

    return df.style.apply(apply_row_styles, axis=1)

# --- DATEN LADEN ---
df_personal = load_data(URL_P)
df_abmeldungen = load_data(URL_A)
team_liste = df_personal["Name"].dropna().tolist() if not df_personal.empty else ["Lade Fehler..."]

tab_bericht, tab_admin = st.tabs(["📝 Support-Bereich", "🔒 High-Team-Bereich"])

# ==========================================
# 1. TAB: SUPPORT-BERICHT & ABMELDUNG
# ==========================================
with tab_bericht:
    sub_tab1, sub_tab2 = st.tabs(["Bericht einreichen", "Abmeldung einreichen"])
    
    with sub_tab1:
        st.header("Support-Bericht einreichen")
        with st.form("support_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.selectbox("Dein Name", team_liste, key="sb_name")
                spieler = st.text_input("Spieler (Discord Username)")
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

    with sub_tab2:
        st.header("Abmeldung (LOA) beantragen")
        with st.form("loa_form", clear_on_submit=True):
            a_name = st.selectbox("Dein Name", team_liste, key="loa_name")
            a_grund = st.text_area("Grund der Abmeldung")
            col1, col2 = st.columns(2)
            with col1: a_von = st.date_input("Von", datetime.now())
            with col2: a_bis = st.date_input("Bis", datetime.now() + timedelta(days=7))
            a_zusatz = st.text_input("Zusatz (z.B. Erreichbarkeit via DC)")
            
            if st.form_submit_button("Abmeldung absenden"):
                loa_row = [datetime.now().strftime("%d.%m.%Y %H:%M"), a_name, a_grund, str(a_von), str(a_bis), a_zusatz, "Offen"]
                requests.post(WEBHOOK_URL, data=json.dumps({"sheet": "A", "row": loa_row}))
                st.success("✅ Abmeldung eingereicht! Ein High-Team Mitglied muss diese noch bestätigen.")

# ==========================================
# 2. TAB: ADMIN-BEREICH
# ==========================================
with tab_admin:
    st.header("Admin-Verwaltung")
    pw = st.text_input("Passwort", type="password")
    
    if pw == "2504":
        admin_sub1, admin_sub2, admin_sub3, admin_sub4 = st.tabs(["📊 Team-Übersicht", "✅ Abmeldungen prüfen", "⚠️ Verwarnungen", "🛠 Bearbeitungs-Modus"])
        
        with admin_sub1:
            st.subheader("Aktueller Team-Status")
            if not df_personal.empty:
                df_p_sort = df_personal.copy()
                df_p_sort['Sort'] = df_p_sort['Rang'].map(lambda x: RANG_CONFIG.get(x, {}).get('order', 99))
                df_p_sort = df_p_sort.sort_values('Sort').drop(columns=['Sort'])
                st.dataframe(style_team_table(df_p_sort, df_abmeldungen), use_container_width=True, height=450)
            
            st.divider()
            st.subheader("Letzte Support-Berichte")
            st.dataframe(load_data(URL_B).iloc[::-1], use_container_width=True)

        with admin_sub2:
            st.subheader("Offene Abmeldungsanträge")
            # Daten frisch laden
            df_a_current = load_data(URL_A)
            
            if df_a_current.empty:
                st.info("Keine Daten in Blatt A gefunden.")
            else:
                # Wir filtern die Zeilen, wo der Status 'Offen' ist
                # .strip() entfernt unsichtbare Leerzeichen, die das Akzeptieren verhindern könnten
                offene = df_a_current[df_a_current['Status'].astype(str).str.strip() == 'Offen']
                
                if offene.empty:
                    st.info("Keine neuen Abmeldungen zum Bearbeiten.")
                else:
                    for idx, row in offene.iterrows():
                        with st.expander(f"📌 Antrag von {row['Name']} ({row['Von']} bis {row['Bis']})"):
                            st.write(f"**Grund:** {row['Grund']}")
                            st.write(f"**Zusatz:** {row.get('Zusatz', 'Kein Zusatz')}")
                            
                            # Der Button nutzt den Index 'idx' aus dem originalen df_a_current
                            if st.button(f"Haken setzen für {row['Name']}", key=f"acc_{idx}"):
                                # Wir setzen den Status exakt auf 'Akzeptiert'
                                df_a_current.at[idx, 'Status'] = 'Akzeptiert'
                                
                                # Das gesamte Sheet aktualisieren
                                payload = {
                                    "sheet": "A", 
                                    "action": "update_all", 
                                    "headers": df_a_current.columns.tolist(), 
                                    "rows": df_a_current.values.tolist()
                                }
                                
                                try:
                                    res = requests.post(WEBHOOK_URL, data=json.dumps(payload))
                                    if res.status_code == 200:
                                        st.success(f"✅ Abmeldung für {row['Name']} wurde gespeichert!")
                                        st.rerun()
                                    else:
                                        st.error("Fehler beim Senden an Google Sheets.")
                                except Exception as e:
                                    st.error(f"Verbindung zum Webhook fehlgeschlagen: {e}")

        with admin_sub3:
            st.subheader("Verwarnung ausstellen")
            with st.form("verwarnung_form", clear_on_submit=True):
                v_target = st.selectbox("Teammitglied wählen", team_liste)
                v_grund = st.text_area("Begründung der Verwarnung")
                v_issuer = st.selectbox("Ausgestellt von", team_liste)
                if st.form_submit_button("Verwarnung rechtskräftig machen"):
                    if v_grund:
                        v_row = [datetime.now().strftime("%d.%m.%Y %H:%M"), v_target, v_grund, v_issuer]
                        requests.post(WEBHOOK_URL, data=json.dumps({"sheet": "V", "row": v_row}))
                        df_p_new = df_personal.copy()
                        df_p_new.loc[df_p_new['Name'] == v_target, 'Verwarnungen'] += 1
                        payload = {"sheet": "P", "action": "update_all", "headers": df_p_new.columns.tolist(), "rows": df_p_new.values.tolist()}
                        requests.post(WEBHOOK_URL, data=json.dumps(payload))
                        st.success(f"⚠️ Verwarnung für {v_target} wurde registriert!")
                        st.rerun()
            st.divider()
            st.subheader("Historie aller Verwarnungen")
            st.dataframe(load_data(URL_V).iloc[::-1], use_container_width=True)

        with admin_sub4:
            st.subheader("Datenbank-Editor")
            edited_p = st.data_editor(df_personal, use_container_width=True, num_rows="dynamic",
                                      column_config={"Rang": st.column_config.SelectboxColumn("Rang", options=list(RANG_CONFIG.keys()))})
            if st.button("Personal-Daten speichern"):
                payload = {"sheet": "P", "action": "update_all", "headers": df_personal.columns.tolist(), "rows": edited_p.values.tolist()}
                requests.post(WEBHOOK_URL, data=json.dumps(payload))
                st.success("✅ Datenbank aktualisiert!")
                st.rerun()

    elif pw != "":
        st.error("Falsches Passwort")
