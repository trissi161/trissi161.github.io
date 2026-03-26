import streamlit as st
import requests
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from io import BytesIO
from datetime import datetime

# ==========================================
# 1. PDF-KLASSEN (LOGIK & DESIGN)
# ==========================================

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
        
        # 1. LOGO POSITION
        logo_url = "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Bild_2026-03-24_235639621.png"
        try:
            resp = requests.get(logo_url, timeout=5)
            self.image(BytesIO(resp.content), x=130, y=15, w=38) 
        except: pass
        
        # 2. TITEL & NAME
        self.set_y(65)
        self.set_font('Helvetica', 'B', 38)
        self.set_text_color(0, 14, 43)
        self.cell(0, 15, 'URKUNDE', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.set_font('Helvetica', 'B', 28)
        self.cell(0, 15, name.upper(), align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.set_font('Helvetica', 'I', 13)
        self.cell(0, 8, f'geboren am {geburtsdatum}', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.ln(10)
        
        # 3. FLIESSTEXT OBEN
        self.set_font('Helvetica', '', 10.5)
        self.set_text_color(30, 30, 30)
        self.set_left_margin(35)
        self.set_right_margin(35)
        self.multi_cell(0, 5, typ_daten['text_oben'], align='C')
        
        self.ln(4)
        
        # 4. DIE POSITION (z.B. NOTARZT)
        self.set_font('Helvetica', 'B', 22)
        self.set_text_color(0, 14, 43)
        anzeige_titel = extra_pos if extra_pos else typ_daten['titel']
        self.cell(0, 12, anzeige_titel.upper(), align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.ln(4)
        
        # 5. FLIESSTEXT UNTEN
        self.set_font('Helvetica', '', 10.5)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5, typ_daten['text_unten'], align='C')
        
# 6. UNTERSCHRIFTENFELD
        try:
            resp_sig = requests.get(aussteller['sig_url'], timeout=5)
            # x=200 (weiter rechts), y=148 (weiter unten), w=65 (größer skaliert)
            self.image(BytesIO(resp_sig.content), x=200, y=148, w=65)
        except: pass
        
        self.set_draw_color(0, 14, 43)
        # Linie passend zur neuen Position (von x=195 bis 275)
        self.line(195, 178, 275, 178) 
        
        # Text unter der Linie
        self.set_xy(195, 179) 
        self.set_font('Helvetica', 'B', 10)
        info = f"{aussteller['name']}\n{aussteller['amt']}\nFalkenfurt, den {datum}"
        self.multi_cell(80, 4.5, info, align='C')
        
        return self.output(dest='S')

class Falkenfurt_HR_Master(FPDF):
    """Klasse für Standard HR-Dokumente (Kündigung, Abmahnung)."""
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


class Falkenfurt_Suspendierung(FPDF):
    """Spezialklasse für Suspendierungen."""
    def header(self):
        self.set_fill_color(0, 14, 43); self.rect(0, 0, 210, 45, 'F')
        logo_url = "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/logo.png"
        try:
            resp = requests.get(logo_url); self.image(BytesIO(resp.content), x=15, y=5, h=35)
        except: pass
        self.set_text_color(255, 255, 255); self.set_font('Helvetica', 'B', 20)
        self.set_xy(70, 12); self.cell(0, 10, "RETTUNGSDIENST"); self.set_xy(70, 22); self.cell(0, 10, "FALKENFURT")
        self.set_text_color(255, 215, 0); self.set_font('Helvetica', 'B', 12); self.set_xy(70, 35); self.cell(0, 5, "PERSONALABTEILUNG / DIENSTLEITUNG")

    def generate(self, d):
        self.add_page(); self.set_top_margin(60)
        self.ln(20); self.set_font('Helvetica', 'B', 16); self.set_text_color(0, 14, 43)
        self.cell(0, 10, "SUSPENDIERUNG VOM DIENSTBETRIEB", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', '', 10); self.cell(0, 10, f"Datum: {d['datum_heute']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10); self.set_font('Helvetica', '', 11); self.set_text_color(0, 0, 0)
        text = (
            f"Sehr geehrte/r Frau/Herr {d['name_empfaenger']},\n\n"
            f"hiermit suspendieren wir Sie mit sofortiger Wirkung vom aktiven Dienstbetrieb im Rettungsdienst Falkenfurt.\n\n"
            f"Diese Maßnahme erfolgt vorläufig bis zum {d['ende_suspendierung']} aufgrund folgender Vorkommnisse:\n"
            f"{d['grund']}\n\n"
            f"Die Freistellung erfolgt unter Fortzahlung Ihrer Bezüge. Während der Dauer der Suspendierung ist Ihnen das Betreten sämtlicher Liegenschaften (Wachen, Verwaltung, Fahrzeughallen) sowie die Nutzung von Dienstfahrzeugen und Dienstkleidung untersagt.\n\n"
            f"Bitte geben Sie Ihren Dienstausweis sowie sämtliche Dienstschlüssel unverzüglich bei der Personalabteilung ab.\n\n"
            f"Wir werden Sie über das weitere Vorgehen zeitnah informieren."
        )
        self.multi_cell(0, 7, text)
        
        y_linie = 245
        self.set_font('Courier', 'I', 14); self.set_text_color(0, 32, 96); self.set_xy(15, y_linie - 12); self.cell(70, 10, d['bearbeiter_name'], align='C')
        self.set_draw_color(0, 0, 0); self.line(15, y_linie, 85, y_linie)
        self.set_text_color(0, 0, 0); self.set_font('Helvetica', 'B', 10); self.set_xy(15, y_linie + 2); self.cell(70, 7, d['bearbeiter_name'], align='C')
        self.set_font('Helvetica', '', 8); self.set_xy(15, y_linie + 7); self.cell(70, 5, "Personalabteilung", align='C')
        try:
            sig_url = "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Unterschriftleon.png"
            resp = requests.get(sig_url); self.image(BytesIO(resp.content), x=125, y=y_linie - 28, h=50) 
        except: pass
        self.line(115, y_linie, 185, y_linie); self.set_font('Helvetica', 'B', 10); self.set_xy(115, y_linie + 2); self.cell(70, 7, "Dr. med. Leon Müller", align='C')
        self.set_font('Helvetica', '', 8); self.set_xy(115, y_linie + 7); self.cell(70, 5, "Geschäftsführung", align='C')
        return self.output(dest='S')


class Falkenfurt_Full_Contract(FPDF):
    """Spezialklasse für den 29-Paragraphen Arbeitsvertrag."""
    def header(self):
        self.set_fill_color(0, 16, 45); self.rect(0, 0, 210, 45, 'F')
        logo_url = "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/logo.png"
        try:
            resp = requests.get(logo_url); self.image(BytesIO(resp.content), x=15, y=8, h=28)
        except: pass
        self.set_text_color(255, 255, 255); self.set_font('Helvetica', 'B', 20)
        self.set_xy(70, 12); self.cell(0, 10, "RETTUNGSDIENST"); self.set_xy(70, 21); self.cell(0, 10, "FALKENFURT")
        self.set_text_color(255, 220, 0); self.set_font('Helvetica', 'B', 11); self.set_xy(70, 32); self.cell(0, 10, "PERSONALABTEILUNG: VOLLSTÄNDIGER ARBEITSVERTRAG")
        self.ln(25)

    def add_paragraph(self, title, text):
        self.set_text_color(0, 0, 0); self.set_font('Helvetica', 'B', 10)
        self.multi_cell(0, 5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', '', 9); self.set_x(20)
        self.multi_cell(175, 4, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT); self.ln(2)

    def generate(self, d):
        self.add_page(); self.set_auto_page_break(True, margin=35)
        self.set_font('Helvetica', 'B', 16); self.cell(0, 10, "Arbeitsvertrag", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT); self.ln(2)
        self.set_font('Helvetica', 'B', 10); self.cell(0, 5, "Praeambel", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', '', 9); self.multi_cell(0, 4, "Dieser Vertrag gilt nur fuer RP-Zwecke auf dem FiveM-RP-Server Falkenfurt Roleplay.\nEr findet sonst keine Anwendung.", align='C'); self.ln(4)
        
        self.set_font('Helvetica', 'B', 10); self.cell(0, 5, "zwischen", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', 'B', 13); self.cell(0, 7, "Dem Rettungsdienst Falkenfurt", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', '', 8); self.cell(0, 4, "- vertreten durch Dr. med. Leon Mueller (nachfolgend 'Arbeitgeber' genannt) -", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT); self.ln(2)
        self.set_font('Helvetica', 'B', 10); self.cell(0, 5, "und", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', 'B', 12); self.cell(0, 7, d['name'], align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', '', 8); self.cell(0, 4, "(nachfolgend 'Arbeitnehmer' genannt)", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT); self.ln(4)
        self.set_font('Helvetica', 'B', 10); self.cell(0, 5, "wird folgender Arbeitsvertrag geschlossen:", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT); self.ln(5)

        # ALLE 29 PARAGRAPHEN
        self.add_paragraph("§ 1) Gegenstand des Arbeitsvertrages", "Gegenstand des Arbeitsvertrages ist ein unbefristetes Anstellungsverhaeltnis zwischen den beiden oben genannten Parteien.")
        self.add_paragraph("§ 2) Beginn des Arbeitsverhaeltnisses", f"Das Arbeitsverhaeltnis beginnt am {d['datum']} und wird auf unbestimmte Zeit geschlossen.")
        self.add_paragraph("§ 3) Anwendbarkeit tariflicher Regelungen", "(1) Fuer das Arbeitsverhaeltnis gelten die Regelungen des staatlichen Tarifvertrages in seiner jeweils gueltigen Fassung (nachfolgend 'Tarifvertrag').\n(2) Falls Regelungen dieses Vertrages dem Tarifvertrag widersprechen, gilt vorrangig der Tarifvertrag.")
        self.add_paragraph("§ 4) Betriebsvereinbarungen", "(1) Auf das Arbeitsverhaeltnis finden keine Betriebsvereinbarungen Anwendung.\n(2) Falls im Betrieb des Arbeitgebers zukuenftig betriebliche Regelungen gelten, gehen diese vor, soweit sie fuer den Arbeitnehmer guenstiger sind.")
        self.add_paragraph("§ 5) Probezeit", "(1) Die ersten 14 Tage des Arbeitsverhaeltnisses gelten als Probezeit.\n(2) Waehrend der Probezeit kann das Arbeitsverhaeltnis von jeder Vertragspartei ohne Angabe von Gruenden gekuendigt werden.")
        self.add_paragraph("§ 6) Taetigkeit", f"(1) Der Arbeitnehmer wird als {d['funktion']} eingestellt.\n(2) Der Arbeitsort ist die Rettungswache in Falkenfurt.\n(3) Im Rahmen der Ausuebung seines Berufes ist es dem Arbeitnehmer erlaubt, auch ausserhalb der genannten Ortschaft seiner Taetigkeit nachzugehen.\n(4) Der Arbeitnehmer verpflichtet sich, seine volle Arbeitskraft in den Dienst des Arbeitgebers zu stellen.")
        self.add_paragraph("§ 7) Wechsel der Taetigkeit und des Arbeitsortes", "Soweit betrieblich erforderlich, ist der Arbeitgeber unter angemessener Beruecksichtigung der Belange des Arbeitnehmers berechtigt, diesem voruebergehend oder auf Dauer eine andere oder zusaetzliche zumutbare Taetigkeit zuzuweisen.")
        self.add_paragraph("§ 8) Arbeitszeit, Ruhepausen, Überstunden, Kurzarbeit, Abwesenheit", "(1) Die woechentliche Mindestdienstzeit wird betrieblich nicht vorgeschrieben.\n(2) Der Anspruch auf Ruhepausen richtet sich nach dem Gesetz. Pausen gelten als Dienstzeit.\n(6) Der Arbeitnehmer verpflichtet sich, einen Ausfall, der laenger als drei Tage andauert, anzuzeigen. Die maximale Dauer der Abwesenheit betraegt vier Wochen.")
        self.add_paragraph("§ 9) Verguetung", "(1) Der Arbeitnehmer erhaelt ein Nettoarbeitsentgelt entsprechend dem TVOeD Falkenfurt.\n(2) Das Arbeitsentgelt ist alle 45 Minuten faellig und wird vom Arbeitgeber auf das Konto des Arbeitnehmers ueberwiesen.")
        self.add_paragraph("§ 10) Sonderzuwendungen", "Die Parteien treffen keine Sonderzuwendungen Vereinbarungen.")
        self.add_paragraph("§ 11) Fortbildungen", "(1) Jeder Arbeitnehmer hat das Recht, Fortbildungen zu erhalten.\n(2) Fuer die Dauer der Fortbildung wird der Arbeitnehmer unter Fortzahlung des Lohns freigestellt.")
        self.add_paragraph("§ 12) Dienstwagen", "Der Arbeitgeber stellt dem Arbeitnehmer fuer die Dauer des Arbeitsverhaeltnisses den Dienstwagen zur Verfuegung. Es gilt die Dienstvorschrift.")
        self.add_paragraph("§ 13) Verguetungsfortzahlung bei persoenlicher Verhinderung", "Lohnfortzahlung erfolgt nur bei Eheschliessung des Arbeitnehmers, Entbindung der Ehefrau/Partnerin, Arbeitsunfall oder akutem Arztbesuch.")
        self.add_paragraph("§ 14) Angaben zur Person", "Der Arbeitnehmer erklaert, arbeitsfaehig zu sein und an keiner ansteckenden Krankheit zu leiden. Er bestätigt, dass keine Vorstrafen im Zusammenhang mit seiner beruflichen Taetigkeit vorliegen.")
        self.add_paragraph("§ 15) Verhalten am Arbeitsplatz", "(1) Der Arbeitnehmer hat den Weisungen des Arbeitgebers nachzukommen.\n(2) Der Arbeitnehmer hat sich nach der betriebsinternen Kleiderordnung zu richten.")
        self.add_paragraph("§ 16) Verschwiegenheitspflicht", "(1) Der Arbeitnehmer verpflichtet sich, ueber alle Betriebs- und Geschaeftsgeheimnisse Stillschweigen zu bewahren.\n(2) Fuer jeden Fall der Zuwiderhandlung kann eine Vertragsstrafe in Hoehe einer Bruttomonatsverguetung faellig werden.")
        self.add_paragraph("§ 17) Wettbewerbsverbot", "Dem Arbeitnehmer ist es untersagt, waehrend des Verhaeltnisses selbststaendig oder fuer fremde Rechnung in Konkurrenz zum Arbeitgeber zu betaetigen.")
        self.add_paragraph("§ 18) Datenschutz und Datensicherheit", "(1) Patientendaten duerfen nur mit schriftlicher Zustimmung weitergegeben werden. (4) Die Veroeffentlichung interner Dokumente ist verboten und hat die fristlose Kuendigung zur Folge.")
        self.add_paragraph("§ 19) Nebentaetigkeit", "Entgeltliche Nebenbeschaeftigungen sind dem Arbeitgeber anzuzeigen und beduerfen einer Genehmigung.")
        self.add_paragraph("§ 20) Anzeige- und Nachweispflichten bei Krankheiten", "Der Arbeitnehmer ist verpflichtet, dem Arbeitgeber jede Arbeitsunfaehigkeit und deren voraussichtliche Dauer unverzueglich anzuzeigen.")
        self.add_paragraph("§ 21) Kuendigung", "(2) Nach Ablauf der Probezeit kann das Arbeitsverhaeltnis ordentlich gekuendigt werden. Alle Kuendigungen beduerfen der Schriftform.")
        self.add_paragraph("§ 22) Kuendigungsschutzklage", "Eine Klage muss innerhalb von zwei Wochen nach Zugang der schriftlichen Kuendigung bei der Justiz Falkenfurt erhoben werden.")
        self.add_paragraph("§ 23) Änderungen und Ergaenzungen", "Aenderungen dieses Arbeitsvertrages beduerfen zu ihrer Wirksamkeit der Schriftform und Unterzeichnung beider Parteien.")
        self.add_paragraph("§ 24) Salvatorische Klausel", "Sollte eine Bestimmung dieses Vertrages unwirksam sein, so beruehrt dies nicht die Wirksamkeit der uebrigen Bestimmungen.")
        self.add_paragraph("§ 25) Dienstkleidung", "Im Dienst ist die vom Arbeitgeber vorgegebene Dienstkleidung zu tragen.")
        self.add_paragraph("§ 26) Verhalten in Sozialen Medien", "(1) Es duerfen keine Fotos von Einsaetzen oder Patienten hochgeladen werden.\n(2) Es duerfen keine menschenverachtenden Bilder veroeffentlicht werden.")
        self.add_paragraph("§ 27) Einhaltung von Sicherheitsvorschriften", "Der Arbeitnehmer verpflichtet sich, saemtliche Gesundheits- und Sicherheitsvorschriften, insbesondere das Tragen der PSA, strikt einzuhalten.")
        self.add_paragraph("§ 28) Rueckzahlungsklausel fuer Ausbildungskosten", "Bei Kuendigung durch den Arbeitnehmer binnen 8 Wochen nach Abschluss der Ausbildung sind 75% der Kosten zurueckzuzahlen.")
        self.add_paragraph("§ 29) Schlussbestimmungen", "Bei Beendigung sind saemtliche im Besitz befindlichen Geschaeftsunterlagen, Schluessel und Dienstfahrzeuge zurueckzugeben. Es gilt deutsches Sachrecht.")

        # UNTERSCHRIFTEN
        self.ln(20); y_pos = self.get_y()
        if y_pos > 220: self.add_page(); y_pos = 50
        y_linie = y_pos + 20
        try:
            sig_url = "https://r2.fivemanage.com/duNnRRRqkxrMPfikEWhQR/Unterschriftleon.png"
            self.image(BytesIO(requests.get(sig_url).content), x=25, y=y_pos - 15, h=55)
        except: pass
        self.line(15, y_linie, 85, y_linie)
        self.set_xy(15, y_linie + 2); self.set_font('Helvetica', 'B', 10); self.cell(70, 7, "Dr. med. Leon Müller", align='C')
        self.set_font('Courier', 'I', 14); self.set_text_color(0, 32, 96); self.set_xy(125, y_linie - 12); self.cell(70, 10, d['name'], align='C')
        self.set_draw_color(0, 0, 0); self.line(125, y_linie, 195, y_linie)
        self.set_text_color(0, 0, 0); self.set_font('Helvetica', 'B', 10); self.set_xy(125, y_linie + 2); self.cell(70, 7, d['name'], align='C')
        return self.output(dest='S')


# ==========================================
# 2. DATEN-KONFIGURATION
# ==========================================

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
    "Notarzt": {
        "titel": "NOTARZT",
        "text_oben": "hat am heutigen Tage die Prüfung zur Anerkennung der Notarztqualifikation in Bezug auf die besondere fachliche Eignung für den Einsatz im Rettungsdienst der Stadt Falkenfurt erfolgreich abgelegt. Auf Grundlage von § 12 Abs. 5 des Rettungsdienst-Gesetzes wird hiermit die Erlaubnis erteilt, die Zusatzbezeichnung",
        "text_unten": "zu führen. Diese Urkunde berechtigt zur Wahrnehmung der ärztlichen Aufgaben im Rahmen der Notfallrettung und zur Leitung der medizinischen Maßnahmen."
    },
    "Leitender Notarzt": {
        "titel": "LEITENDER NOTARZT",
        "text_oben": "hat am heutigen Tage die Prüfung zur Anerkennung als Leitender Notarzt in Bezug auf die besondere fachliche Eignung für den Einsatz im Rettungsdienst der Stadt Falkenfurt erfolgreich abgelegt. Auf Grundlage von § 12 Abs. 5 des einschlägigen Rettungsdienstgesetzes wird hiermit die Erlaubnis erteilt die Funktionsbezeichnung",
        "text_unten": "zu führen. Diese Urkunde berechtigt zur Wahrnehmung der medizinischen Führungsaufgaben bei Großschadensereignissen sowie zur Ausübung der medizinischen Weisungsbefugnis."
    },
    "Einsatzleiter RD": {
        "titel": "EINSATZLEITER RETTUNGSDIENST",
        "text_oben": "hat am heutigen Tage die Prüfung zur Anerkennung als Einsatzleiter Rettungsdienst in Bezug auf die besondere fachliche Eignung für den Einsatz im Rettungsdienst der Stadt Falkenfurt erfolgreich abgelegt. Auf Grundlage von § 12 Abs. 5 des einschlägigen Rettungsdienstgesetzes wird hiermit die Erlaubnis erteilt die Funktionsbezeichnung",
        "text_unten": "zu führen. Diese Urkunde berechtigt zur Wahrnehmung der operativen Koordinierung komplexer Einsatzlagen sowie zur Führung der eingesetzten Rettungsmittel am Einsatzort."
    },
    "Org. Leiter RD": {
        "titel": "ORGANISATORISCHER LEITER",
        "text_oben": "hat am heutigen Tage die Prüfung zur Anerkennung als Organisatorischer Leiter Rettungsdienst in Bezug auf die besondere fachliche Eignung für den Einsatz im Rettungsdienst der Stadt Falkenfurt erfolgreich abgelegt. Auf Grundlage von § 12 Abs. 5 des einschlägigen Rettungsdienstgesetzes wird hiermit die Erlaubnis erteilt die Funktionsbezeichnung",
        "text_unten": "zu führen. Diese Urkunde berechtigt zur Wahrnehmung der organisatorisch-taktischen Leitungsaufgaben bei Großeinsatzlagen sowie zur Koordination der Logistik und Raumordnung."
    },
    "Ausbilder RS": {
        "titel": "AUSBILDER RS",
        "text_oben": "hat am heutigen Tage die Prüfung zur Anerkennung als Ausbilder für Rettungssanitäter in Bezug auf die besondere fachliche und methodische Eignung für den Einsatz im Rettungsdienst der Stadt Falkenfurt erfolgreich abgelegt. Auf Grundlage von § 12 Abs. 5 des einschlägigen Rettungsdienstgesetzes wird hiermit die Erlaubnis erteilt, die Funktionsbezeichnung",
        "text_unten": "zu führen. Diese Urkunde berechtigt zur Vermittlung der Grundlagen der Notfallmedizin und des Krankentransports sowie zur Abnahme interner Leistungsnachweise."
    },
    "Ausbilder NFS": {
        "titel": "AUSBILDER NFS",
        "text_oben": "hat am heutigen Tage die Prüfung zur Anerkennung als Ausbilder für Notfallsanitäter in Bezug auf die besondere fachliche und pädagogische Eignung für den Einsatz im Rettungsdienst der Stadt Falkenfurt erfolgreich abgelegt. Auf Grundlage von § 12 Abs. 5 des einschlägigen Rettungsdienstgesetzes wird hiermit die Erlaubnis erteilt, die Funktionsbezeichnung",
        "text_unten": "zu führen. Diese Urkunde berechtigt zur Vermittlung invasiver Maßnahmen, der Durchführung von Simulationstrainings sowie zur fachlichen Vorbereitung auf Prüfungen."
    },
    "Ausbilder NA": {
        "titel": "AUSBILDER NA",
        "text_oben": "hat am heutigen Tage die Prüfung zur Anerkennung als Ausbilder für den Notarztdienst in Bezug auf die besondere fachliche und didaktische Eignung für den Einsatz im Rettungsdienst der Stadt Falkenfurt erfolgreich abgelegt. Auf Grundlage von § 12 Abs. 5 des einschlägigen Rettungsdienstgesetzes wird hiermit die Erlaubnis erteilt, die Funktionsbezeichnung",
        "text_unten": "zu führen. Diese Urkunde berechtigt zur Durchführung von klinisch-praktischen Einweisungen sowie zur Supervision von Notärzten in der Anerkennungsphase."
    },
    "Ernennung": {
        "titel": "POSITION",
        "text_oben": "wird am heutigen Tage in Bezug auf die besondere fachliche und persönliche Eignung für den Rettungsdienst der Stadt Falkenfurt ernannt. Auf Grundlage der internen Organisationsrichtlinien wird hiermit die Erlaubnis erteilt, die Position",
        "text_unten": "wahrzunehmen. Diese Urkunde berechtigt zur Führung des zugeordneten Fachbereiches, zur Ausübung der damit verbundenen Weisungsbefugnisse sowie zur eigenverantwortlichen Leitung der zugewiesenen Dienstgeschäfte."
    }
}

ernennungs_rollen = ["Wachleiter", "Leiter Rettungsdienstschule", "Leiter Rettungsdienst", "Personalabteilungsleitung"]

# ==========================================
# 3. STREAMLIT APP OBERFLÄCHE
# ==========================================

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
        if st.form_submit_button("Urkunde generieren"):
            if u_name and u_geb:
                pdf = RDF_Urkunden_Master()
                u_pdf_data = pdf.generate_pdf(u_name, u_geb, u_datum, aussteller_liste[wahl_boss], urkundentypen[wahl_typ], extra_pos)

    if u_pdf_data:
        st.success("✅ Urkunde bereit!")
        st.download_button("⬇️ Urkunde herunterladen", data=bytes(u_pdf_data), file_name=f"Urkunde_{u_name.replace(' ','_')}.pdf")

# --- TAB 2: HR ---
with t2:
    st.header("HR Dokumenten-Management")
    hr_wahl = st.selectbox("Dokument wählen", ["Kündigung (Angestellt)", "Kündigung (Azubi)", "Abmahnung", "Suspendierung", "Arbeitsvertrag (Vollständig)"])
    
    hr_pdf_data = None
    with st.form("hr_form_universal"):
        empfaenger = st.text_input("Name des Empfängers")
        bearbeiter = st.text_input("Unterschrift links (Dein Name)")
        d_heute = st.date_input("Heutiges Datum", value=datetime.now()).strftime("%d.%m.%Y")
        
        # Felder je nach Wahl
        if hr_wahl == "Kündigung (Angestellt)":
            d_ende = st.date_input("Kündigung zum", value=datetime.now()).strftime("%d.%m.%Y")
            titel = "KÜNDIGUNG DES ARBEITSVERHÄLTNISSES"
            text = (f"Sehr geehrte/r Frau/Herr {empfaenger},\n\nhiermit kündigen wir das mit Ihnen bestehende Arbeitsverhältnis ordentlich zum {d_ende}.\n\n"
                    "Wir weisen Sie auf Ihre Meldepflicht bei der Agentur für Arbeit hin. Bitte geben Sie alle Ausrüstungsgegenstände bis zum letzten Arbeitstag ab.")
        
        elif hr_wahl == "Kündigung (Azubi)":
            beruf = st.text_input("Ausbildungsberuf", value="Notfallsanitäter")
            d_ende = st.date_input("Ende zum", value=datetime.now()).strftime("%d.%m.%Y")
            titel = "KÜNDIGUNG DES BERUFSAUSBILDUNGSVERHÄLTNISSES"
            text = (f"Sehr geehrte/r Frau/Herr {empfaenger},\n\nhiermit kündigen wir das Ausbildungsverhältnis zum/zur {beruf} zum {d_ende}.\n\n"
                    "Sofern Sie sich in der Probezeit befinden, erfolgt dies gemäß § 22 BBiG ohne Frist.")

        elif hr_wahl == "Abmahnung":
            grund = st.text_area("Sachverhalt (Fehlverhalten)")
            v_datum = st.date_input("Vorfall am").strftime("%d.%m.%Y")
            titel = "ABMAHNUNG"
            text = (f"Sehr geehrte/r Frau/Herr {empfaenger},\n\nhiermit mahnen wir Sie wegen folgendem Vorfall am {v_datum} ab:\n\n{grund}\n\n"
                    "Ein Wiederholungsfall kann zur Kündigung führen.")

        elif hr_wahl == "Suspendierung":
            grund_susp = st.text_area("Grund der Suspendierung")
            ende_susp = st.text_input("Suspendiert bis zum", value="auf Weiteres")

        elif hr_wahl == "Arbeitsvertrag (Vollständig)":
            funktion = st.text_input("Position/Funktion", value="Notfallsanitäter")

        if st.form_submit_button("Dokument generieren"):
            if empfaenger and bearbeiter:
                if hr_wahl == "Suspendierung":
                    pdf = Falkenfurt_Suspendierung()
                    hr_pdf_data = pdf.generate({'name_empfaenger': empfaenger, 'bearbeiter_name': bearbeiter, 'datum_heute': d_heute, 'ende_suspendierung': ende_susp, 'grund': grund_susp})
                elif hr_wahl == "Arbeitsvertrag (Vollständig)":
                    pdf = Falkenfurt_Full_Contract()
                    hr_pdf_data = pdf.generate({'name': empfaenger, 'funktion': funktion, 'datum': d_heute})
                else:
                    pdf = Falkenfurt_HR_Master()
                    hr_pdf_data = pdf.generate_doc(titel, text, {'datum_heute': d_heute, 'bearbeiter_name': bearbeiter})

    if hr_pdf_data:
        st.success(f"✅ {hr_wahl} bereit!")
        st.download_button("⬇️ Dokument herunterladen", data=bytes(hr_pdf_data), file_name=f"{hr_wahl.replace(' ','_')}.pdf")
