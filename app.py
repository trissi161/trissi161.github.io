import streamlit as st
import requests
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from io import BytesIO
from datetime import datetime

class ELRD_Urkunde_Safe(FPDF):
    def draw_border(self):
        self.set_line_width(1.5)
        self.set_draw_color(0, 14, 43) 
        self.rect(10, 10, 277, 190) 
        self.set_line_width(0.5)
        self.set_draw_color(255, 215, 0) 
        self.rect(13, 13, 271, 184) 

    def generate_pdf(self, name, geburtsdatum, datum, aussteller_info):
        self.add_page(orientation='L')
        self.draw_border()
        
        # 1. LOGO
        logo_url = "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/logo.png"
        try:
            response = requests.get(logo_url, timeout=5)
            self.image(BytesIO(response.content), x=126, y=12, w=45) 
        except: pass

        # 2. TITEL
        self.set_y(55)
        self.set_font('Helvetica', 'B', 38)
        self.set_text_color(0, 14, 43)
        self.cell(0, 15, 'URKUNDE', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # 3. NAME & GEB
        self.set_font('Helvetica', 'B', 26)
        self.cell(0, 12, name.upper(), align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', 'I', 13)
        self.cell(0, 8, f'geboren am {geburtsdatum}', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

        # 4. TEXT
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

        # --- DYNAMISCHER UNTERSCHRIFTEN-BLOCK ---
        try:
            response_sig = requests.get(aussteller_info['sig_url'], timeout=5)
            # Positionierung der Unterschrift (etwas angepasst für die Optik)
            self.image(BytesIO(response_sig.content), x=185, y=148, w=65)
        except:
            pass

        self.set_draw_color(0, 14, 43)
        self.line(185, 175, 270, 175) 
        
        self.set_xy(185, 176) 
        self.set_font('Helvetica', 'B', 10)
        # Hier werden Name und Funktion aus der Auswahl eingesetzt
        info_text = f"{aussteller_info['name']}\n{aussteller_info['amt']}\nFalkenfurt, den {datum}"
        self.multi_cell(85, 4.5, info_text, align='C')
        
        return self.output(dest='S')

# --- STREAMLIT CONFIG & DATEN ---
st.set_page_config(page_title="RD Falkenfurt Urkunden", page_icon="🚑")

# Definition der Aussteller
aussteller_daten = {
    "Dr. med. Leon Müller (Geschäftsführer)": {
        "name": "Dr. med. Leon Müller",
        "amt": "Geschäftsführer",
        "sig_url": "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Unterschriftleon.png"
    },
    "Dr. med. Leon Müller (ÄLRD)": {
        "name": "Dr. med. Leon Müller",
        "amt": "Ärztlicher Leiter Rettungsdienst",
        "sig_url": "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Unterschriftleon.png"
    },
    "Thomas Schäfer (Leiter RD)": {
        "name": "Thomas Schäfer",
        "amt": "Leiter Rettungsdienst",
        "sig_url": "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Thomas.png"
    }
}

st.header("🚑 ELRD Urkunden-Erstellung")

with st.sidebar:
    st.subheader("Einstellungen")
    auswahl = st.selectbox("Wer stellt die Urkunde aus?", list(aussteller_daten.keys()))
    selected_boss = aussteller_daten[auswahl]

with st.form("generator_form"):
    col1, col2 = st.columns(2)
    with col1:
        u_name = st.text_input("Vollständiger Name des Absolventen")
    with col2:
        u_geb = st.text_input("Geburtsdatum (TT.MM.JJJJ)")
    
    u_datum = st.date_input("Ausstellungsdatum", value=datetime.now()).strftime("%d.%m.%Y")
    
    submit = st.form_submit_button("Vorschau & PDF Erstellen")

if submit:
    if u_name and u_geb:
        pdf = ELRD_Urkunde_Safe()
        # Wir übergeben das Paket mit Name, Amt und Unterschrift-URL an die Funktion
        pdf_bytes = pdf.generate_pdf(u_name, u_geb, u_datum, selected_boss)
        
        st.success(f"Urkunde für {u_name} wurde generiert!")
        st.download_button(
            label="⬇️ PDF Herunterladen",
            data=bytes(pdf_bytes),
            file_name=f"Urkunde_ELRD_{u_name.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Bitte füllen Sie Name und Geburtsdatum aus.")
