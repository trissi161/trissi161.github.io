import streamlit as st

# Seiten-Konfiguration (Tab-Titel und Icon)
st.set_page_config(page_title="SALE FvPD | San Andreas", page_icon="🚔", layout="wide")

# --- HEADER ---
st.title("🚔 San Andreas Law Enforcement")
st.subheader("Fort Valley Police Department - Official Representation")

# --- NAVIGATION (Sidebar) ---
st.sidebar.image("https://dein-logo-link.png", width=150) # Falls du ein Logo hast
menu = st.sidebar.radio("Navigation", ["Home", "Features", "Regelwerk", "Bewerbung"])

if menu == "Home":
    st.image("https://dein-cooles-bild.jpg", caption="To Protect and to Serve")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Server Status", value="Online", delta="Ping: 24ms")
    with col2:
        st.metric(label="Officer im Dienst", value="12", delta="Aktiv")
    with col3:
        st.metric(label="Bürger-Zufriedenheit", value="98%")

    st.markdown("""
    ### Willkommen beim FvPD
    Wir sind die führende Exekutivbehörde in San Andreas. Unser Fokus liegt auf 
    **realistischem Roleplay**, professioneller Ausbildung und modernster Technik.
    """)

elif menu == "Features":
    st.header("Unsere Highlights")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("### 🏎️ Moderner Fuhrpark")
        st.write("Vom klassischen Crown Vic bis zum modernen Interceptor – alles mit Custom-Handling.")
    with col_b:
        st.info("### 💻 Eigenes MDT")
        st.write("Unser Mobile Data Terminal erlaubt Abfragen in Echtzeit direkt aus dem Streifenwagen.")

elif menu == "Regelwerk":
    st.header("Verhaltenskodex")
    st.warning("Das Missachten der Dienstvorschriften führt zu Disziplinarmaßnahmen.")
    with st.expander("§1 Eigensicherung"):
        st.write("Die Eigensicherung hat stets oberste Priorität...")
    with st.expander("§2 Funkdisziplin"):
        st.write("Kurz, prägnant und nach 10-Codes.")

elif menu == "Bewerbung":
    st.header("Werde Teil des Teams")
    st.write("Wir suchen ständig motivierte Rekruten!")
    
    with st.form("apply_form"):
        name = st.text_input("Name (IC)")
        alter = st.number_input("Alter (OOC)", min_value=16)
        erfahrung = st.text_area("Bisherige Erfahrungen im RP")
        submit = st.form_submit_button("Bewerbung absenden")
        
        if submit:
            st.success(f"Danke {name}! Deine Bewerbung wurde an die Personalabteilung übermittelt.")
