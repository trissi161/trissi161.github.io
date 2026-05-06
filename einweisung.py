import streamlit as st
import requests
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Konfiguration aus Streamlit Secrets
DISCORD_BOT_TOKEN = st.secrets["DISCORD_TOKEN"]
GUILD_ID = st.secrets["GUILD_ID"]
ROLE_ID = st.secrets["ROLE_ID"]

# Seite einrichten
st.set_page_config(page_title="PD Einweisung", page_icon="🚔")

# Verbindung zu Google Sheets herstellen
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. DATEN LADEN
try:
    # ttl=0 sorgt dafür, dass wir immer die frischesten Daten ziehen
    df = conn.read(ttl=0)
except Exception as e:
    st.error(f"Verbindung zum Google Sheet fehlgeschlagen: {e}")
    df = pd.DataFrame()

st.title("🚔 PD Einweisung & Onboarding")

# 2. DOKUMENT ANZEIGEN
st.write("Bitte lies dir das folgende Dokument aufmerksam durch.")
document_html = """
<div style="height: 400px; overflow-y: scroll; padding: 15px; border: 1px solid #333; border-radius: 10px; background-color: #1e1e1e; color: #ffffff;">
    <h2>Dienstanweisung Police Department</h2>
    <p><strong>§1 Verhalten im Dienst:</strong> Jeder Beamte hat sich respektvoll zu verhalten...</p>
    <p>... hier dein ausführlicher Text für die Einweisung ...</p>
    <p>Füge hier alle Regeln ein, die für deine Cops wichtig sind.</p>
    <hr>
    <p style='text-align: center;'>--- ENDE DES DOKUMENTS ---</p>
</div>
"""
st.markdown(document_html, unsafe_allow_html=True)

st.divider()

# 3. FORMULAR-BEREICH
st.subheader("Persönliche Angaben & Dienstnummer")

# Dienstnummer-Auswahl aus dem Sheet
ausgewaehlte_nr = None
if not df.empty and 'Dienstnummer' in df.columns and 'Name' in df.columns:
    # Filter: Nur Nummern anzeigen, wo die Spalte 'Name' leer ist
    freie_nummern = df[df['Name'].isna() | (df['Name'] == "")]['Dienstnummer'].tolist()
    
    if freie_nummern:
        ausgewaehlte_nr = st.selectbox("Wähle eine freie Dienstnummer:", freie_nummern)
    else:
        st.warning("Momentan sind keine Dienstnummern frei! Kontaktiere einen Admin.")
else:
    st.error("Fehler: Das Google Sheet konnte nicht geladen werden oder die Spalten 'Dienstnummer'/'Name' fehlen.")

# Namenseingabe für das Sheet
name_eingabe = st.text_input("Dein Name (Vorname_Nachname):", placeholder="z.B. Max_Mustermann")

# Discord ID Eingabe
discord_id = st.text_input("Deine Discord User-ID (Zahlenfolge):", placeholder="z.B. 123456789012345678")
st.caption("Rechtsklick auf dein Profil in Discord -> ID kopieren (Entwicklermodus muss an sein).")

# Bestätigung
confirm = st.checkbox("Ich bestätige, dass ich die Einweisung vollständig gelesen und verstanden habe.")

st.divider()

# 4. ABSCHLUSS-LOGIK
if st.button("Einweisung abschließen", disabled=not confirm):
    if not discord_id or not name_eingabe or not ausgewaehlte_nr:
        st.error("Bitte fülle alle Felder aus (Name, ID und Dienstnummer).")
    else:
        # --- A. DISCORD ROLLE VERGEBEN ---
        url = f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{discord_id}/roles/{ROLE_ID}"
        headers = {
            "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        try:
            discord_response = requests.put(url, headers=headers)
            
            if discord_response.status_code == 204:
                # --- B. GOOGLE SHEET AKTUALISIEREN ---
                try:
                    # 1. Den Index der gewählten Dienstnummer finden
                    idx = df.index[df['Dienstnummer'] == ausgewaehlte_nr].tolist()[0]
                    
                    # 2. Nur den Namen im lokalen Abbild (df) ändern
                    df.at[idx, 'Name'] = name_eingabe
                    
                    # 3. Das gesamte Sheet aktualisieren
                    # Da wir gspread im Hintergrund nutzen, ist das die sicherste Methode
                    conn.update(data=df)
                    
                    st.success(f"✅ Erfolg! Die Rolle wurde zugewiesen und Dienstnummer {ausgewaehlte_nr} auf deinen Namen reserviert.")
                    st.balloons()
                    
                    # Cache leeren, damit beim nächsten Laden die Nummer weg ist
                    st.cache_data.clear()
                    
                except Exception as sheet_error:
                    st.error(f"Rolle vergeben, aber Fehler beim Google Sheet Eintrag: {sheet_error}")
                    st.info("Bitte informiere einen Admin, dass dein Name nicht im Sheet eingetragen werden konnte.")
                    
                    # Cache leeren, damit die Nummer beim nächsten Laden weg ist
                    st.cache_data.clear()
                    
                except Exception as sheet_error:
                    st.error(f"Rolle vergeben, aber Fehler beim Google Sheet Eintrag: {sheet_error}")
                    st.info("Bitte informiere einen Admin, dass dein Name nicht im Sheet eingetragen werden konnte.")
            
            elif discord_response.status_code == 404:
                st.error("❌ User-ID nicht gefunden. Bist du sicher, dass du auf dem Discord-Server bist?")
            elif discord_response.status_code == 403:
                st.error("❌ Bot hat keine Berechtigung. Die Bot-Rolle muss in Discord ÜBER der Cop-Rolle stehen!")
            else:
                st.error(f"❌ Discord-Fehler: {discord_response.status_code}")
                
        except Exception as e:
            st.error(f"Ein technischer Fehler ist aufgetreten: {e}")
