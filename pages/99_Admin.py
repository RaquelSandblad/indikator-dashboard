"""
Administration - Systeminställningar, API-status och systeminformation
"""

import streamlit as st
import sys
import os
import requests
from datetime import datetime

# Lägg till root directory till path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import KOMMUN_KOD, ORTER
from data_sources import SCBDataSource

st.set_page_config(
    page_title="Admin - Kungsbacka",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Administration & Systeminformation")
st.markdown("Systemkonfiguration, datakällstatus och information")

# OM SYSTEMET
st.subheader("ℹ️ Om systemet")

st.markdown("""
### 🏛️ Kungsbacka Dashboard

Detta system visar aktuell data för planering och utveckling i Kungsbacka kommun.

#### 📊 Datakällor:
- **SCB (Statistiska Centralbyrån)** - Befolkningsdata 2024
- **Antura** - Planbesked (under utveckling)
- **Kolada** - Kommun- och landstingsdatabasen (planerat)

#### 🔄 Senast uppdaterat:
- SCB-data: Automatisk hämtning
- Systemversion: v2.0 (Oktober 2025)

#### 🛠️ Teknisk information:
- Byggd med Streamlit och Python
- Använder SCB:s öppna API
- Realtidsuppdatering av befolkningsdata
""")

st.markdown("---")

# API-STATUS
st.subheader("📡 API-status")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### SCB API")
    try:
        scb = SCBDataSource()
        pop_data = scb.fetch_population_data()
        if not pop_data.empty:
            st.success("✅ SCB API fungerar")
            latest_year = pop_data["År"].max()
            st.metric("Senaste tillgängliga data", f"År {latest_year}")
            st.metric("Antal datapunkter", len(pop_data))
        else:
            st.warning("⚠️ SCB API svarar men returnerar ingen data")
    except Exception as e:
        st.error("❌ SCB API ej tillgängligt")
        with st.expander("Feldetaljer"):
            st.code(str(e))

with col2:
    st.markdown("### Kolada API")
    try:
        response = requests.get("http://api.kolada.se/v2/kpi", timeout=10)
        if response.status_code == 200:
            kpis = response.json().get('values', [])
            st.success("✅ Kolada API fungerar")
            st.metric("Antal KPI:er tillgängliga", len(kpis))
        else:
            st.error(f"❌ Kolada API: HTTP {response.status_code}")
    except Exception as e:
        st.warning("⚠️ Kolada API ej tillgängligt just nu")
        with st.expander("Feldetaljer"):
            st.code(str(e))

st.markdown("---")

# ANTURA STATUS
st.subheader("🏢 Antura-integration")

col1, col2 = st.columns(2)

with col1:
    st.info("📋 Antura planbesked")
    st.write("**Status:** Under utveckling")
    st.write("**Planerat:** Q4 2025")
    st.write("**Funktion:** Automatisk hämtning av planbesked och planer")

with col2:
    st.info("📊 Planerad data från Antura")
    st.write("- Planbesked (positiva/negativa)")
    st.write("- Detaljplaner")
    st.write("- Program")
    st.write("- Geografisk information")

st.markdown("---")

# SYSTEMINFORMATION
st.subheader("🖥️ Systeminformation")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Konfiguration")
    st.write(f"**Kommun kod:** {KOMMUN_KOD}")
    st.write(f"**Antal orter:** {len(ORTER)}")
    st.write(f"**Python version:** {sys.version.split()[0]}")
    st.write(f"**Systemtid:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with col2:
    st.markdown("### Orter i systemet")
    orter_list = list(ORTER.keys())
    for ort in orter_list:
        st.write(f"- {ort} (kod: {ORTER[ort]})")

st.markdown("---")

# FILSTATUS
st.subheader("📁 Filstatus")

required_files = [
    "config.py",
    "data_sources.py",
    "utils.py",
    "SCB_Dataservice.py",
    "Home.py"
]

file_status = []
for file in required_files:
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), file)
    exists = os.path.exists(file_path)
    status = "✅ OK" if exists else "❌ Saknas"
    
    file_status.append({
        "Fil": file,
        "Status": status
    })

import pandas as pd
df_files = pd.DataFrame(file_status)
st.dataframe(df_files, use_container_width=True)

st.markdown("---")

# CACHE INFORMATION
st.subheader("💾 Cache-information")

cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")

if os.path.exists(cache_dir):
    cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
    st.success(f"✅ Cache-katalog finns med {len(cache_files)} filer")
    
    if cache_files:
        with st.expander("Visa cache-filer"):
            for i, cache_file in enumerate(cache_files[:10], 1):
                st.write(f"{i}. {cache_file}")
            if len(cache_files) > 10:
                st.write(f"... och {len(cache_files) - 10} filer till")
else:
    st.warning("⚠️ Ingen cache-katalog hittad")

st.caption("System-administration och teknisk information | Kungsbacka kommun")
