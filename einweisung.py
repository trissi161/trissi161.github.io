import streamlit as st
import requests

# Konfiguration (Diese Werte später in Streamlit Secrets eintragen!)
DISCORD_BOT_TOKEN = st.secrets["MTUwMTMwOTAwMjA3NDY4OTY2Nw.G7hjIJ.mrYXpBNs-wToyIhWUuk7Q7RYSB0R9vA2RfSqdY"]
GUILD_ID = st.secrets["1347693028667822204"]
ROLE_ID = st.secrets["1347693028684464278"]

st.set_page_config(page_title="PD Einweisung", page_icon="🚔")

st.title("🚔 PD Einweisung & Onboarding")
st.write("Bitte lies dir das folgende Dokument aufmerksam durch.")

# 1. Das Dokument in einer scrollbaren Box
document_html = """
<div style="height: 400px; overflow-y: scroll; padding: 15px; border: 1px solid #333; border-radius: 10px; background-color: #1e1e1e; color: #ffffff;">
    <h2>Dienstanweisung Police Department</h2>
    <p><strong>§1 Verhalten im Dienst:</strong> Jeder Beamte hat sich respektvoll zu verhalten...</p>
    <p>... hier dein extrem langer Text für die Einweisung ...</p>
    <p>... noch mehr Text ...</p>
    <hr>
    <p style='text-align: center;'>--- ENDE DES DOKUMENTS ---</p>
</div>
"""
st.markdown(document_html, unsafe_allow_html=True)

st.divider()

# 2. Identifizierung & Bestätigung
discord_id = st.text_input("Deine Discord User-ID (Zahlenfolge):", placeholder="z.B. 123456789012345678")
st.caption("Deine ID findest du in Discord unter 'Benutzereinstellungen > Erweitert > Entwicklermodus an' -> Rechtsklick auf dein Profil -> ID kopieren.")

confirm = st.checkbox("Ich bestätige, dass ich die Einweisung vollständig gelesen und verstanden habe.")

# 3. Logik zur Rollenvergabe
if st.button("Einweisung abschließen & Rolle erhalten", disabled=not confirm):
    if not discord_id:
        st.error("Bitte gib deine Discord-ID ein.")
    else:
        # API Call an Discord (Rolle zuweisen)
        url = f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{discord_id}/roles/{ROLE_ID}"
        headers = {
            "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.put(url, headers=headers)
        
        if response.status_code == 204:
            st.success("✅ Erfolg! Die Cop-Rolle wurde dir auf dem Discord zugewiesen.")
            st.balloons()
        elif response.status_code == 404:
            st.error("❌ User nicht gefunden. Bist du sicher, dass du auf dem Server bist?")
        else:
            st.error(f"❌ Fehler: {response.status_code}. Kontaktiere einen Admin.")
