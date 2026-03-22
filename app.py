import streamlit as st
import requests
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from io import BytesIO
from datetime import datetime

# --- DIE MASTER-KLASSE ---
class RDF_Urkunden_Generator(FPDF):
    def draw_border(self):
        # Der typische Falkenfurt-Rahmen
        self.set_line_width(1.5)
        self.set_draw_color(0, 14, 43) 
        self.rect(10, 10, 277, 190) 
        self.set_line_width(0.5)
        self.set_draw_color(255, 215, 0) 
        self.rect(13, 13, 271, 184) 

    def generate_pdf(self, name, geburtsdatum, datum, aussteller, typ_daten):
        self.add_page(orientation='L')
        self.set_auto_page_break(auto=False)
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
        self.ln(2)

        # 4. DYNAMISCHER TEXT (Je nach Urkundentyp)
        self.set_font('Helvetica', '', 11.5)
        self.set_text_color(30, 30, 30)
        self.set_left_margin(35)
        self.set_right_margin(35)
        
        self.multi_cell(0, 5.5, typ_daten['text_oben'], align='C')
        
        self.ln(2)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(0, 14, 43)
        self.cell(0, 12, typ_daten['titel'], align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

        self.set_font('Helvetica', '', 11)
        self.multi_cell(0, 5.5, typ_daten['text_unten'], align='C')

        # --- UNTERSCHRIFTEN-BLOCK ---
        try:
            resp_sig = requests.get(aussteller['sig_url'], timeout=5)
            self.image(BytesIO(resp_sig.content), x=185, y=148, w=65)
        except: pass

        self.set_draw_color(0, 14, 43)
        self.line(185, 175, 270, 175) 
        
        self.set_xy(185, 176) 
        self.set_font('Helvetica', 'B', 10)
        info = f"{aussteller['name']}\n{aussteller['amt']}\nFalkenfurt, den {datum}"
        self.multi_cell(85, 4.5, info, align='C')
        
        return self.output(dest='S')

# --- DATEN-KONFIGURATION ---

aussteller_liste = {
    "Dr. med. Leon Müller (Geschäftsführer)": {
        "name": "Dr. med. Leon Müller", "amt": "Geschäftsführer",
        "sig_url": "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Unterschriftleon.png"
    },
    "Dr. med. Leon Müller (ÄLRD)": {
        "name": "Dr. med. Leon Müller", "amt": "Ärztlicher Leiter Rettungsdienst",
        "sig_url": "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Unterschriftleon.png"
    },
    "Thomas Schäfer (Leiter RD)": {
        "name": "Thomas Schäfer", "amt": "Leiter Rettungsdienst",
        "sig_url": "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Thomas.png"
    }
}

urkundentypen = {
    "Rettungssanitäter": {
        "titel": "RETTUNGSSANITÄTER",
        "text_oben": "hat am heutigen Tage die Prüfung zur Anerkennung als Rettungssanitäter in Bezug auf die besondere fachliche Eignung für den Einsatz im Rettungsdienst der Stadt Falkenfurt erfolgreich abgelegt. Auf Grundlage von § 12 Abs. 5 des einschlägigen Rettungsdienstgesetzes wird hiermit die Erlaubnis erteilt die Berufsbezeichnung",
        "text_unten": "zu führen. Diese Urkunde berechtigt zur Wahrnehmung der rettungsdienstlichen Aufgaben im Rahmen der Notfallrettung und Krankentransports sowie zur Durchführung der medizinischen Erstversorgung und Unterstützung am Einsatzort."
    },
    "Notfallsanitäter": {
        "titel": "NOTFALLSANITÄTER",
        "text_oben": "hat am heutigen Tage die Prüfung zur Anerkennung als Notfallsanitäter in Bezug auf die besondere fachliche Eignung für den Einsatz im Rettungsdienst der Stadt Falkenfurt erfolgreich abgelegt. Auf Grundlage von § 12 Abs. 5 des einschlägigen Rettungsdienstgesetzes wird hiermit die Erlaubnis erteilt die Berufsbezeichnung",
        "text_unten": "zu führen. Diese Urkunde berechtigt zur Wahrnehmung der rettungsdienstlichen Aufgaben im Rahmen der Notfallrettung sowie zur Durchführung und Leitung der medizinischen Erstversorgung am Einsatzort."
    },
    "Notarzt": {
        "titel": "NOTARZT",
        "text_oben": "hat am heutigen Tage die Prüfung zur Anerkennung der Notarztqualifikation in Bezug auf die besondere fachliche Eignung für den Einsatz im Rettungsdienst der Stadt Falkenfurt erfolgreich abgelegt. Auf Grundlage von § 12 Abs. 5 des RD-Gesetzes sowie der VchärQ wird hiermit die Erlaubnis erteilt, die Zusatzbezeichnung",
        "text_unten": "zu führen. Diese Urkunde berechtigt zur Wahrnehmung der ärztlichen Aufgaben im Rahmen der Notfallrettung und zur Leitung der medizinischen Maßnahmen am Einsatzort."
    },
    "Einsatzleiter RD": {
        "titel": "EINSATZLEITER RETTUNGSDIENST",
        "text_oben": "hat am heutigen Tage die Prüfung zur Anerkennung als Einsatzleiter Rettungsdienst in Bezug auf die besondere fachliche Eignung für den Einsatz im Rettungsdienst der Stadt Falkenfurt erfolgreich abgelegt. Auf Grundlage von § 12 Abs. 5 des einschlägigen Rettungsdienstgesetzes wird hiermit die Erlaubnis erteilt die Funktionsbezeichnung",
        "text_unten": "zu führen. Diese Urkunde berechtigt zur Wahrnehmung der operativen Koordinierung komplexer Einsatzlagen sowie zur Führung der eingesetzten Rettungsmittel am Einsatzort."
    }
}

# --- WEB-INTERFACE (Streamlit) ---
st.set_page_config(page_title="RDF Urkunden-Zentrum", page_icon="🚑")

st.title("🚑 RDF Urkunden-Zentrum")

with st.sidebar:
    st.header("Konfiguration")
    wahl_typ = st.selectbox("Urkundentyp", list(urkundentypen.keys()))
    wahl_boss = st.selectbox("Aussteller / Unterschrift", list(aussteller_liste.keys()))

with st.form("main_form"):
    c1, c2 = st.columns(2)
    with c1:
        u_name = st.text_input("Name des Absolventen")
    with c2:
        u_geb = st.text_input("Geburtsdatum (TT.MM.JJJJ)")
    
    u_datum = st.date_input("Prüfungsdatum", value=datetime.now()).strftime("%d.%m.%Y")
    
    submit = st.form_submit_button("PDF generieren")

if submit:
    if u_name and u_geb:
        pdf = RDF_Urkunden_Generator()
        bytes_out = pdf.generate_pdf(u_name, u_geb, u_datum, aussteller_liste[wahl_boss], urkundentypen[wahl_typ])
        
        st.success(f"{wahl_typ}-Urkunde für {u_name} erstellt!")
        st.download_button(
            label="⬇️ PDF Herunterladen",
            data=bytes(bytes_out),
            file_name=f"Urkunde_{wahl_typ}_{u_name.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Bitte Namen und Geburtsdatum angeben.")
