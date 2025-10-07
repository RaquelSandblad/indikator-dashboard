"""
Kungsbacka Planeringsdashboard
Huvudsida - Navigation till alla undersidor
"""

import streamlit as st
from PIL import Image
import os
from datetime import datetime

# Streamlit konfiguration
st.set_page_config(
    page_title="Inledning - Kungsbacka",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS för bättre utseende
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .welcome-card {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Välkomstmeddelande
st.markdown("""
<div class="main-header">
    <h1 style="color: white; margin: 0;">🏙️ Inledning</h1>
    <p style="color: white; margin: 0.5rem 0 0 0; opacity: 0.9;">
        Verktyg för uppföljning av översiktsplanering och strategisk utveckling
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Välkommen!")
    st.write("Detta verktyg hjälper dig att:")
    st.markdown("""
    - **Följa upp** översiktsplanens genomförande
    - **Analysera** befolkningsutveckling och prognoser
    - **Visualisera** planbesked och byggprojekt på karta
    - **Hämta** aktuell data från SCB, Kolada och andra källor
    - **Jämföra** nyckeltal med andra kommuner
    """)
    
    # Senaste uppdatering
    today = datetime.now().strftime("%Y-%m-%d")
    st.info(f"📅 Senaste datauppdatering: {today}")

with col2:
    # Visa kommunbild om den finns
    try:
        if os.path.exists("image.png"):
            image = Image.open("image.png")
            st.image(image, caption="Kungsbacka kommun", use_container_width=True)
    except Exception as e:
        st.write("🏙️ Kungsbacka kommun")

# Snabbnavigation
st.markdown("---")
st.subheader("🧭 Navigera till:")

st.info("👈 Använd sidomenyn till vänster för att navigera mellan olika vyer")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📊 Översikt & Nyckeltal**")
    st.caption("Huvudnyckeltal och översikt")
    
    st.markdown("**📈 Befolkningsanalys**")
    st.caption("Detaljerad befolkningsdata")

with col2:
    st.markdown("**🗺️ Kartor & Planbesked**")
    st.caption("Geografisk visualisering")
    
    st.markdown("**📋 Komplett Dataöversikt**")
    st.caption("All tillgänglig data")

with col3:
    st.markdown("**🔍 Kommunjämförelser**")
    st.caption("Jämför med andra kommuner")
    
    st.markdown("**⚙️ Administration**")
    st.caption("Inställningar och API-status")

# Footer med viktig info
st.markdown("---")
st.caption("💡 Tips: Använd sidomenyn till vänster för att navigera mellan olika vyer")
