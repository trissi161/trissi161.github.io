# --- TAB 2: HR ---
with t2:
    st.header("HR Dokumenten-Management")
    hr_wahl = st.selectbox("Dokument wählen", ["Kündigung (Angestellt)", "Kündigung (Azubi)", "Abmahnung", "Suspendierung", "Arbeitsvertrag (Vollständig)"])
    
    hr_pdf_data = None
    with st.form("hr_form_universal"):
        empfaenger = st.text_input("Name des Empfängers")
        bearbeiter = st.text_input("Unterschrift links (Dein Name)")
        d_heute = st.date_input("Heutiges Datum", value=datetime.now()).strftime("%d.%m.%Y")
        
        # 1. Variablen vorbereiten (muss VOR der Text-Zuweisung passieren)
        if hr_wahl == "Kündigung (Angestellt)":
            v_datum = st.date_input("Kündigung zum (Datum)").strftime("%d.%m.%Y")
            titel = "KÜNDIGUNG DES ARBEITSVERHÄLTNISSES"
            text = (f"Sehr geehrte/r Frau/Herr {empfaenger},\n\n"
                    f"hiermit kündigen wir das mit Ihnen bestehende Arbeitsverhältnis ordentlich unter Einhaltung der vertraglich vereinbarten Kündigungsfrist zum {v_datum}.\n\n"
                    f"Hilfsweise kündigen wir zum nächstmöglichen Termin.\n\n"
                    f"Wir weisen Sie ausdrücklich darauf hin, dass Sie gemäß § 38 Abs. 1 SGB III verpflichtet sind, sich spätestens drei Monate vor Beendigung des Arbeitsverhältnisses persönlich bei der Agentur für Arbeit arbeitssuchend zu melden.\n\n"
                    f"Bitte geben Sie sämtliche in Ihrem Besitz befindliche Ausrüstungsgegenstände, Schlüssel sowie Dienstausweise bis spätestens zu Ihrem letzten Arbeitstag bei der Dienststellenleitung ab.\n\n"
                    f"Für Ihren weiteren Weg wünschen wir Ihnen alles Gute.")
        
        elif hr_wahl == "Kündigung (Azubi)":
            beruf = st.text_input("Ausbildungsberuf", value="Notfallsanitäter")
            v_datum = st.date_input("Ende zum (Datum)").strftime("%d.%m.%Y")
            titel = "KÜNDIGUNG DES BERUFSAUSBILDUNGSVERHÄLTNISSES"
            text = (f"Sehr geehrte/r Frau/Herr {empfaenger},\n\n"
                    f"hiermit kündigen wir das mit Ihnen bestehende Ausbildungsverhältnis zum/zur {beruf} "
                    f"unter Einhaltung der maßgeblichen Fristen zum {v_datum}.\n\n"
                    f"Sofern Sie sich noch in der Probezeit befinden, erfolgt diese Kündigung gemäß § 22 Abs. 1 BBiG ohne Einhaltung einer Kündigungsfrist.\n\n"
                    f"Bitte geben Sie sämtliche Lehrmaterialien, Dienstkleidung und Schlüssel bis zum letzten Arbeitstag ab.\n\n"
                    f"Wir wünschen Ihnen für Ihren weiteren Werdegang viel Erfolg.")

        elif hr_wahl == "Abmahnung":
            v_datum = st.date_input("Vorfall am").strftime("%d.%m.%Y")
            grund = st.text_area("Sachverhalt (Fehlverhalten)")
            titel = "ABMAHNUNG"
            text = (f"Sehr geehrte/r Frau/Herr {empfaenger},\n\nhiermit mahnen wir Sie wegen folgendem Vorfall am {v_datum} ab:\n\n{grund}\n\n"
                    f"Durch dieses Verhalten verletzen Sie Ihre arbeitsvertraglichen Pflichten erheblich. Wir fordern Sie auf, Ihr Verhalten umgehend zu korrigieren.\n\n"
                    f"Im Falle einer Wiederholung werden wir das Arbeitsverhältnis kündigen. Eine Kopie dieser Abmahnung wird zu Ihrer Personalakte genommen.")

        elif hr_wahl == "Suspendierung":
            grund_susp = st.text_area("Grund der Suspendierung")
            ende_susp = st.text_input("Suspendiert bis zum", value="auf Weiteres")
            # Text wird hier in der Klasse Falkenfurt_Suspendierung generiert

        elif hr_wahl == "Arbeitsvertrag (Vollständig)":
            funktion = st.text_input("Position/Funktion", value="Notfallsanitäter")
            # Text wird hier in der Klasse Falkenfurt_Full_Contract generiert

        # 2. Submit Button (Wichtig: Muss im Form-Block bleiben!)
        submit_hr = st.form_submit_button("Dokument generieren")

        if submit_hr:
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
            else:
                st.warning("Bitte Namen des Empfängers und Bearbeiters ausfüllen.")

    if hr_pdf_data:
        st.success(f"✅ {hr_wahl} bereit!")
        st.download_button("⬇️ Dokument herunterladen", data=bytes(hr_pdf_data), file_name=f"{hr_wahl.replace(' ','_')}.pdf")
