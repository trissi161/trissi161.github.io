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

# --- DATEN ---
aussteller_liste = {
    "Dr. med. Leon Müller (Geschäftsführer)": {"name": "Dr. med. Leon Müller", "amt": "Geschäftsführer", "sig_url": "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Unterschriftleon.png"},
    "Dr. med. Leon Müller (ÄLRD)": {"name": "Dr. med. Leon Müller", "amt": "Ärztlicher Leiter Rettungsdienst", "sig_url": "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Unterschriftleon.png"},
    "Thomas Schäfer (Leiter RD)": {"name": "Thomas Schäfer", "amt": "Leiter Rettungsdienst", "sig_url": "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Thomas.png"}
}
urkundentypen = {
    "Rettungssanitäter": {
        "titel": "RETTUNGSSANITÄTER",
        "text_oben": "hat am heutigen Tage die Prüfung zur Anerkennung als Rettungssanitäter in Bezug auf die besondere fachliche Eignung für den Einsatz im Rettungsdienst der Stadt Falkenfurt erfolgreich abgelegt. Auf Grundlage von § 12 Abs. 5 des einschlägigen Rettungsdienstgesetzes wird hiermit die Erlaubnis erteilt die Berufsbezeichnung",
        "text_unten": "zu führen. Diese Urkunde berechtigt zur Wahrnehmung der rettungsdienstlichen Aufgaben im Rahmen der Notfallrettung und Krankentransports sowie zur Durchführung der medizinischen Erstversorgung."
    },
    "Notfallsanitäter": {
        "titel": "NOTFALLSANITÄTER",
        "text_oben": "hat am heutigen Tage die Prüfung zur Anerkennung als Notfallsanitäter in Bezug auf die besondere fachliche Eignung für den Einsatz im Rettungsdienst der Stadt Falkenfurt erfolgreich abgelegt. Auf Grundlage von § 12 Abs. 5 des einschlägigen Rettungsdienstgesetzes wird hiermit die Erlaubnis erteilt die Berufsbezeichnung",
        "text_unten": "zu führen. Diese Urkunde berechtigt zur Wahrnehmung der rettungsdienstlichen Aufgaben im Rahmen der Notfallrettung sowie zur Durchführung und Leitung der medizinischen Erstversorgung."
    },
    "Ernennung": {
        "titel": "POSITION",
        "text_oben": "wird am heutigen Tage in Bezug auf die besondere fachliche und persönliche Eignung für den Rettungsdienst der Stadt Falkenfurt ernannt. Auf Grundlage der internen Organisationsrichtlinien wird hiermit die Erlaubnis erteilt, die Position",
        "text_unten": "wahrzunehmen. Diese Urkunde berechtigt zur Führung des zugeordneten Fachbereiches, zur Ausübung der damit verbundenen Weisungsbefugnisse sowie zur eigenverantwortlichen Leitung der zugewiesenen Dienstgeschäfte innerhalb des Stadtgebietes von Falkenfurt und des zugehörigen Rettungsdienstbereiches."
    }
}
ernennungs_rollen = ["Wachleiter", "Leiter Rettungsdienstschule", "Leiter Rettungsdienst", "Personalabteilungsleitung"]

# --- APP ---
st.set_page_config(page_title="RDF Verwaltung", page_icon="🚑", layout="centered")
t1, t2 = st.tabs(["🎓 Urkunden-Zentrum", "📋 Personalwesen (HR)"])

# --- TAB 1: URKUNDEN ---
with t1:
    st.header("Urkunden-Generator")
    with st.sidebar:
        st.subheader("Urkunden-Settings")
        wahl_typ = st.selectbox("Typ", list(urkundentypen.keys()))
        extra_pos = st.selectbox("Position", ernennungs_rollen) if wahl_typ == "Ernennung" else None
        wahl_boss = st.selectbox("Aussteller", list(aussteller_liste.keys()))
    
    u_pdf_data = None
    with st.form("u_form"):
        c1, c2 = st.columns(2)
        u_name = c1.text_input("Name des Absolventen")
        u_geb = c2.text_input("Geburtsdatum (TT.MM.JJJJ)")
        u_datum = st.date_input("Prüfungsdatum", value=datetime.now()).strftime("%d.%m.%Y")
        u_submit = st.form_submit_button("Urkunde generieren")
        if u_submit:
            if u_name and u_geb:
                pdf = RDF_Urkunden_Master()
                u_pdf_data = pdf.generate_pdf(u_name, u_geb, u_datum, aussteller_liste[wahl_boss], urkundentypen[wahl_typ], extra_pos)

    if u_pdf_data:
        st.success("✅ Urkunde bereit!")
        st.download_button("⬇️ Urkunde herunterladen", data=bytes(u_pdf_data), file_name=f"Urkunde_{u_name.replace(' ','_')}.pdf")

