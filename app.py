import streamlit as st
import requests
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from io import BytesIO
from datetime import datetime

# Die Urkunden-Klasse
class ELRD_Urkunde_Safe(FPDF):
    def draw_border(self):
        self.set_line_width(1.5)
        self.set_draw_color(0, 14, 43) 
        self.rect(10, 10, 277, 190) 
        self.set_line_width(0.5)
        self.set_draw_color(255, 215, 0) 
        self.rect(13, 13, 271, 184) 

    def generate_pdf(self, name, geburtsdatum, datum):
        self.add_page(orientation='L')
        self.draw_border()
        
        # Logo
        logo_url = "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/logo.png"
        try:
            response = requests.get(logo_url, timeout=5)
            self.image(BytesIO(response.content), x=126, y=12, w=45) 
        except: pass

        # Titel
        self.set_y(55)
        self.set_font('Helvetica', 'B', 38)
        self.set_text_color(0, 14, 43)
        self.cell(0, 15, 'URKUNDE', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Name & Geburtsdatum
        self.set_font('Helvetica', 'B', 26)
        self.cell(0, 12, name.upper(), align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', 'I', 13)
        self.cell(0, 8, f'geboren am {geburtsdatum}', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

        # Haupttext
        self.set_font('Helvetica', '', 11.5)
        self.set_text_color(30, 30, 30)
        self.set_left_margin(35)
        self.set_right_margin(35)
        
        inhalt = ("hat am heutigen Tage die Prüfung zur Anerkennung als Einsatzleiter Rettungsdienst in Bezug auf die "
                  "besondere fachliche Eignung für den Einsatz im Rettungsdienst der Stadt Falkenfurt erfolgreich abgelegt. "
                  "Auf Grundlage von § 12 Abs. 5 des einschlägigen Rettungsdienstgesetzes wird hiermit die Erlaubnis erteilt die Funktionsbezeichnung")
        self.multi_cell(0, 6, inhalt, align='C')
        
        self.ln(2)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(0, 14, 43)
        self.cell(0, 15, 'EINSATZLEITER RETTUNGSDIENST', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

        inhalt2 = ("zu führen. Diese Urkunde berechtigt zur Wahrnehmung der operativen Koordinierung komplexer Einsatzlagen "
                  "sowie zur Führung der eingesetzten Rettungsmittel am Einsatzort innerhalb des Stadtgebietes von Falkenfurt "
                  "und des zugehörigen Rettungsdienstbereiches.")
        self.set_font('Helvetica', '', 11)
        self.multi_cell(0, 6, inhalt2, align='C')

        # Unterschrift
        sig_url = "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Thomas.png"
        try:
            response_sig = requests.get(sig_url, timeout=5)
            self.image(BytesIO(response_sig.content), x=185, y=148, w=80)
        except: pass

        self.set_draw_color(0, 14, 43)
        self.line(185, 175, 270, 175) 
        self.set_xy(185, 176) 
        self.set_font('Helvetica', 'B', 10)
        info = f"Thomas Schäfer\nLeiter Rettungsdienst\nFalkenfurt, den {datum}"
        self.multi_cell(85, 4.5, info, align='C')
        
        return self.output(dest='S')

# --- Web-Interface ---
st.set_page_config(page_title="RD Falkenfurt Urkunden", page_icon="🚑")

st.header("🚑 ELRD Urkunden-Erstellung")
st.info("Bitte füllen Sie die Felder aus, um das Zertifikat zu generieren.")

with st.form("generator_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Vollständiger Name")
    with col2:
        geb = st.text_input("Geburtsdatum (z.B. 01.01.1990)")
    
    datum_urkunde = st.date_input("Ausstellungsdatum", value=datetime.now()).strftime("%d.%m.%Y")
    
    submit = st.form_submit_button("Vorschau & PDF Erstellen")

if submit:
    if name and geb:
        pdf = ELRD_Urkunde_Safe()
        pdf_output = pdf.generate_pdf(name, geb, datum_urkunde)
        
        st.success(f"Urkunde für {name} ist fertig!")
        st.download_button(
            label="⬇️ PDF Herunterladen",
            data=bytes(pdf_output),
            file_name=f"Urkunde_ELRD_{name.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Bitte Namen und Geburtsdatum eingeben!")
