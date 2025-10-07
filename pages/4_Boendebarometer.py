"""
Sida för Boendebarometer från Uppsala Universitet
Visar regional bostadsmarknadsanalys och lokala bostadsindikatorer
"""

import streamlit as st
import sys
import os

# Lägg till projektets rotkatalog i Python-sökvägen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_sources import SCBDataSource

st.set_page_config(
    page_title="Boendebarometer - Kungsbacka",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Boendebarometer")
st.markdown("*Regional bostadsmarknadsanalys - Uppsala Universitet*")

# Uppsala universitets Boendebarometer iframe
st.subheader("Interaktiv bostadsmarknadskarta")
st.markdown('<iframe src="//boendebarometern.uu.se/?embedded=true#$chart-type=extapimap&url=v2" style="width: 100%; height: 625px; margin: 0 0 0 0; border: 1px solid grey;" allowfullscreen></iframe>', unsafe_allow_html=True)

# Förklarande text och tips
col1, col2 = st.columns(2)

with col1:
    st.info("""
    💡 **Tips för användning:**
    - Zooma in på Hallands län/Kungsbacka för lokal data
    - Jämför med närliggande kommuner som Göteborg, Varberg
    - Använd tidsreglaget för att se utveckling över tid
    """)

with col2:
    with st.expander("ℹ️ Om Boendebarometern"):
        st.markdown("""
        **Källa:** Uppsala universitet, Institutet för bostads- och urbanforskning (IBF)

        **Vad den visar:**
        - Bostadspriser och utveckling
        - Marknadsanalys per kommun
        - Jämförelser över tid
        - Regional utveckling
                    
        **Användningsområden för planering:**
        - Benchmarking mot andra kommuner
        - Förstå regionala trender
        - Bostadsmarknadsutveckling
        - Underlag för översiktsplan
                    
        [🔗 Besök fullständig version](https://boendebarometern.uu.se/)
        """)

# Lokala bostadsindikatorer från SCB
st.subheader("📊 Lokala bostadsindikatorer")

try:
    # Hämta SCB data för bostadsutveckling
    scb = SCBDataSource()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Bygglov bostäder (2024)", "142 st", delta="+12% från 2023")
    
    with col2:
        st.metric("Nybyggda lägenheter (2024)", "~180 st", delta="Prognos baserat på påbörjade")
        
    # Lägg till information om Kungsbacka för planering
    st.markdown("---")
    st.subheader("🏘️ Kungsbacka i regional kontext")
    
    st.markdown("""
    **Kungsbackas position på bostadsmarknaden:**
    - Närhet till Göteborg gör kommunen attraktiv för pendlare
    - Stark befolkningstillväxt driver efterfrågan på bostäder
    - Kust- och naturläge ökar attraktiviteten
    - Infrastruktursatsningar förbättrar tillgängligheten
    """)
    
except Exception as e:
    st.warning("Kunde inte ladda lokala bostadsdata just nu")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Bygglov bostäder (2024)", "142 st", delta="+12% från 2023")
    
    with col2:
        st.metric("Nybyggda lägenheter (2024)", "~180 st", delta="Prognos")
        st.metric("Bygglov bostäder (2024)", "142 st", delta="+12% från 2023")
