import streamlit as st
import requests
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from io import BytesIO
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- KONFIGURATION ---
st.set_page_config(page_title="Team Management Falkenfurt", page_icon="👾", layout="wide")

# Verbindung zu Google Sheets (Nutzt die Daten aus deinen Secrets)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Fehler bei der Verbindung zu Google Sheets. Prüfe deine Secrets!")

# --- PDF KLASSEN (Urkunden & HR) ---
# [Hier bleiben deine Klassen RDF_Urkunden_Master, Falkenfurt_HR_Master etc. wie sie waren]
# (Ich kürze das hier ab, damit der Code übersichtlich bleibt - behalte deine Klassen einfach bei!)

class RDF_Urkunden_Master(FPDF):
    def draw_border(self):
        self.set_line_width(1.5)
        self.set_draw_color(0, 14, 43) 
        self.rect(10, 10, 277, 190) 
        self.set_line_width(0.5)
        self.set_draw_color(255, 215, 0) 
        self.rect(13, 13, 271, 184) 

    def generate_pdf(self, name, geburtsdatum, datum, aussteller, typ_daten, extra_pos=None):
        self.add_page(orientation='L')
        self.set_auto_page_break(auto=False)
        self.draw_border()
        logo_url = "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Bild_2026-03-24_235639621.png"
        try:
            resp = requests.get(logo_url, timeout=5)
            self.image(BytesIO(resp.content), x=128, y=12, w=40) 
        except: pass
        self.set_y(75)
        self.set_font('Helvetica', 'B', 38)
        self.set_text_color(0, 14, 43)
        self.cell(0, 15, 'URKUNDE' if typ_daten['titel'] != "SUSPENDIERUNG" else "DOKUMENT", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', 'B', 26)
        self.cell(0, 12, name.upper(), align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', 'I', 13)
        self.cell(0, 8, f'geboren am {geburtsdatum}', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)
        self.set_font('Helvetica', '', 11.5)
        self.set_text_color(30, 30, 30)
        self.set_left_margin(35)
        self.set_right_margin(35)
        self.multi_cell(0, 5.5, typ_daten['text_oben'], align='C')
        self.ln(2)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(0, 14, 43)
        anzeige_titel = extra_pos if extra_pos else typ_daten['titel']
        self.cell(0, 12, anzeige_titel.upper(), align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)
        self.set_font('Helvetica', '', 11)
        self.multi_cell(0, 5.5, typ_daten['text_unten'], align='C')
        try:
            resp_sig = requests.get(aussteller['sig_url'], timeout=5)
            self.image(BytesIO(resp_sig.content), x=185, y=145, w=65)
        except: pass
        self.set_draw_color(0, 14, 43)
        self.line(185, 175, 270, 175) 
        self.set_xy(185, 176) 
        self.set_font('Helvetica', 'B', 10)
        info = f"{aussteller['name']}\n{aussteller['amt']}\nFalkenfurt, den {datum}"
        self.multi_cell(85, 4.5, info, align='C')
        return self.output(dest='S')

# [Füge hier deine anderen PDF Klassen wie Falkenfurt_HR_Master ein...]

# --- HAUPT-TABS ---
tab_panel, tab_urkunden, tab_hr = st.tabs(["👥 Team-Panel", "📜 Urkunden", "📂 HR-Dokumente"])

# ==========================================
# 1. TAB: TEAM-PANEL (Google Sheets)
# ==========================================
with tab_panel:
    st.header("RDF Team-Dashboard")
    
    # Daten laden
    try:
        df_personal = conn.read(worksheet="Personal")
        df_berichte = conn.read(worksheet="Berichte")
    except:
        st.warning("Konnte Daten nicht laden. Prüfe die Tabellenblatt-Namen (Personal/Berichte)!")
        df_personal = pd.DataFrame(columns=["Name", "Rang", "Verwarnungen"])
        df_berichte = pd.DataFrame(columns=["Zeitpunkt", "Supporter", "FallID", "Bericht", "Status"])

    sub_nav = st.radio("Aktion wählen:", ["Support-Bericht schreiben", "Admin-Bereich"], horizontal=True)

    if sub_nav == "Support-Bericht schreiben":
        with st.form("support_form"):
            supporter_name = st.selectbox("Dein Name", df_personal["Name"].tolist() if not df_personal.empty else ["Keine Daten"])
            fall_id = st.text_input("Fall-ID")
            bericht_text = st.text_area("Was ist vorgefallen?")
            status_fall = st.selectbox("Status", ["Geklärt", "Offen", "Eskaliert"])
            
            if st.form_submit_button("Bericht absenden"):
                neuer_eintrag = pd.DataFrame([{
                    "Zeitpunkt": datetime.now().strftime("%d.%m.%Y %H:%M"),
                    "Supporter": supporter_name,
                    "FallID": fall_id,
                    "Bericht": bericht_text,
                    "Status": status_fall
                }])
                df_neu = pd.concat([df_berichte, neuer_eintrag], ignore_index=True)
                conn.update(worksheet="Berichte", data=df_neu)
                st.success("Bericht gespeichert!")

    elif sub_nav == "Admin-Bereich":
        pw = st.text_input("Admin-Passwort", type="password")
        if pw == "2504":
            st.subheader("Mitarbeiterliste & Verwarnungen")
            # Hier kann die Leitung editieren
            edited_personal = st.data_editor(df_personal, num_rows="dynamic")
            if st.button("Personal-Änderungen speichern"):
                conn.update(worksheet="Personal", data=edited_personal)
                st.success("Personal-Daten aktualisiert!")
            
            st.divider()
            st.subheader("Alle Support-Berichte")
            st.dataframe(df_berichte, use_container_width=True)
        elif pw != "":
            st.error("Falsches Passwort!")

# ==========================================
# 2. TAB: URKUNDEN (Dein alter Code)
# ==========================================
with tab_urkunden:
    # [Hier fügst du deinen bisherigen Urkunden-Code ein]
    st.write("Hier kommen deine Urkunden-Optionen rein...")

# ==========================================
# 3. TAB: HR (Dein alter Code)
# ==========================================
with tab_hr:
    # [Hier fügst du deinen bisherigen HR-Code ein]
    st.write("Hier kommen deine HR-Optionen rein...")
