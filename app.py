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
        self.cell(0, 8, f'geboren am {geburbsdatum if "geburbsdatum" in locals() else geburtsdatum}', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
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

    def footer_sigs(self, bearbeiter_name, funktion_rechts="Geschäftsführung"):
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
        self.set_font('Helvetica', '', 8); self.set_xy(115, y_linie + 7); self.cell(70, 5, funktion_rechts, align='C')

    def generate_doc(self, titel, text, d):
        self.add_page(); self.set_top_margin(60)
        self.ln(20); self.set_font('Helvetica', 'B', 16); self.set_text_color(0, 14, 43)
        self.cell(0, 10, titel, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', '', 10); self.cell(0, 10, f"Datum: {d['datum_heute']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10); self.set_font('Helvetica', '', 11); self.set_text_color(0, 0, 0)
        self.multi_cell(0, 7, text)
        self.footer_sigs(d['bearbeiter_name'])
        return self.output(dest='S')

# --- SPEZIALKLASSE ARBEITSVERTRAG ---
class Falkenfurt_Full_Contract(FPDF):
    def header(self):
        self.set_fill_color(0, 16, 45); self.rect(0, 0, 210, 45, 'F')
        logo_url = "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/logo.png"
        try:
            resp = requests.get(logo_url)
            self.image(BytesIO(resp.content), x=15, y=8, h=28)
        except: pass
        self.set_text_color(255, 255, 255); self.set_font('Helvetica', 'B', 20)
        self.set_xy(70, 12); self.cell(0, 10, "RETTUNGSDIENST")
        self.set_xy(70, 21); self.cell(0, 10, "FALKENFURT")
        self.set_text_color(255, 220, 0); self.set_font('Helvetica', 'B', 11)
        self.set_xy(70, 32); self.cell(0, 10, "PERSONALABTEILUNG: VOLLSTÄNDIGER ARBEITSVERTRAG")
        self.ln(25)

    def add_paragraph(self, title, text):
        self.set_text_color(0, 0, 0); self.set_font('Helvetica', 'B', 10)
        self.multi_cell(0, 5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', '', 9); self.set_x(20)
        self.multi_cell(175, 4, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def generate(self, d):
        self.add_page(); self.set_auto_page_break(True, margin=35)
        self.set_font('Helvetica', 'B', 16); self.cell(0, 10, "Arbeitsvertrag", align='C', ln=True); self.ln(2)
        self.set_font('Helvetica', 'B', 10); self.cell(0, 5, "Praeambel", align='C', ln=True); self.set_font('Helvetica', '', 9)
        self.multi_cell(0, 4, "Dieser Vertrag gilt nur fuer RP-Zwecke auf dem FiveM-RP-Server Falkenfurt Roleplay.\nEr findet sonst keine Anwendung.", align='C')
        self.ln(4); self.set_font('Helvetica', 'B', 10); self.cell(0, 5, "zwischen", align='C', ln=True)
        self.set_font('Helvetica', 'B', 13); self.cell(0, 7, "Dem Rettungsdienst Falkenfurt", align='C', ln=True)
        self.set_font('Helvetica', '', 8); self.cell(0, 4, "- vertreten durch Dr. med. Leon Mueller -", align='C', ln=True); self.ln(2)
        self.set_font('Helvetica', 'B', 10); self.cell(0, 5, "und", align='C', ln=True)
        self.set_font('Helvetica', 'B', 12); self.cell(0, 7, d['name'], align='C', ln=True)
        self.set_font('Helvetica', '', 8); self.cell(0, 4, "(nachfolgend 'Arbeitnehmer' genannt)", align='C', ln=True); self.ln(4)
        
        paragraphs = [
            ("§ 1) Gegenstand des Arbeitsvertrages", "Gegenstand des Arbeitsvertrages ist ein unbefristetes Anstellungsverhaeltnis zwischen den beiden oben genannten Parteien."),
            ("§ 2) Beginn des Arbeitsverhaeltnisses", f"Das Arbeitsverhaeltnis beginnt am {d['datum']} und wird auf unbestimmte Zeit geschlossen."),
            ("§ 3) Anwendbarkeit tariflicher Regelungen", "(1) Fuer das Arbeitsverhaeltnis gelten die Regelungen des staatlichen Tarifvertrages in seiner jeweils gueltigen Fassung (nachfolgend 'Tarifvertrag').\n(2) Falls Regelungen dieses Vertrages dem Tarifvertrag widersprechen, gilt vorrangig der Tarifvertrag."),
            ("§ 4) Betriebsvereinbarungen", "(1) Auf das Arbeitsverhaeltnis finden keine Betriebsvereinbarungen Anwendung.\n(2) Falls im Betrieb des Arbeitgebers zukuenftig betriebliche Regelungen gelten, gehen diese vor, soweit sie fuer den Arbeitnehmer guenstiger sind."),
            ("§ 5) Probezeit", "(1) Die ersten 14 Tage des Arbeitsverhaeltnisses gelten als Probezeit.\n(2) Waehrend der Probezeit kann das Arbeitsverhaeltnis von jeder Vertragspartei ohne Angabe von Gruenden gekuendigt werden."),
            ("§ 6) Taetigkeit", f"(1) Der Arbeitnehmer wird als {d['funktion']} eingestellt.\n(2) Der Arbeitsort ist die Rettungswache in Falkenfurt.\n(3) Im Rahmen der Ausuebung seines Berufes ist es dem Arbeitnehmer erlaubt, auch ausserhalb der genannten Ortschaft seiner Taetigkeit nachzugehen.\n(4) Der Arbeitnehmer verpflichtet sich, seine volle Arbeitskraft in den Dienst des Arbeitgebers zu stellen."),
            ("§ 7) Wechsel der Taetigkeit und des Arbeitsortes", "Soweit betrieblich erforderlich, ist der Arbeitgeber unter angemessener Beruecksichtigung der Belange des Arbeitnehmers berechtigt, diesem voruebergehend oder auf Dauer eine andere oder zusaetzliche zumutbare Taetigkeit zuzuweisen."),
            ("§ 8) Arbeitszeit, Ruhepausen, Überstunden, Kurzarbeit, Abwesenheit", "(1) Die woechentliche Mindestdienstzeit wird betrieblich nicht vorgeschrieben.\n(2) Der Anspruch auf Ruhepausen richtet sich nach dem Gesetz. Pausen gelten als Dienstzeit.\n(6) Der Arbeitnehmer verpflichtet sich, einen Ausfall, der laenger als drei Tage andauert, anzuzeigen. Die maximale Dauer der Abwesenheit betraegt vier Wochen."),
            ("§ 9) Verguetung", "(1) Der Arbeitnehmer erhaelt ein Nettoarbeitsentgelt entsprechend dem TVOeD Falkenfurt.\n(2) Das Arbeitsentgelt ist alle 45 Minuten faellig und wird vom Arbeitgeber auf das Konto des Arbeitnehmers ueberwiesen."),
            ("§ 10) Sonderzuwendungen", "Die Parteien treffen keine Sonderzuwendungen Vereinbarungen."),
            ("§ 11) Fortbildungen", "(1) Jeder Arbeitnehmer hat das Recht, Fortbildungen zu erhalten.\n(2) Fuer die Dauer der Fortbildung wird der Arbeitnehmer unter Fortzahlung des Lohns freigestellt."),
            ("§ 12) Dienstwagen", "Der Arbeitgeber stellt dem Arbeitnehmer fuer die Dauer des Arbeitsverhaeltnisses den Dienstwagen zur Verfuegung. Es gilt die Dienstvorschrift."),
            ("§ 13) Verguetungsfortzahlung bei persoenlicher Verhinderung", "Lohnfortzahlung erfolgt nur bei Eheschliessung des Arbeitnehmers, Entbindung der Ehefrau/Partnerin, Arbeitsunfall oder akutem Arztbesuch."),
            ("§ 14) Angaben zur Person", "Der Arbeitnehmer erklaert, arbeitsfaehig zu sein und an keiner ansteckenden Krankheit zu leiden. Er bestätigt, dass keine Vorstrafen im Zusammenhang mit seiner beruflichen Taetigkeit vorliegen."),
            ("§ 15) Verhalten am Arbeitsplatz", "(1) Der Arbeitnehmer hat den Weisungen des Arbeitgebers nachzukommen.\n(2) Der Arbeitnehmer hat sich nach der betriebsinternen Kleiderordnung zu richten."),
            ("§ 16) Verschwiegenheitspflicht", "(1) Der Arbeitnehmer verpflichtet sich, ueber alle Betriebs- und Geschaeftsgeheimnisse Stillschweigen zu bewahren.\n(2) Fuer jeden Fall der Zuwiderhandlung kann eine Vertragsstrafe in Hoehe einer Bruttomonatsverguetung faellig werden."),
            ("§ 17) Wettbewerbsverbot", "Dem Arbeitnehmer ist es untersagt, waehrend des Verhaeltnisses selbststaendig oder fuer fremde Rechnung in Konkurrenz zum Arbeitgeber zu betaetigen."),
            ("§ 18) Datenschutz und Datensicherheit", "(1) Patientendaten duerfen nur mit schriftlicher Zustimmung weitergegeben werden. (4) Die Veroeffentlichung interner Dokumente ist verboten und hat die fristlose Kuendigung zur Folge."),
            ("§ 19) Nebentaetigkeit", "Entgeltliche Nebenbeschaeftigungen sind dem Arbeitgeber anzuzeigen und beduerfen einer Genehmigung."),
            ("§ 20) Anzeige- und Nachweispflichten bei Krankheiten", "Der Arbeitnehmer ist verpflichtet, dem Arbeitgeber jede Arbeitsunfaehigkeit und deren voraussichtliche Dauer unverzueglich anzuzeigen."),
            ("§ 21) Kuendigung", "(2) Nach Ablauf der Probezeit kann das Arbeitsverhaeltnis ordentlich gekuendigt werden. Alle Kuendigungen beduerfen der Schriftform."),
            ("§ 22) Kuendigungsschutzklage", "Eine Klage muss innerhalb von zwei Wochen nach Zugang der schriftlichen Kuendigung bei der Justiz Falkenfurt erhoben werden."),
            ("§ 23) Änderungen und Ergaenzungen", "Aenderungen dieses Arbeitsvertrages beduerfen zu ihrer Wirksamkeit der Schriftform und Unterzeichnung beider Parteien."),
            ("§ 24) Salvatorische Klausel", "Sollte eine Bestimmung dieses Vertrages unwirksam sein, so beruehrt dies nicht die Wirksamkeit der uebrigen Bestimmungen."),
            ("§ 25) Dienstkleidung", "Im Dienst ist die vom Arbeitgeber vorgegebene Dienstkleidung zu tragen."),
            ("§ 26) Verhalten in Sozialen Medien", "(1) Es duerfen keine Fotos von Einsaetzen oder Patienten hochgeladen werden.\n(2) Es duerfen keine menschenverachtenden Bilder veroeffentlicht werden."),
            ("§ 27) Einhaltung von Sicherheitsvorschriften", "Der Arbeitnehmer verpflichtet sich, saemtliche Gesundheits- und Sicherheitsvorschriften, insbesondere das Tragen der PSA, strikt einzuhalten."),
            ("§ 28) Rueckzahlungsklausel fuer Ausbildungskosten", "Bei Kuendigung durch den Arbeitnehmer binnen 8 Wochen nach Abschluss der Ausbildung sind 75% der Kosten zurueckzuzahlen."),
            ("§ 29) Schlussbestimmungen", "Bei Beendigung sind saemtliche im Besitz befindlichen Geschaeftsunterlagen, Schluessel und Dienstfahrzeuge zurueckzugeben. Es gilt deutsches Sachrecht.")
        ]
        for title, text in paragraphs:
            self.add_paragraph(title, text)

        self.ln(20); y_linie = self.get_y() + 20
        if y_linie > 260: self.add_page(); y_linie = 60
        try:
            sig_url = "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Unterschriftleon.png"
            self.image(BytesIO(requests.get(sig_url).content), x=25, y=y_linie - 35, h=55)
        except: pass
        self.line(15, y_linie, 85, y_linie); self.set_font('Helvetica', 'B', 10); self.set_xy(15, y_linie + 2); self.cell(70, 7, "Dr. med. Leon Müller", align='C', ln=True)
        self.set_font('Helvetica', '', 8); self.set_x(15); self.cell(70, 4, "Geschäftsführung Rettungsdienst", align='C')
        self.set_font('Courier', 'I', 14); self.set_text_color(0, 32, 96); self.set_xy(125, y_linie - 12); self.cell(70, 10, d['name'], align='C')
        self.line(125, y_linie, 195, y_linie); self.set_text_color(0, 0, 0); self.set_font('Helvetica', 'B', 10); self.set_xy(125, y_linie + 2); self.cell(70, 7, d['name'], align='C', ln=True)
        self.set_font('Helvetica', '', 8); self.set_x(125); self.cell(70, 4, d['funktion'], align='C')
        return self.output(dest='S')

# --- DATEN & APP ---
aussteller_liste = {
    "Dr. med. Leon Müller (Geschäftsführer)": {"name": "Dr. med. Leon Müller", "amt": "Geschäftsführer", "sig_url": "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Unterschriftleon.png"},
    "Thomas Schäfer (Leiter RD)": {"name": "Thomas Schäfer", "amt": "Leiter Rettungsdienst", "sig_url": "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Thomas.png"}
}
urkundentypen = {
    "Rettungssanitäter": {"titel": "RETTUNGSSANITÄTER", "text_oben": "hat am heutigen Tage die Prüfung zur Anerkennung als RS erfolgreich abgelegt...", "text_unten": "Diese Urkunde berechtigt zur Wahrnehmung der Aufgaben..."},
    "Notfallsanitäter": {"titel": "NOTFALLSANITÄTER", "text_oben": "hat am heutigen Tage die Prüfung zur Anerkennung als NFS erfolgreich abgelegt...", "text_unten": "Diese Urkunde berechtigt zur Leitung medizinischer Erstversorgung..."},
    "Ernennung": {"titel": "POSITION", "text_oben": "wird am heutigen Tage ernannt...", "text_unten": "Diese Urkunde berechtigt zur Führung des Fachbereiches..."}
}

st.set_page_config(page_title="RDF Verwaltung", page_icon="🚑", layout="centered")
t1, t2 = st.tabs(["🎓 Urkunden", "📋 Personalwesen (HR)"])

with t1:
    st.header("Urkunden-Zentrum")
    u_pdf_data = None
    with st.form("u_form"):
        wahl_typ = st.selectbox("Typ", list(urkundentypen.keys()))
        u_name = st.text_input("Name")
        u_geb = st.text_input("Geburtsdatum")
        u_datum = st.date_input("Datum").strftime("%d.%m.%Y")
        if st.form_submit_button("Generieren"):
            pdf = RDF_Urkunden_Master()
            u_pdf_data = pdf.generate_pdf(u_name, u_geb, u_datum, aussteller_liste["Dr. med. Leon Müller (Geschäftsführer)"], urkundentypen[wahl_typ])
    if u_pdf_data: st.download_button("⬇️ Download Urkunde", data=bytes(u_pdf_data), file_name="Urkunde.pdf")

with t2:
    st.header("HR Dokumenten-Management")
    hr_wahl = st.selectbox("Dokument wählen", ["Arbeitsvertrag (Vollständig)", "Suspendierung", "Abmahnung", "Kündigung (Angestellt)", "Kündigung (Azubi)"])
    hr_pdf_data = None
    with st.form("hr_form"):
        empfaenger = st.text_input("Name des Mitarbeiters")
        bearbeiter = st.text_input("Dein Name (Unterschrift links)")
        d_heute = st.date_input("Heutiges Datum").strftime("%d.%m.%Y")
        
        if hr_wahl == "Arbeitsvertrag (Vollständig)":
            funktion = st.text_input("Funktion/Stelle", value="Notfallsanitäter")
            if st.form_submit_button("Vertrag erstellen"):
                pdf_v = Falkenfurt_Full_Contract()
                hr_pdf_data = pdf_v.generate({'name': empfaenger, 'funktion': funktion, 'datum': d_heute})
        
        elif hr_wahl == "Suspendierung":
            grund = st.text_area("Grund der Suspendierung")
            bis_wann = st.text_input("Suspendiert bis wann?", value="auf Weiteres")
            if st.form_submit_button("Suspendierung erstellen"):
                pdf_s = Falkenfurt_HR_Master()
                text = (f"Sehr geehrte/r Frau/Herr {empfaenger},\n\nhiermit suspendieren wir Sie mit sofortiger Wirkung vom aktiven Dienstbetrieb.\n\nDiese Maßnahme erfolgt vorläufig bis zum {bis_wann} aufgrund folgender Vorkommnisse:\n{grund}\n\nDie Freistellung erfolgt unter Fortzahlung Ihrer Bezüge. Während der Dauer ist Ihnen das Betreten der Liegenschaften untersagt. Bitte geben Sie Ihren Dienstausweis unverzüglich ab.")
                hr_pdf_data = pdf_s.generate_doc("SUSPENDIERUNG VOM DIENSTBETRIEB", text, {'datum_heute': d_heute, 'bearbeiter_name': bearbeiter})
        
        elif hr_wahl == "Abmahnung":
            grund = st.text_area("Sachverhalt")
            if st.form_submit_button("Abmahnung erstellen"):
                pdf_a = Falkenfurt_HR_Master()
                text = (f"Sehr geehrte/r Frau/Herr {empfaenger},\n\nhiermit mahnen wir Sie wegen des folgenden Fehlverhaltens förmlich ab:\n\nSACHVERHALT: {grund}\n\nWir fordern Sie auf, Ihr Verhalten umgehend zu korrigieren. Im Wiederholungsfall droht die Kündigung.")
                hr_pdf_data = pdf_a.generate_doc("ABMAHNUNG", text, {'datum_heute': d_heute, 'bearbeiter_name': bearbeiter})

        elif "Kündigung" in hr_wahl:
            d_ende = st.date_input("Termin zum").strftime("%d.%m.%Y")
            if st.form_submit_button("Kündigung erstellen"):
                pdf_k = Falkenfurt_HR_Master()
                text = f"Sehr geehrte/r Frau/Herr {empfaenger},\n\nhiermit kündigen wir das Verhältnis ordentlich zum {d_ende}."
                hr_pdf_data = pdf_k.generate_doc("KÜNDIGUNG", text, {'datum_heute': d_heute, 'bearbeiter_name': bearbeiter})

    if hr_pdf_data: st.download_button("⬇️ Download Dokument", data=bytes(hr_pdf_data), file_name=f"{hr_wahl}.pdf")
