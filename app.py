import streamlit as st
import requests
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from io import BytesIO
from datetime import datetime

# --- KLASSE 1: URKUNDEN (QUERFORMAT) ---
class RDF_Urkunden_Master(FPDF):
    def draw_border(self):
        self.set_line_width(1.5); self.set_draw_color(0, 14, 43) 
        self.rect(10, 10, 277, 190) 
        self.set_line_width(0.5); self.set_draw_color(255, 215, 0) 
        self.rect(13, 13, 271, 184) 

    def generate_pdf(self, name, geburtsdatum, datum, aussteller, typ_daten, extra_pos=None):
        self.add_page(orientation='L')
        self.set_auto_page_break(auto=False)
        self.draw_border()
        logo_url = "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/logo.png"
        try:
            resp = requests.get(logo_url, timeout=5)
            self.image(BytesIO(resp.content), x=126, y=12, w=45) 
        except: pass
        self.set_y(55); self.set_font('Helvetica', 'B', 38); self.set_text_color(0, 14, 43)
        self.cell(0, 15, 'URKUNDE', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', 'B', 26)
        self.cell(0, 12, name.upper(), align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', 'I', 13)
        self.cell(0, 8, f'geboren am {geburtsdatum}', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2); self.set_font('Helvetica', '', 11.5); self.set_text_color(30, 30, 30)
        self.set_left_margin(35); self.set_right_margin(35)
        self.multi_cell(0, 5.5, typ_daten['text_oben'], align='C')
        self.ln(2); self.set_font('Helvetica', 'B', 24); self.set_text_color(0, 14, 43)
        anzeige_titel = extra_pos if extra_pos else typ_daten['titel']
        self.cell(0, 12, anzeige_titel.upper(), align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2); self.set_font('Helvetica', '', 11)
        self.multi_cell(0, 5.5, typ_daten['text_unten'], align='C')
        try:
            resp_sig = requests.get(aussteller['sig_url'], timeout=5)
            self.image(BytesIO(resp_sig.content), x=185, y=148, w=65)
        except: pass
        self.set_draw_color(0, 14, 43); self.line(185, 175, 270, 175) 
        self.set_xy(185, 176); self.set_font('Helvetica', 'B', 10)
        info = f"{aussteller['name']}\n{aussteller['amt']}\nFalkenfurt, den {datum}"
        self.multi_cell(85, 4.5, info, align='C')
        return self.output(dest='S')

# --- KLASSE 2: PERSONALWESEN (HOCHFORMAT) ---
class Falkenfurt_HR_Master(FPDF):
    def header(self):
        self.set_fill_color(0, 14, 43); self.rect(0, 0, 210, 45, 'F')
        logo_url = "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/logo.png"
        try:
            resp = requests.get(logo_url)
            self.image(BytesIO(resp.content), x=15, y=5, h=35)
        except: pass
        self.set_text_color(255, 255, 255); self.set_font('Helvetica', 'B', 20)
        self.set_xy(70, 12); self.cell(0, 10, "RETTUNGSDIENST")
        self.set_xy(70, 22); self.cell(0, 10, "FALKENFURT")
        self.set_text_color(255, 215, 0); self.set_font('Helvetica', 'B', 12)
        self.set_xy(70, 35); self.cell(0, 5, "PERSONALABTEILUNG / DIENSTLEITUNG")

    def generate_kuendigung(self, d):
        self.add_page(); self.set_top_margin(60)
        self.ln(20); self.set_font('Helvetica', 'B', 16); self.set_text_color(0, 14, 43)
        self.cell(0, 10, "KÜNDIGUNG DES ARBEITSVERHÄLTNISSES", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', '', 10); self.cell(0, 10, f"Datum: {d['datum_heute']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10); self.set_font('Helvetica', '', 11); self.set_text_color(0, 0, 0)
        text = (f"Sehr geehrte/r Frau/Herr {d['name_empfaenger']},\n\nhiermit kündigen wir das mit Ihnen bestehende Arbeitsverhältnis ordentlich unter Einhaltung der vertraglich vereinbarten Kündigungsfrist zum {d['datum_ende']}.\n\nHilfsweise kündigen wir zum nächstmöglichen Termin.\n\nWir weisen Sie ausdrücklich darauf hin, dass Sie gemäß § 38 Abs. 1 SGB III verpflichtet sind, sich spätestens drei Monate vor Beendigung arbeitssuchend zu melden.\n\nBitte geben Sie sämtliche Ausrüstungsgegenstände bis spätestens zu Ihrem letzten Arbeitstag ab.\n\nFür Ihren weiteren Weg wünschen wir Ihnen alles Gute.")
        self.multi_cell(0, 7, text)
        y_linie = 245
        self.set_font('Courier', 'I', 14); self.set_text_color(0, 32, 96); self.set_xy(15, y_linie - 12) 
        self.cell(70, 10, d['bearbeiter_name'], align='C')
        self.line(15, y_linie, 85, y_linie); self.set_text_color(0, 0, 0); self.set_font('Helvetica', 'B', 10)
        self.set_xy(15, y_linie + 2); self.cell(70, 7, d['bearbeiter_name'], align='C')
        self.set_font('Helvetica', '', 8); self.set_xy(15, y_linie + 7); self.cell(70, 5, "Personalabteilung", align='C')
        try:
            sig_url = "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Unterschriftleon.png"
            resp = requests.get(sig_url); self.image(BytesIO(resp.content), x=125, y=y_linie - 28, h=50) 
        except: pass
        self.line(115, y_linie, 185, y_linie); self.set_font('Helvetica', 'B', 10)
        self.set_xy(115, y_linie + 2); self.cell(70, 7, "Dr. med. Leon Müller", align='C')
        self.set_font('Helvetica', '', 8); self.set_xy(115, y_linie + 7); self.cell(70, 5, "Geschäftsführung", align='C')
        return self.output(dest='S')

# --- DATEN ---
aussteller_liste = {
    "Dr. med. Leon Müller (Geschäftsführer)": {"name": "Dr. med. Leon Müller", "amt": "Geschäftsführer", "sig_url": "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Unterschriftleon.png"},
    "Dr. med. Leon Müller (ÄLRD)": {"name": "Dr. med. Leon Müller", "amt": "Ärztlicher Leiter Rettungsdienst", "sig_url": "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Unterschriftleon.png"},
    "Thomas Schäfer (Leiter RD)": {"name": "Thomas Schäfer", "amt": "Leiter Rettungsdienst", "sig_url": "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Thomas.png"}
}
urkundentypen = {
    "Rettungssanitäter": {"titel": "RETTUNGSSANITÄTER", "text_oben": "hat am heutigen Tage die Prüfung zur Anerkennung als RS erfolgreich abgelegt...", "text_unten": "Diese Urkunde berechtigt zur Wahrnehmung der Aufgaben..."},
    "Notfallsanitäter": {"titel": "NOTFALLSANITÄTER", "text_oben": "hat am heutigen Tage die Prüfung zur Anerkennung als NFS erfolgreich abgelegt...", "text_unten": "Diese Urkunde berechtigt zur Leitung medizinischer Erstversorgung..."},
    "Ernennung": {"titel": "POSITION", "text_oben": "wird am heutigen Tage ernannt...", "text_unten": "Diese Urkunde berechtigt zur Führung des Fachbereiches..."}
}
ernennungs_rollen = ["Wachleiter", "Leiter Rettungsdienstschule", "Leiter Rettungsdienst", "Personalabteilungsleitung"]

# --- APP LAYOUT ---
st.set_page_config(page_title="RDF Verwaltung", page_icon="🚑", layout="centered")

tab1, tab2 = st.tabs(["🎓 Urkunden-Zentrum", "📋 Personalwesen (HR)"])

# --- TAB 1: URKUNDEN ---
with tab1:
    st.header("Urkunden-Generator")
    with st.sidebar:
        st.subheader("Urkunden-Settings")
        wahl_typ = st.selectbox("Typ", list(urkundentypen.keys()))
        extra_pos = st.selectbox("Position", ernennungs_rollen) if wahl_typ == "Ernennung" else None
        wahl_boss = st.selectbox("Aussteller", list(aussteller_liste.keys()))
    
    with st.form("u_form"):
        col1, col2 = st.columns(2)
        u_name = col1.text_input("Name")
        u_geb = col2.text_input("Geburtsdatum")
        u_datum = st.date_input("Datum", value=datetime.now()).strftime("%d.%m.%Y")
        if st.form_submit_button("Urkunde erstellen"):
            if u_name and u_geb:
                pdf = RDF_Urkunden_Master()
                out = pdf.generate_pdf(u_name, u_geb, u_datum, aussteller_liste[wahl_boss], urkundentypen[wahl_typ], extra_pos)
                st.download_button("⬇️ Download Urkunde", data=bytes(out), file_name="Urkunde.pdf")

# --- TAB 2: HR DOKUMENTE ---
with tab2:
    st.header("HR Dokumente & Kündigungen")
    hr_typ = st.selectbox("Dokumenten-Typ", ["Kündigungsschreiben"])
    
    if hr_typ == "Kündigungsschreiben":
        with st.form("hr_form"):
            name_e = st.text_input("Name des Mitarbeiters")
            bearbeiter = st.text_input("Dein Name (Personalabteilung)")
            colA, colB = st.columns(2)
            d_heute = colA.date_input("Heutiges Datum", value=datetime.now()).strftime("%d.%m.%Y")
            d_ende = colB.date_input("Kündigungstermin zum", value=datetime.now()).strftime("%d.%m.%Y")
            
            if st.form_submit_button("Kündigung generieren"):
                if name_e and bearbeiter:
                    pdf_hr = Falkenfurt_HR_Master()
                    d = {'name_empfaenger': name_e, 'bearbeiter_name': bearbeiter, 'datum_heute': d_heute, 'datum_ende': d_ende}
                    out_hr = pdf_hr.generate_kuendigung(d)
                    st.download_button("⬇️ Download Kündigung", data=bytes(out_hr), file_name=f"Kuendigung_{name_e}.pdf")
