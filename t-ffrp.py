import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import time 
import pytz
berlin_tz = pytz.timezone("Europe/Berlin")

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
URL_D = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=D"

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
    """Ermittelt nur das Emoji für den Status."""
    if df_a.empty: return "🟢"
    now = datetime.now().date()
    suche_name = str(name).strip().lower()
    aktive_a = df_a[(df_a['Status'].astype(str).str.strip() == 'Akzeptiert')].copy()
    for _, row in aktive_a.iterrows():
        if str(row['Name']).strip().lower() == suche_name:
            try:
                start = pd.to_datetime(row['Von']).date()
                ende = pd.to_datetime(row['Bis']).date()
                if start <= now <= ende: return "🔴"
                elif now < start <= (now + timedelta(days=2)): return "🟡"
            except: continue
    return "🟢"

def style_team_table(df, df_a):
    if df.empty: return df
    status_emojis = [get_status_info(n, df_a) for n in df['Name']]
    df_styled = df.copy()
    if "Status" not in df_styled.columns:
        df_styled.insert(0, "Status", status_emojis)
    
    def apply_row_styles(row):
        rank = row['Rang']
        rank_color = RANG_CONFIG.get(rank, {}).get('color', '#ffffff')
        st_emoji = get_status_info(row['Name'], df_a)
        styles = []
        for col in row.index:
            if col == "Status": styles.append('text-align: center; font-size: 1.2rem;')
            elif col in ['Name', 'Rang']:
                opacity = "0.4" if st_emoji == "🔴" else "1.0"
                styles.append(f'color: {rank_color}; font-weight: bold; opacity: {opacity};')
            elif col == 'Verwarnungen' and 'Verwarnungen' in row:
                try:
                    v = int(row['Verwarnungen'])
                    v_c = '#2ecc71' if v == 0 else '#f1c40f' if v == 1 else '#e67e22' if v == 2 else '#e74c3c'
                    styles.append(f'color: {v_c}; font-weight: bold;')
                except: styles.append('color: #d1d1d1;')
            else: styles.append('color: #d1d1d1;')
        return styles
    return df_styled.style.apply(apply_row_styles, axis=1)

# --- DATEN LADEN ---
df_personal = load_data(URL_P)
df_abmeldungen = load_data(URL_A)
team_liste = df_personal["Name"].dropna().tolist() if not df_personal.empty else ["Lade Fehler..."]

tab_bericht, tab_admin = st.tabs(["📝 Team-Bereich", "🔒 High-Team-Bereich"])

