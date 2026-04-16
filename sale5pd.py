import streamlit as st

# Grundkonfiguration
st.set_page_config(page_title="SALE FvPD | San Andreas", page_icon="🚔", layout="wide")

# Navigation in der Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Gehe zu:", ["Home", "Über uns", "Team"])

# --- HOME PAGE ---
if page == "Home":
    col1, space, col2 = st.columns([1.2, 0.2, 1])
    with col1:
        st.markdown('<h1 style="font-size: 60px;">DEIN <span style="color: #0047AB;">LAW ENFORCEMENT</span><br>NEXT LEVEL.</h1>', unsafe_allow_html=True)
        st.write("Willkommen auf der offiziellen Seite von San Andreas Law Enforcement.")
        st.button("🚀 Jetzt Starten")
    
    with col2:
        st.info("Server-Status-Box (hier kommt dein Dashboard-Code rein)")

# --- ÜBER UNS PAGE ---
elif page == "Über uns":
    st.title("📖 Über das Projekt")
    
    col_text, col_img = st.columns([2, 1])
    with col_text:
        st.markdown("""
        ### Unsere Vision
        San Andreas Law Enforcement (SALE) wurde mit dem Ziel ins Leben gerufen, das realistischste 
        Polizei-Roleplay in der FiveM-Szene zu bieten. Wir legen Wert auf:
        
        * **Qualität vor Quantität:** Jeder Officer durchläuft eine fundierte Ausbildung.
        * **Technische Innovation:** Eigene Skripte für MDT, Funk und Interaktion.
        * **Fairness:** Ein transparentes Regelwerk für alle Spieler.
        
        ### Das FvPD
        Das *Fort Valley Police Department* ist unser Herzstück. Es repräsentiert eine moderne 
        Polizeibehörde, die mit modernster Technik gegen die Kriminalität in San Andreas vorgeht.
        """)
    with col_img:
        # Hier könntest du ein Bild von eurem PD oder ein Logo einfügen
        st.image("https://via.placeholder.com/400x300.png?text=FvPD+Impressionen", caption="Unser Hauptquartier")

# --- TEAM PAGE ---
elif page == "Team":
    st.title("👥 Das Team hinter SALE")
    st.write("Die Administration und Leitung des Projekts.")
    
    # Beispiel für Team-Karten in Spalten
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    
    with row1_col1:
        st.image("https://via.placeholder.com/150", width=150) # Platzhalter für Profilbild
        st.subheader("Name 1")
        st.caption("Projektleitung / Founder")
        st.write("Zuständig für die technische Entwicklung und Vision.")

    with row1_col2:
        st.image("https://via.placeholder.com/150", width=150)
        st.subheader("Name 2")
        st.caption("Chief of Police")
        st.write("Leitet das operative Geschäft des FvPD.")

    with row1_col3:
        st.image("https://via.placeholder.com/150", width=150)
        st.subheader("Name 3")
        st.caption("Community Management")
        st.write("Ansprechpartner für Sorgen und Wünsche der Spieler.")

    st.divider()
    st.info("Du möchtest Teil des Teams werden? Schau im Discord vorbei!")