# --- TAB 2: HR ---
with t2:
    st.header("HR Dokumenten-Management")
    hr_wahl = st.selectbox("Dokument wählen", ["Kündigung (Angestellt)", "Kündigung (Azubi)", "Abmahnung"])
    
    hr_pdf_data = None
    with st.form("hr_form_universal"):
        empfaenger = st.text_input("Name des Empfängers")
        bearbeiter = st.text_input("Unterschrift links (Dein Name)")
        d_heute = st.date_input("Heutiges Datum", value=datetime.now()).strftime("%d.%m.%Y")
        
        if hr_wahl == "Kündigung (Angestellt)":
            d_ende = st.date_input("Kündigung zum", value=datetime.now()).strftime("%d.%m.%Y")
            titel = "KÜNDIGUNG DES ARBEITSVERHÄLTNISSES"
            text = (f"Sehr geehrte/r Frau/Herr {empfaenger},\n\n"
                    f"hiermit kündigen wir das mit Ihnen bestehende Arbeitsverhältnis ordentlich unter Einhaltung der vertraglich vereinbarten Kündigungsfrist zum {d_ende}.\n\n"
                    f"Hilfsweise kündigen wir zum nächstmöglichen Termin.\n\n"
                    f"Wir weisen Sie ausdrücklich darauf hin, dass Sie gemäß § 38 Abs. 1 SGB III verpflichtet sind, sich spätestens drei Monate vor Beendigung des Arbeitsverhältnisses persönlich bei der Agentur für Arbeit arbeitssuchend zu melden. Die Einhaltung dieser Frist ist Voraussetzung für den Bezug von Arbeitslosengeld.\n\n"
                    f"Bitte geben Sie sämtliche in Ihrem Besitz befindliche Ausrüstungsgegenstände, Schlüssel sowie Dienstausweise bis spätestens zu Ihrem letzten Arbeitstag bei der Dienststellenleitung ab.\n\n"
                    f"Über Ihren noch offenen Resturlaub sowie die Abgeltung etwaiger Überstunden werden wir Sie gesondert informieren. Ein qualifiziertes Arbeitszeugnis wird Ihnen zeitnah ausgestellt.\n\n"
                    f"Für Ihren weiteren Weg wünschen wir Ihnen alles Gute.")
        
        elif hr_wahl == "Kündigung (Azubi)":
            beruf = st.text_input("Ausbildungsberuf", value="Notfallsanitäter")
            d_ende = st.date_input("Ende zum", value=datetime.now()).strftime("%d.%m.%Y")
            titel = "KÜNDIGUNG DES BERUFSAUSBILDUNGSVERHÄLTNISSES"
            text = (f"Sehr geehrte/r Frau/Herr {empfaenger},\n\n"
                    f"hiermit kündigen wir das mit Ihnen bestehende Ausbildungsverhältnis zum/zur {beruf} "
                    f"unter Einhaltung der maßgeblichen Fristen zum {d_ende}.\n\n"
                    f"Sofern Sie sich noch in der Probezeit befinden, erfolgt diese Kündigung gemäß § 22 Abs. 1 BBiG ohne Einhaltung einer Kündigungsfrist und ohne Angabe von Gründen.\n\n"
                    f"Wir weisen Sie darauf hin, dass Sie sich innerhalb von drei Tagen nach Erhalt dieses Schreibens bei der Agentur für Arbeit arbeitssuchend melden müssen, um Nachteile beim Bezug von Leistungen zu vermeiden.\n\n"
                    f"Bitte geben Sie sämtliche Lehrmaterialien, Dienstkleidung, Schlüssel sowie Ihren Dienstausweis bis zum letzten Arbeitstag bei der Ausbildungsleitung ab. Ein Ausbildungszeugnis wird Ihnen nach Beendigung ausgehändigt.\n\n"
                    f"Wir wünschen Ihnen für Ihren weiteren Werdegang viel Erfolg.")

        elif hr_wahl == "Abmahnung":
            grund = st.text_area("Sachverhalt (Fehlverhalten)")
            v_datum = st.date_input("Vorfall am").strftime("%d.%m.%Y")
            v_zeit = st.text_input("Uhrzeit", value="08:00")
            titel = "ABMAHNUNG"
            text = (f"Sehr geehrte/r Frau/Herr {empfaenger},\n\n"
                    f"hiermit mahnen wir Sie wegen des folgenden arbeitsvertraglichen Fehlverhaltens förmlich ab:\n\n"
                    f"SACHVERHALT: {grund}\n"
                    f"DATUM/ZEIT: {v_datum} um {v_zeit} Uhr\n\n"
                    f"Durch dieses Verhalten verletzen Sie Ihre arbeitsvertraglichen Pflichten in erheblichem Maße. Wir fordern Sie hiermit auf, Ihr Verhalten umgehend zu korrigieren und Ihren vertraglich vereinbarten Pflichten künftig ordnungsgemäß und pünktlich nachzukommen.\n\n"
                    f"Wir weisen Sie ausdrücklich darauf hin, dass wir im Falle einer Wiederholung oder bei weiteren Pflichtverletzungen das Arbeitsverhältnis kündigen werden. Eine Kopie dieser Abmahnung wird zu Ihrer Personalakte genommen.\n\n"
                    f"Wir hoffen auf eine künftig reibungslose Zusammenarbeit.")

        if st.form_submit_button("Dokument vorschaufertig machen"):
            if empfaenger and bearbeiter:
                pdf_hr = Falkenfurt_HR_Master()
                hr_pdf_data = pdf_hr.generate_doc(titel, text, {'datum_heute': d_heute, 'bearbeiter_name': bearbeiter})

    if hr_pdf_data:
        st.success(f"✅ {hr_wahl} bereit!")
        st.download_button("⬇️ Dokument herunterladen", data=bytes(hr_pdf_data), file_name=f"{hr_wahl.replace(' ','_')}.pdf")
