import streamlit as st

# Grundkonfiguration
st.set_page_config(page_title="SALE FvPD | San Andreas", page_icon="🚔", layout="wide")

# Custom CSS für den Look (Schriftgrößen und Abstände)
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .big-font {
        font-size: 60px !important;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 20px;
    }
    .highlight {
        color: #0047AB; /* Dein Polizei-Blau */
    }
    .status-card {
        background-color: #1a1c24;
        border-radius: 15px;
        padding: 25px;
        border: 1px solid #2d2f39;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HERO SECTION ---
col1, space, col2 = st.columns([1.2, 0.2, 1])

with col1:
    st.markdown('<p style="color: #0047AB; font-weight: bold;">● Season 1 – Jetzt Live</p>', unsafe_allow_html=True)
    st.markdown('<div class="big-font">DEIN <span class="highlight">LAW ENFORCEMENT</span><br>NEXT LEVEL.</div>', unsafe_allow_html=True)
    st.write(
        "Erlebe San Andreas so realistisch wie nie zuvor. "
        "High-Performance, spezialisierte Departments und eine "
        "Community, die echtes Teamplay schätzt."
    )
    
    # Buttons nebeneinander
    btn_col1, btn_col2 = st.columns([1, 1.5])
    with btn_col1:
        st.button("🚀 Jetzt Starten", use_container_width=True)
    with btn_col2:
        st.button("💬 Discord beitreten", use_container_width=True)

with col2:
    # Die Status-Box (ähnlich wie im Bild)
    with st.container():
        st.markdown("""
        <div class="status-card">
            <div style="display: flex; justify-content: space-between;">
                <span style="font-weight: bold;">SALE FvPD</span>
                <span style="color: #2ecc71;">● Online</span>
            </div>
            <p style="color: gray; font-size: 0.8em;">FiveM Roleplay · San Andreas</p>
            <h1 style="margin-top: 20px; margin-bottom: 0;">14</h1>
            <p style="color: gray;">Spieler aktiv</p>
            <hr style="border-color: #2d2f39;">
            <div style="display: flex; justify-content: space-between; font-size: 0.9em;">
                <div><strong>64</strong><br><span style="color: gray;">Max. Slots</span></div>
                <div><strong>22ms</strong><br><span style="color: gray;">Latenz</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- WEITERE FEATURES (Unterm Hero) ---
st.write("---")
feat1, feat2, feat3 = st.columns(3)
with feat1:
    st.subheader("🚔 Realismus")
    st.write("Strenges Regelwerk für maximale Immersion.")
with feat2:
    st.subheader("🔧 Technik")
    st.write("Eigene Scripts und optimierte Performance.")
with feat3:
    st.subheader("🤝 Community")
    st.write("Ein faires Miteinander auf Augenhöhe.")
