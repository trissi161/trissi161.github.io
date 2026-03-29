import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

--- CONFIG ---
st.set_page_config(page_title="RDF Team-Panel", page_icon="📝", layout="wide")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1TZHjV7RTrE27p-hapfMe11eCUXhS9QFAd53OCQjpeOc"

--- VERBINDUNG ---
conn = None
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"❌ Verbindung fehlgeschlagen: {e}")

--- LOAD FUNCTION ---
def load_data(sheet_name):
    if conn is None:
        return pd.DataFrame()
    try:
        return conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
    except Exception as e:
        st.error(f"⚠️ Fehler bei '{sheet_name}': {e}")
        return pd.DataFrame()

--- DATEN ---
df_personal = load_data("P")
df_berichte = load_data("B")

if not df_personal.empty and "Name" in df_personal.columns:
    team_liste = df_personal["Name"].dropna().tolist()
else:
    team_liste = ["Keine Daten"]

--- TABS ---
tab_bericht, tab_admin = st.tabs(["📝 Support-Bericht", "🔒 Admin"])

=========================
📝 BERICHT
=========================
with tab_bericht:
    st.header("Support-Bericht")

    with st.form("form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            dein_name = st.selectbox("Name", team_liste)
            spieler = st.text_input("Spieler")
            mitglieder = st.text_area("Beteiligte")

        with col2:
            problem = st.text_area("Problem")
            massnahmen = st.text_area("Maßnahmen")
            begruendung = st.text_area("Begründung")

        clips = st.text_area("Beweise")

        if st.form_submit_button("Speichern"):
            if not spieler or not problem:
                st.warning("⚠️ Spieler + Problem nötig!")
            else:
                neuer = pd.DataFrame([{
                    "Zeitpunkt": datetime.now().strftime("%d.%m.%Y %H:%M"),
                    "Ersteller": dein_name,
                    "Spieler": spieler,
                    "Beteiligte": mitglieder,
                    "Problem": problem,
                    "Massnahmen": massnahmen,
                    "Begruendung": begruendung,
                    "Beweise": clips
                }])

                try:
                    df_alt = load_data("B")
                    df_neu = pd.concat([df_alt, neuer], ignore_index=True)

                    conn.update(
                        spreadsheet=SHEET_URL,
                        worksheet="B",
                        data=df_neu
                    )

                    st.success("✅ Gespeichert!")
                except Exception as e:
                    st.error(f"❌ Fehler: {e}")

=========================
🔒 ADMIN
=========================
with tab_admin:
    pw = st.text_input("Passwort", type="password")

    if pw == "2504":
        wahl = st.radio("Bereich", ["Berichte", "Personal"])

        if wahl == "Berichte":
            st.dataframe(load_data("B"), use_container_width=True)

        else:
            df_p = load_data("P")
            edited = st.data_editor(df_p, num_rows="dynamic")

            if st.button("Speichern"):
                conn.update(
                    spreadsheet=SHEET_URL,
                    worksheet="P",
                    data=edited
                )
                st.success("✅ Aktualisiert!")
