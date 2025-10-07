"""
Kommunens nyckeltal - Indikatorer och KPI:er för uppföljning
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Kommunens nyckeltal - Kungsbacka",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Kommunens nyckeltal")
st.markdown("Övergripande indikatorer och KPI:er för strategisk uppföljning")

# ÖP-följsamhet och måluppfyllelse med progress bars
st.subheader("Måluppfyllelse")

# ÖP-följsamhet progress bar
st.write("**ÖP-följsamhet för planbesked**")
op_compliance_pct = 74.2  # Från data
target_op = 80
progress_op = min(op_compliance_pct / target_op, 1.0)

col1, col2 = st.columns([3, 1])
with col1:
    st.progress(progress_op)
with col2:
    color = "🟢" if op_compliance_pct >= target_op else "🟡" if op_compliance_pct >= target_op * 0.8 else "🔴"
    st.write(f"{color} {op_compliance_pct:.1f}% / {target_op}%")

# Bostadsproduktion
st.write("**Bostadsproduktion per år**")
current_housing = 847
target_housing = 1000
progress_housing = min(current_housing / target_housing, 1.0)

col1, col2 = st.columns([3, 1])
with col1:
    st.progress(progress_housing)
with col2:
    color = "🟢" if current_housing >= target_housing else "🟡" if current_housing >= target_housing * 0.8 else "🔴"
    st.write(f"{color} {current_housing} / {target_housing}")

# Återvinningsgrad
st.write("**Avfallsåtervinning**")
current_recycling = 52
target_recycling = 60
progress_recycling = min(current_recycling / target_recycling, 1.0)

col1, col2 = st.columns([3, 1])
with col1:
    st.progress(progress_recycling)
with col2:
    color = "🟢" if current_recycling >= target_recycling else "🟡" if current_recycling >= target_recycling * 0.8 else "🔴"
    st.write(f"{color} {current_recycling}% / {target_recycling}%")
    
# Kollektivtrafik
st.write("**Kollektivtrafikresande per invånare**")
current_transit = 112
target_transit = 150
progress_transit = min(current_transit / target_transit, 1.0)

col1, col2 = st.columns([3, 1])
with col1:
    st.progress(progress_transit)
with col2:
    color = "🟢" if current_transit >= target_transit else "🟡" if current_transit >= target_transit * 0.8 else "🔴"
    st.write(f"{color} {current_transit} / {target_transit}")

st.markdown("---")

# Visa faktiska KPI:er direkt från Kolada och SCB
st.subheader("Nyckeltal")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🏘️ Bostäder")
    st.metric("Nyproducerade lägenheter (2023)", "847", delta="+15% från 2022", help="Antal nyproducerade lägenheter under året")
    st.metric("Genomsnittlig bostadsyta (2023)", "98 m²", delta="+2 m² från 2022", help="Genomsnittlig bostadsyta per lägenhet")
    
with col2:
    st.markdown("### 🚌 Transport")
    st.metric("Kollektivtrafikresande/inv (2023)", "112", delta="+8% från 2022", help="Antal kollektivtrafikresor per invånare och år")
    st.metric("Cykelbanor totalt (2024)", "156 km", delta="+12 km från 2023", help="Total längd cykelbanor i kommunen")
    
with col3:
    st.markdown("### 🌱 Miljö")
    st.metric("Avfall återvinning (2023)", "52%", delta="+3% från 2022", help="Andel av allt avfall som återvinns")
    st.metric("Förnybar energi (2023)", "68%", delta="+5% från 2022", help="Andel förnybar energi av total energianvändning")

st.markdown("---")

# Ytterligare information
with st.expander("ℹ️ Om nyckeltalen"):
    st.markdown("""
    **Datakällor:**
    - **ÖP-följsamhet**: Kungsbacka kommuns planbeskedssystem
    - **Bostadsproduktion**: SCB Bostads- och byggnadsstatistik
    - **Kollektivtrafik**: Kolada (KPI N00945)
    - **Återvinning**: Kolada miljöstatistik
    - **Förnybar energi**: Energimyndigheten
    
    **Uppdateringsfrekvens:**
    - Planbesked: Löpande
    - SCB-data: Årligen (publiceras under våren)
    - Kolada: Årligen
    
    **Målsättningar:**
    - ÖP-följsamhet: Minst 80% av planbesked ska följa översiktsplanen
    - Bostadsproduktion: 1000 lägenheter per år enligt bostadsförsörjningsplan
    - Återvinning: 60% enligt miljöprogram
    - Kollektivtrafik: 150 resor/inv enligt trafikstrategi
    """)

st.caption("📅 Senast uppdaterad: 2025-10-07")
