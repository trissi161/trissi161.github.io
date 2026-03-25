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

# --- KLASSE 2: HR DOKUMENTE (HOCHFORMAT) ---
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

    def footer_sigs(self, bearbeiter_name):
        y_linie = 245
        self.set_font('Courier', 'I', 14); self.set_text_color(0, 32, 96); self.set_xy(15, y_linie - 12) 
        self.cell(70, 10, bearbeiter_name, align='C')
        self.set_draw_color(0, 0, 0); self.line(15, y_linie, 85, y_linie)
        self.set_text_color(0, 0, 0); self.set_font('Helvetica', 'B', 10)
        self.set_xy(15, y_linie + 2); self.cell(70, 7, bearbeiter_name, align='C')
        self.set_font('Helvetica', '', 8); self.set_xy(15, y_linie + 7); self.cell(70, 5, "Personalabteilung", align='C')
        try:
            sig_url = "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Unterschriftleon.png"
            resp = requests.get(sig_url); self.image(BytesIO(resp.content), x=125, y=y_linie - 28, h=50) 
        except: pass
        self.line(115, y_linie, 185, y_linie); self.set_font('Helvetica', 'B', 10)
        self.set_xy(115, y_linie + 2); self.cell(70, 7, "Dr. med. Leon Müller", align='C')
        self.set_font('Helvetica', '', 8); self.set_xy(115, y_linie + 7); self.cell(70, 5, "Geschäftsführung", align='C')

    def generate_doc(self, titel, text, d):
        self.add_page(); self.set_top_margin(60)
        self.ln(20); self.set_font('Helvetica', 'B', 16); self.set_text_color(0, 14, 43)
        self.cell(0, 10, titel, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', '', 10); self.cell(0, 10, f"Datum: {d['datum_heute']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10); self.set_font('Helvetica', '', 11); self.set_text_color(0, 0, 0)
        self.multi_cell(0, 7, text)
        self.footer_sigs(d['bearbeiter_name'])
        return self.output(dest='S')

# --- KONFIGURATION ---
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

# --- APP ---
st.set_page_config(page_title="RDF Verwaltung", page_icon="🚑", layout="centered")
t1, t2 = st.tabs(["🎓 Urkunden-Zentrum", "📋 Personalwesen (HR)"])

with t1:
    st.header("Urkunden-Generator")
    with st.sidebar:
        st.subheader("Urkunden-Settings")
        wahl_typ = st.selectbox("Typ", list(urkundentypen.keys()))
        extra_pos = st.selectbox("Position", ernennungs_rollen) if wahl_typ == "Ernennung" else None
        wahl_boss = st.selectbox("Aussteller", list(aussteller_liste.keys()))
    
    with st.form("u_form"):
        c1, c2 = st.columns(2)
        u_name = c1.text_input("Name")
        u_geb = c2.text_input("Geburtsdatum")
        u_datum = st.date_input("Datum", value=datetime.now()).strftime("%d.%m.%Y")
        if st.form_submit_button("Urkunde erstellen"):
            pdf = RDF_Urkunden_Master()
            out = pdf.generate_pdf(u_name, u_geb, u_datum, aussteller_liste[wahl_boss], urkundentypen[wahl_typ], extra_pos)
            st.download_button("⬇️ Download Urkunde", data=bytes(out), file_name="Urkunde.pdf")

with t2:
    st.header("HR Dokumenten-Management")
    hr_wahl = st.selectbox("Dokument wählen", ["Kündigung (Angestellt)", "Kündigung (Azubi)", "Abmahnung"])
    
    # Wir bereiten eine Variable für das PDF vor
    pdf_data = None
    pdf_filename = "Dokument.pdf"

    with st.form("hr_form_universal"):
        empfaenger = st.text_input("Name des Empfängers")
        bearbeiter = st.text_input("Dein Name (Unterschrift links)")
        d_heute = st.date_input("Heutiges Datum", value=datetime.now()).strftime("%d.%m.%Y")
        
        if hr_wahl == "Kündigung (Angestellt)":
            d_ende = st.date_input("Kündigungsdatum zum", value=datetime.now()).strftime("%d.%m.%Y")
            text = f"Sehr geehrte/r Frau/Herr {empfaenger},\n\nhiermit kündigen wir das bestehende Arbeitsverhältnis ordentlich zum {d_ende}.\n\nHilfsweise kündigen wir zum nächstmöglichen Termin.\n\nFür Ihren weiteren Weg alles Gute."
            titel = "KÜNDIGUNG DES ARBEITSVERHÄLTNISSES"
        
        elif hr_wahl == "Kündigung (Azubi)":
            beruf = st.text_input("Ausbildungsberuf", value="Notfallsanitäter")
            d_ende = st.date_input("Enddatum", value=datetime.now()).strftime("%d.%m.%Y")
            text = f"Sehr geehrte/r Frau/Herr {empfaenger},\n\nhiermit kündigen wir das Ausbildungsverhältnis zum/zur {beruf} zum {d_ende}.\n\nIn der Probezeit erfolgt dies gemäß § 22 Abs. 1 BBiG ohne Angabe von Gründen."
            titel = "KÜNDIGUNG DES AUSBILDUNGSVERHÄLTNISSES"

        elif hr_wahl == "Abmahnung":
            grund = st.text_area("Sachverhalt (Was ist passiert?)")
            v_datum = st.date_input("Vorfall am").strftime("%d.%m.%Y")
            v_zeit = st.text_input("Uhrzeit", value="08:00")
            text = f"Sehr geehrte/r Frau/Herr {empfaenger},\n\nhiermit mahnen wir Sie wegen folgendem Fehlverhalten ab:\n\nSACHVERHALT: {grund}\nDATUM/ZEIT: {v_datum} um {v_zeit} Uhr.\n\nWir weisen darauf hin, dass im Wiederholungsfall die Kündigung droht."
            titel = "ABMAHNUNG"

        # Der Submit-Button erstellt NUR die Daten
        submitted = st.form_submit_button("Dokument vorschaufertig machen")
        if submitted:
            if empfaenger and bearbeiter:
                pdf_hr = Falkenfurt_HR_Master()
                pdf_data = pdf_hr.generate_doc(titel, text, {'datum_heute': d_heute, 'bearbeiter_name': bearbeiter})
                pdf_filename = f"{hr_wahl.replace(' ', '_')}_{empfaenger.replace(' ', '_')}.pdf"

    # DER DOWNLOAD-BUTTON MUSS HIER STEHEN (Außerhalb des 'with st.form')
    if pdf_data:
        st.success(f"✅ {hr_wahl} bereit!")
        st.download_button(
            label="⬇️ PDF jetzt herunterladen",
            data=bytes(pdf_data),
            file_name=pdf_filename,
            mime="application/pdf"
        )
