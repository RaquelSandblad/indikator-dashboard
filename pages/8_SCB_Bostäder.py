"""
SCB Bostäder - Bostadsbestånd och nyproduktion från SCB
"""

import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.scb_connector import SCBConnector

st.set_page_config(page_title="SCB Bostäder - Kungsbacka", page_icon="🏘️", layout="wide")

st.title("🏘️ Bostadsdata från SCB")
st.markdown("*Bostadsbestånd och nyproduktion från Statistiska Centralbyrån*")

scb = SCBConnector()

# API-status
try:
    test = scb.get_housing_stock(years=["2024"])
    st.success("✅ SCB Bostadsdata ansluten")
except Exception as e:
    st.error(f"❌ Fel: {e}")

st.markdown("---")

# Hämta data
with st.spinner("Hämtar bostadsdata..."):
    housing_stock = scb.get_housing_stock()
    new_const = scb.get_new_construction()

# HUVUDMETRICS
st.subheader("📊 Bostadsbestånd 2024")

if not housing_stock.empty:
    latest = housing_stock[housing_stock['År'] == housing_stock['År'].max()]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total = latest['Antal'].sum()
        st.metric("🏘️ Totalt antal lägenheter", f"{total:,}".replace(",", " "))
    
    with col2:
        smahus = latest[latest['Hustyp'] == 'Småhus']['Antal'].sum()
        pct_smahus = (smahus / total * 100) if total > 0 else 0
        st.metric("🏡 Småhus", f"{smahus:,}".replace(",", " "), f"{pct_smahus:.1f}%")
    
    with col3:
        flerbo = latest[latest['Hustyp'] == 'Flerbostadshus']['Antal'].sum()
        pct_flerbo = (flerbo / total * 100) if total > 0 else 0
        st.metric("🏢 Flerbostadshus", f"{flerbo:,}".replace(",", " "), f"{pct_flerbo:.1f}%")

st.markdown("---")

# BOSTADSBESTÅND UTVECKLING
st.subheader("📈 Bostadsbestånd över tid (5 år)")

if not housing_stock.empty:
    fig = px.line(housing_stock, x='År', y='Antal', color='Hustyp', 
                  markers=True,
                  title='Utveckling av bostadsbeståndet',
                  labels={'Antal': 'Antal lägenheter', 'År': 'År'})
    fig.update_layout(hovermode='x unified', height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Stapeldiagram fördelning per år
    fig2 = px.bar(housing_stock, x='År', y='Antal', color='Hustyp',
                  title='Fördelning per år',
                  labels={'Antal': 'Antal lägenheter', 'År': 'År'},
                  barmode='stack')
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# NYBYGGNATION
st.subheader("🏗️ Nybyggnation (Färdigställda lägenheter)")

if not new_const.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        latest_new = new_const[new_const['År'] == new_const['År'].max()]
        total_new = latest_new['Antal'].sum()
        st.metric("🎉 Färdigställda 2024", f"{total_new:,}".replace(",", " "))
    
    with col2:
        # Genomsnitt senaste 5 åren
        avg_new = new_const.groupby('År')['Antal'].sum().mean()
        st.metric("📊 Snitt senaste 5 åren", f"{avg_new:.0f}")
    
    # Nybyggnationstrend
    yearly_new = new_const.groupby('År')['Antal'].sum().reset_index()
    fig = px.bar(yearly_new, x='År', y='Antal',
                 title='Färdigställda lägenheter per år',
                 labels={'Antal': 'Antal lägenheter', 'År': 'År'},
                 color='Antal',
                 color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)
    
    # Per hustyp
    fig2 = px.bar(new_const, x='År', y='Antal', color='Hustyp',
                  title='Nybyggnation per hustyp',
                  labels={'Antal': 'Antal lägenheter', 'År': 'År'},
                  barmode='group')
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# JÄMFÖRELSE
st.subheader("📊 Halland-jämförelse")

col1, col2 = st.columns(2)

with col1:
    st.info("""
    **Jämför med andra kommuner:**
    - Varberg
    - Halmstad  
    - Laholm
    - Falkenberg
    - Hylte
    """)

with col2:
    comp_data = scb.compare_municipalities("befolkning", year="2024")
    if not comp_data.empty:
        st.dataframe(comp_data, use_container_width=True, hide_index=True)

# RÅDATA
with st.expander("📋 Rådata"):
    st.markdown("### Bostadsbestånd")
    st.dataframe(housing_stock, use_container_width=True)
    
    st.markdown("### Nybyggnation")
    st.dataframe(new_const, use_container_width=True)
    
    st.caption(f"Källa: SCB, hämtad {datetime.now().strftime('%Y-%m-%d %H:%M')}")
