import streamlit as st

# Grundkonfiguration
st.set_page_config(page_title="SALE FvPD | FivePD Server", page_icon="🚔", layout="wide")

# --- CUSTOM DESIGN (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .big-font { font-size: 55px !important; font-weight: 800; line-height: 1.1; margin-bottom: 20px; color: white; }
    .highlight { color: #0047AB; }
    .status-card {
        background-color: #1a1c24;
        border-radius: 15px;
        padding: 25px;
        border: 1px solid #2d2f39;
        color: white;
    }
    .team-card {
        background-color: #1a1c24;
        border-radius: 10px;
        padding: 20px;
        border-bottom: 4px solid #0047AB;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---
st.sidebar.title("🚔 SALE FvPD")
page = st.sidebar.radio("Navigation", ["Startseite", "Über uns", "Team-Leitung"])

# --- SEITE: STARTSEITE ---
if page == "Startseite":
    col1, space, col2 = st.columns([1.2, 0.2, 1])

    with col1:
        st.markdown('<p style="color: #0047AB; font-weight: bold; margin-bottom: 0;">● Season 1 – FivePD Experience</p>', unsafe_allow_html=True)
        st.markdown('<div class="big-font">DEIN <span class="highlight">FIVE PD</span><br>NEXT LEVEL.</div>', unsafe_allow_html=True)
        st.write(
            "Erlebe den ultimativen LSPD:FR Online Server. "
            "Realistische KI-Einsätze, professionelle Strukturen und eine "
            "starke Community warten auf dich bei San Andreas Law Enforcement."
        )
        
        btn_col1, btn_col2 = st.columns([1, 1.2])
        with btn_col1:
            st.button("🚀 Server beitreten", use_container_width=True)
        with btn_col2:
            st.button("💬 Discord Community", use_container_width=True)

    with col2:
        st.markdown(f"""
        <div class="status-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: bold; font-size: 1.2em;">SALE FvPD</span>
                <span style="color: #2ecc71; font-size: 0.9em;">● Online</span>
            </div>
            <p style="color: gray; font-size: 0.8em; margin-bottom: 20px;">FivePD Framework · GTA V</p>
            <h1 style="margin: 0; font-size: 3em;">14</h1>
            <p style="color: gray; margin-bottom: 20px;">Officer im Dienst</p>
            <hr style="border: 0; border-top: 1px solid #2d2f39; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.9em;">
                <div><strong>64</strong><br><span style="color: gray;">Slots</span></div>
                <div><strong>24ms</strong><br><span style="color: gray;">Latenz</span></div>
                <div><strong>EU</strong><br><span style="color: gray;">Region</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- SEITE: ÜBER UNS ---
elif page == "Über uns":
    st.markdown('<div class="big-font">WAS IST <span class="highlight">SALE FvPD?</span></div>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("""
        ### Die Mission
        SALE FvPD bringt das bekannte **LSPD:FR Erlebnis** in den Multiplayer. 
        Wir nutzen das **FivePD Framework**, um Spielern die Möglichkeit zu geben, 
        gemeinsam gegen die KI-Kriminalität in San Andreas vorzugehen.
        
        ### Was uns ausmacht:
        * **Sync & Performance:** Ein flüssiges Erlebnis trotz vieler KI-Einsätze.
        * **Callouts:** Eine riesige Auswahl an verschiedenen Einsatzszenarien.
        * **Progression:** Steige im Rang auf und schalte neue Fahrzeuge und Ausrüstung frei.
        * **Kooperation:** Hier wird Teamwork großgeschrieben – kein "Gambo", sondern taktisches Vorgehen.
        """)
    with col_b:
        st.info("**Info für Neulinge:**\n\nDu brauchst keine lokalen Mods. Einfach über FiveM joinen und das FvPD-System lädt alles Notwendige automatisch!")

# --- SEITE: TEAM ---
elif page == "Team-Leitung":
    st.markdown('<div class="big-font">UNSER <span class="highlight">TEAM</span></div>', unsafe_allow_html=True)
    st.write("Die administrativen Köpfe hinter dem San Andreas Law Enforcement Projekt.")
    
    t_col1, t_col2, t_col3 = st.columns(3)
    
    team_members = [
        {"name": "AdminName1", "rank": "Projektleitung", "desc": "Zuständig für Technik & Hosting."},
        {"name": "AdminName2", "rank": "Management", "desc": "Zuständig für Regeln & Community."},
        {"name": "AdminName3", "rank": "Supportleitung", "desc": "Dein Ansprechpartner bei Problemen."}
    ]
    
    cols = [t_col1, t_col2, t_col3]
    for i, member in enumerate(team_members):
        with cols[i]:
            st.markdown(f"""
            <div class="team-card">
                <h3 style="margin-bottom: 5px;">{member['name']}</h3>
                <p style="color: #0047AB; font-weight: bold; margin-bottom: 15px;">{member['rank']}</p>
                <p style="font-size: 0.9em; color: #bdc3c7;">{member['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
