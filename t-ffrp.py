import streamlit as st
import pandas as pd

st.title("Verbindungstest")

# Deine ID aus der URL
SHEET_ID = "1TZHjV7RTrE27p-hapfMe11eCUXhS9QFAd53OCQjpeOc"

# Wir versuchen die Daten als CSV-Export zu ziehen (sehr stabil)
url_p = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=P"
url_b = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=B"

st.write("Versuche Blatt 'P' zu laden...")
try:
    df_p = pd.read_csv(url_p)
    st.success("Erfolg! Blatt 'P' wurde geladen:")
    st.dataframe(df_p)
except Exception as e:
    st.error(f"Fehler bei Blatt 'P': {e}")

st.write("Versuche Blatt 'B' zu laden...")
try:
    df_b = pd.read_csv(url_b)
    st.success("Erfolg! Blatt 'B' wurde geladen:")
    st.dataframe(df_b)
except Exception as e:
    st.error(f"Fehler bei Blatt 'B': {e}")