# ==========================================
# 1. TAB: TEAM-BEREICH
# ==========================================
with tab_bericht:
    sub_tab1, sub_tab2 = st.tabs(["Support Berichte", "Abmeldungen"])
    
    with sub_tab1:
        st.header("Support-Bericht einreichen")
        with st.form("support_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.selectbox("Dein Name", team_liste, key="sb_name")
                spieler = st.text_input("Spieler (Discord Username)")
                andere_teamler = [t for t in team_liste if t != name]
                beteiligte = st.multiselect(
                    "Andere beteiligte Teamler", 
                    options=andere_teamler,
                    help="Wähle alle Teammitglieder aus, die dabei waren."
                )
                
            with c2:
                problem = st.text_area("Problem")
                massnahmen = st.text_area("Maßnahmen")
                begruendung = st.text_area("Begründung")
            
            clips = st.text_area("Beweise (Clips / Zeugen / Bilder)")
            
            if st.form_submit_button("Bericht absenden"):
                beteiligte_text = ", ".join(beteiligte) if beteiligte else "Keine"
                
                row_data = [
                    datetime.now(berlin_tz).strftime("%d.%m.%Y %H:%M"), 
                    name, 
                    spieler, 
                    beteiligte_text, 
                    problem, 
                    massnahmen, 
                    begruendung, 
                    clips
                ]
                
                try:
                    res = requests.post(WEBHOOK_URL, data=json.dumps({"sheet": "B", "row": row_data}))
                    if res.status_code == 200:
                        st.success("✅ Bericht gespeichert!")
                    else:
                        st.error("Fehler beim Senden.")
                except Exception as e:
                    st.error(f"Verbindung fehlgeschlagen: {e}")

    with sub_tab2:
        st.header("Abmeldung beantragen")
        with st.form("loa_form", clear_on_submit=True):
            a_name = st.selectbox("Dein Name", team_liste, key="loa_name")
            a_grund = st.text_area("Grund der Abmeldung")
            col1, col2 = st.columns(2)
            with col1: a_von = st.date_input("Von", datetime.now())
            with col2: a_bis = st.date_input("Bis", datetime.now() + timedelta(days=7))
            a_zusatz = st.text_input("Zusatz (z.B. Erreichbarkeit via DC)")
            
            if st.form_submit_button("Abmeldung absenden"):
                loa_row = [
                    datetime.now(berlin_tz).strftime("%d.%m.%Y %H:%M"), 
                    a_name, a_grund, str(a_von), str(a_bis), a_zusatz, "Offen"]
                requests.post(WEBHOOK_URL, data=json.dumps({"sheet": "A", "row": loa_row}))
                st.success("✅ Abmeldung eingereicht!")

        st.divider()
        st.subheader("📊 Aktuelle Team-Verfügbarkeit")
        if not df_personal.empty:
            df_status_view = df_personal.copy()
            df_status_view['Sort'] = df_status_view['Rang'].map(lambda x: RANG_CONFIG.get(x, {}).get('order', 99))
            df_status_view = df_status_view.sort_values('Sort')[['Name', 'Rang']]
            st.dataframe(style_team_table(df_status_view, df_abmeldungen), use_container_width=True, height=400, hide_index=True)
            st.info("💡 **Legende:** 🟢 Anwesend | 🟡 Bald abwesend | 🔴 Abwesend")

# ==========================================
# 2. TAB: ADMIN-BEREICH
# ==========================================
with tab_admin:
    st.header("Admin-Verwaltung")
    pw = st.text_input("Passwort", type="password")
    
    if pw == "2504":
        admin_sub1, admin_sub2, admin_sub3, admin_sub4, admin_sub5 = st.tabs(["📊 Team-Übersicht", "✅ Abmeldungen prüfen", "⚠️ Verwarnungen", "🛠 Bearbeitungs-Modus", "🔃 Rangänderungen"])
        
        with admin_sub1:
            st.subheader("Aktueller Team-Status")
            if not df_personal.empty:
                df_p_sort = df_personal.copy()
                df_p_sort['Sort'] = df_p_sort['Rang'].map(lambda x: RANG_CONFIG.get(x, {}).get('order', 99))
                df_p_sort = df_p_sort.sort_values('Sort').drop(columns=['Sort'])
                st.dataframe(style_team_table(df_p_sort, df_abmeldungen), use_container_width=True, height=350, hide_index=True)
                st.caption("🟢 Anwesend | 🟡 Bald weg | 🔴 Abwesend")
            
            st.divider()
            
            # --- Statistiken ---
            df_berichte = load_data(URL_B)
            
            if not df_berichte.empty:
                df_berichte.columns = df_berichte.columns.str.strip()
                
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    st.subheader("📈 Berichte (14 Tage)")
                    time_col = 'Zeitpunkt' if 'Zeitpunkt' in df_berichte.columns else df_berichte.columns[0]
                    
                    df_stats_time = df_berichte.copy()
                    df_stats_time['Datum'] = pd.to_datetime(df_stats_time[time_col], dayfirst=True).dt.date
                    
                    # 1. Zeitraum festlegen (mit Berlin-Zeit)
                    heute = datetime.now(berlin_tz).date()
                    vor_14_tagen = heute - timedelta(days=14)
                    
                    # 2. Vollständigen Bereich erstellen
                    alle_tage = pd.date_range(start=vor_14_tagen, end=heute).date
                    df_final = pd.DataFrame({'Datum': alle_tage})
                    
                    # 3. Echte Daten zählen
                    df_counts = df_stats_time[df_stats_time['Datum'] >= vor_14_tagen]
                    daily_counts = df_counts.groupby('Datum').size().reset_index(name='Berichte')
                    
                    # 4. Merge & Sortierung sicherstellen
                    df_final = pd.merge(df_final, daily_counts, on='Datum', how='left').fillna(0)
                    df_final['Berichte'] = df_final['Berichte'].astype(int)
                    df_final = df_final.sort_values('Datum') # WICHTIG: Chronologisch sortieren

                    if not df_final.empty:
                        # TRICK: Wir nutzen altair direkt für das Line-Chart. 
                        # Das behält die zeitliche Sortierung bei, auch bei Monatswechseln.
                        import altair as alt
                        
                        line_chart = alt.Chart(df_final).mark_line(color="#ff4b4b", point=True).encode(
                            x=alt.X('Datum:T', title='Datum', axis=alt.Axis(format='%d.%m.', labelAngle=-45)),
                            # tickCount steuert, wie viele Labels maximal angezeigt werden
                            y=alt.Y('Berichte:Q', title='Anzahl', axis=alt.Axis(tickMinStep=1, format='d', tickCount=df_final['Berichte'].max() + 1)),
                            tooltip=['Datum', 'Berichte']
                        ).properties(height=300)
                        
                        st.altair_chart(line_chart, use_container_width=True)
                    else:
                        st.info("Keine Daten für diesen Zeitraum.")

                with col_chart2:
                    st.subheader("🏆 Top Supporter (Gesamt)")
                    if 'Ersteller' in df_berichte.columns:
                        supporter_counts = df_berichte['Ersteller'].value_counts().reset_index()
                        supporter_counts.columns = ['Ersteller', 'Anzahl']
                        top_supporter = supporter_counts.head(10).sort_values(by='Anzahl', ascending=False)
                        
                        if not top_supporter.empty:
                            import altair as alt
                            chart = alt.Chart(top_supporter).mark_bar(color="#2ecc71").encode(
                                x=alt.X('Anzahl:Q', title='Anzahl Berichte', axis=alt.Axis(format='d')),
                                y=alt.Y('Ersteller:N', sort='-x', title='Supporter'),
                            ).properties(height=300)
                            st.altair_chart(chart, use_container_width=True)
                    else:
                        st.error("Spalte 'Ersteller' nicht gefunden!")
            
                st.divider()
                st.subheader("📋 Letzte Support-Berichte")
                # Hier ist die Tabelle wieder! iloc[::-1] dreht sie um, damit die neuesten oben stehen.
                st.dataframe(df_berichte.iloc[::-1], use_container_width=True, height=400, hide_index=True)
            else:
                st.info("Noch keine Berichts-Daten vorhanden.")

        with admin_sub2:
            st.subheader("Offene Abmeldungsanträge")
            df_a_current = pd.read_csv(f"{URL_A}&cachebust={datetime.now().timestamp()}")
            df_a_current['Status'] = df_a_current['Status'].astype(str).str.strip()
            
            # Neue Anträge
            offene = df_a_current[df_a_current['Status'] == 'Offen']
            if offene.empty:
                st.info("Keine neuen Abmeldungen.")
            else:
                for idx, row in offene.iterrows():
                    with st.expander(f"📌 Antrag von {row['Name']} ({row['Von']} - {row['Bis']})"):
                        st.write(f"Grund: {row['Grund']}")
                        if st.button(f"Akzeptieren: {row['Name']}", key=f"acc_{idx}"):
                            df_a_current.at[idx, 'Status'] = 'Akzeptiert'
                            payload = {"sheet": "A", "action": "update_all", "headers": df_a_current.columns.tolist(), "rows": df_a_current.fillna("").values.tolist()}
                            requests.post(WEBHOOK_URL, data=json.dumps(payload))
                            st.success("Akzeptiert!")
                            time.sleep(1)
                            st.rerun()

            st.divider()
            st.subheader("Aktive Abmeldungen verwalten")
            akzeptiert = df_a_current[df_a_current['Status'] == 'Akzeptiert'].copy()
            if not akzeptiert.empty:
                akzeptiert.insert(0, "Löschen", False)
                edited_a = st.data_editor(akzeptiert, column_config={"Löschen": st.column_config.CheckboxColumn(default=False)}, disabled=["Zeitpunkt", "Name", "Von", "Bis", "Status"], use_container_width=True, hide_index=True)
                
                if st.button("Ausgewählte Abmeldungen abbrechen"):
                    to_delete = edited_a[edited_a["Löschen"] == True]
                    for _, d_row in to_delete.iterrows():
                        df_a_current = df_a_current[~((df_a_current['Name'] == d_row['Name']) & (df_a_current['Zeitpunkt'] == d_row['Zeitpunkt']))]
                    payload = {"sheet": "A", "action": "update_all", "headers": df_a_current.columns.tolist(), "rows": df_a_current.fillna("").values.tolist()}
                    requests.post(WEBHOOK_URL, data=json.dumps(payload))
                    st.success("Aktualisiert!")
                    time.sleep(1)
                    st.rerun()

        with admin_sub3:
            st.subheader("Verwarnung ausstellen")
            with st.form("verwarnung_form", clear_on_submit=True):
                v_target = st.selectbox("Mitglied", team_liste)
                v_grund = st.text_area("Grund")
                v_issuer = st.selectbox("Von", team_liste)
                if st.form_submit_button("Senden"):
                    v_row = [
                        datetime.now(berlin_tz).strftime("%d.%m.%Y %H:%M"), 
                        v_target, v_grund, v_issuer]
                    requests.post(WEBHOOK_URL, data=json.dumps({"sheet": "V", "row": v_row}))
                    
                    df_p_new = df_personal.copy()
                    df_p_new['Verwarnungen'] = pd.to_numeric(df_p_new['Verwarnungen'], errors='coerce').fillna(0)
                    df_p_new.loc[df_p_new['Name'] == v_target, 'Verwarnungen'] += 1
                    
                    requests.post(WEBHOOK_URL, data=json.dumps({"sheet": "P", "action": "update_all", "headers": df_p_new.columns.tolist(), "rows": df_p_new.values.tolist()}))
                    st.success(f"✅ Verwarnung für {v_target} wurde registriert!")
                    time.sleep(1)
                    st.rerun()

            st.divider()
            st.subheader("📜 Historie der Verwarnungen")
            
            # Daten aus Blatt V laden
            df_verwarnungen = load_data(URL_V)
            
            if not df_verwarnungen.empty:
                df_verwarnungen.columns = df_verwarnungen.columns.str.strip()
                st.dataframe(
                    df_verwarnungen.iloc[::-1], 
                    use_container_width=True, 
                    hide_index=True
                )
            else:
                st.info("Bisher wurden keine Verwarnungen ausgesprochen.")

        with admin_sub4:
            st.subheader("Datenbank-Editor")
            edited_p = st.data_editor(df_personal, use_container_width=True, num_rows="dynamic", column_config={"Rang": st.column_config.SelectboxColumn("Rang", options=list(RANG_CONFIG.keys()))})
            if st.button("Speichern"):
                requests.post(WEBHOOK_URL, data=json.dumps({"sheet": "P", "action": "update_all", "headers": df_personal.columns.tolist(), "rows": edited_p.values.tolist()}))
                st.success("Gespeichert!")
                st.rerun()

        with admin_sub5: 
            st.subheader("Team-Rang Änderung protokollieren")

            # 1. Auswahl des Mitglieds (AUSSERHALB des Formulars für Live-Update)
            d_target = st.selectbox("Mitglied auswählen", team_liste, key="dr_target")

            # Aktuellen Rang live aus den Daten ziehen
            if not df_personal.empty and d_target:
                aktueller_rang = df_personal[df_personal['Name'] == d_target]['Rang'].values[0]
                st.info(f"Aktueller Rang von **{d_target}**: `{aktueller_rang}`")
            else:
                aktueller_rang = "Unbekannt"

            # 2. Das Formular für die restlichen Daten
            with st.form("derank_form", clear_on_submit=True):
                alle_raenge = list(RANG_CONFIG.keys())
                d_new_rank = st.selectbox("Neuer Rang", alle_raenge)
                
                d_grund = st.text_area("Grund für die Änderung")
                d_issuer = st.selectbox("Ausgeführt von (Admin)", team_liste, key="derank_admin")
                
                if st.form_submit_button("Rang-Änderung speichern & protokollieren"):
                    if d_target and d_grund and d_new_rank != aktueller_rang:
                        derank_log = [
                            datetime.now(berlin_tz).strftime("%d.%m.%Y %H:%M"),
                            d_target,
                            aktueller_rang,
                            d_new_rank,
                            d_grund,
                            d_issuer
                        ]
                        
                        # Personal-Datenblatt 'P' lokal aktualisieren
                        df_p_updated = df_personal.copy()
                        df_p_updated.loc[df_p_updated['Name'] == d_target, 'Rang'] = d_new_rank
                        
                        try:
                            # Sende Protokoll an Blatt D
                            requests.post(WEBHOOK_URL, data=json.dumps({"sheet": "D", "row": derank_log}))
                            
                            # Update das Personalblatt P
                            payload_p = {
                                "sheet": "P", 
                                "action": "update_all", 
                                "headers": df_p_updated.columns.tolist(), 
                                "rows": df_p_updated.fillna("").values.tolist()
                            }
                            requests.post(WEBHOOK_URL, data=json.dumps(payload_p))
                            
                            st.success(f"✅ {d_target} wurde erfolgreich auf {d_new_rank} gesetzt!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Fehler: {e}")
                    elif d_new_rank == aktueller_rang:
                        st.warning("Der gewählte Rang ist identisch mit dem aktuellen Rang.")
                    else:
                        st.warning("Bitte alle Felder ausfüllen.")

            st.divider()
            st.subheader("📜 Historie der Rang-Änderungen")
            df_deranks = load_data(URL_D)
            if not df_deranks.empty:
                st.dataframe(df_deranks.iloc[::-1], use_container_width=True, hide_index=True)
