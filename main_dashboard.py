#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Kungsbacka Dashboard - Ren version med SCB 2024 data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Lägg till aktuell katalog till Python-sökvägen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importera lokala moduler
from config import KOMMUN_KOD, ORTER
from scb_api_clean import SCBDataSource

# Streamlit konfiguration
st.set_page_config(
    page_title="Kungsbacka Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Huvudfunktion för Streamlit-appen"""
    
    # Sidhuvud
    st.title("🏛️ Kungsbacka Kommun Dashboard")
    st.markdown("### Aktuell data för planering och utveckling")
    
    # Sidebar för navigation
    with st.sidebar:
        st.header("📊 Navigation")
        page = st.selectbox(
            "Välj vy:",
            ["🏠 Översikt", "📈 Befolkningsdata", "📊 Planbesked - Antura", "ℹ️ Om systemet"]
        )
    
    # Skapa SCB-instans
    scb = SCBDataSource()
    
    if page == "🏠 Översikt":
        show_overview(scb)
    elif page == "📈 Befolkningsdata":
        show_population_data(scb)
    elif page == "📊 Planbesked - Antura":
        show_antura_section()
    elif page == "ℹ️ Om systemet":
        show_about()

def show_overview(scb):
    """Visar översiktsvy med nyckeltal"""
    
    st.header("📊 Översikt Kungsbacka kommun")
    
    # Hämta aktuella data
    with st.spinner("Hämtar senaste data från SCB..."):
        pop_data = scb.fetch_population_data()
    
    if not pop_data.empty:
        # Beräkna nyckeltal
        latest_year = pop_data["År"].max()
        latest_data = pop_data[pop_data["År"] == latest_year]
        total_population = latest_data["Antal"].sum()
        men = latest_data[latest_data["Kön"] == "Män"]["Antal"].sum()
        women = latest_data[latest_data["Kön"] == "Kvinnor"]["Antal"].sum()
        
        # Visa nyckeltal
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total befolkning",
                value=f"{total_population:,}",
                help=f"Senaste data från SCB ({latest_year})"
            )
        
        with col2:
            st.metric(
                label="Män",
                value=f"{men:,}",
                delta=f"{men - women:+,}"
            )
        
        with col3:
            st.metric(
                label="Kvinnor", 
                value=f"{women:,}",
                delta=f"{women - men:+,}"
            )
        
        with col4:
            if len(pop_data["År"].unique()) > 1:
                prev_year = sorted(pop_data["År"].unique())[-2]
                prev_total = pop_data[pop_data["År"] == prev_year]["Antal"].sum()
                growth = total_population - prev_total
                st.metric(
                    label="Årlig förändring",
                    value=f"{growth:+,}",
                    delta=f"{(growth/prev_total)*100:.1f}%"
                )
        
        # Befolkningsutveckling över tid
        st.subheader("📈 Befolkningsutveckling")
        
        yearly_data = pop_data.groupby(["År", "Kön"])["Antal"].sum().reset_index()
        
        fig = px.line(
            yearly_data,
            x="År",
            y="Antal", 
            color="Kön",
            title="Befolkningsutveckling Kungsbacka kommun",
            markers=True
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Visa rådata
        with st.expander("📋 Visa rådata från SCB"):
            st.dataframe(pop_data, use_container_width=True)
            st.caption(f"Källa: SCB, hämtad {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    else:
        st.warning("⚠️ Kunde inte hämta befolkningsdata från SCB")
        st.info("Kontrollera internetanslutning eller försök igen senare")

def show_population_data(scb):
    """Detaljerad befolkningsanalys"""
    
    st.header("📈 Detaljerad befolkningsanalys")
    
    tab1, tab2 = st.tabs(["📊 Befolkningsdata", "🔄 Åldersfördelning"])
    
    with tab1:
        st.subheader("Befolkningsstatistik")
        
        with st.spinner("Hämtar befolkningsdata..."):
            pop_data = scb.fetch_population_data()
        
        if not pop_data.empty:
            # Interaktiv tabell
            st.dataframe(
                pop_data.pivot(index=["År", "Region"], columns="Kön", values="Antal").reset_index(),
                use_container_width=True
            )
        else:
            st.error("Kunde inte hämta befolkningsdata")
    
    with tab2:
        st.subheader("Åldersfördelning")
        
        with st.spinner("Hämtar åldersdata..."):
            age_data = scb.fetch_age_distribution()
        
        if not age_data.empty:
            # Skapa ålderspyramid
            fig = go.Figure()
            
            men_data = age_data[age_data["Kön"] == "Män"]
            women_data = age_data[age_data["Kön"] == "Kvinnor"]
            
            # Män (negativa värden för vänster sida)
            fig.add_trace(go.Bar(
                y=men_data["Ålder"],
                x=-men_data["Antal"],
                name="Män",
                orientation='h',
                marker_color='lightblue'
            ))
            
            # Kvinnor (positiva värden för höger sida)
            fig.add_trace(go.Bar(
                y=women_data["Ålder"],
                x=women_data["Antal"], 
                name="Kvinnor",
                orientation='h',
                marker_color='pink'
            ))
            
            fig.update_layout(
                title="Ålderspyramid Kungsbacka kommun",
                xaxis_title="Antal invånare",
                yaxis_title="Åldersgrupp",
                barmode='relative',
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Visa åldersdata
            with st.expander("📋 Visa åldersdata"):
                st.dataframe(age_data, use_container_width=True)
        
        else:
            st.warning("⚠️ Åldersdata inte tillgänglig just nu")

def show_antura_section():
    """Visar Antura planbesked-sektionen"""
    
    st.header("📊 Planbesked i Antura")
    st.markdown("---")

    # Antura-tabell i expander (rullgardin)
    with st.expander("Planbesked i Antura – vad vi vill kunna få ut", expanded=False):
        st.markdown("""
        <div style='font-size:1em; color:#888; margin-bottom:1em;'>
        (Denna sektion kommer att uppdateras automatiskt när Antura-integration är på plats. Rubrikerna nedan är statiska, data kommer från Antura.)
        </div>
        <div style='display:flex; gap:32px;'>
            <div style='flex:1;'>
                <table style='width:100%; border-collapse:collapse; border:1px solid #ccc;'>
                    <tr>
                        <td rowspan='3' style='background:#c19a9a; color:black; font-weight:bold; padding:10px; font-size:0.9em; writing-mode:vertical-rl; text-orientation:mixed; width:15%; text-align:center;'>BOSTÄDER</td>
                        <td rowspan='1' style='background:#c19a9a; color:black; font-weight:bold; padding:8px; font-size:0.85em; writing-mode:vertical-rl; text-orientation:mixed; width:15%; text-align:center;'>Kungsbacka stad</td>
                        <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.75em; width:50%;'>
                                Gåsevadholm S:1<br>
                                <u>Bäratorr</u> 2:1 och 1:12 samt Kungsbacka 5:1<br>
                                Hammerö 7:3<br>
                                Hammerö 13:7 m.fl.<br>
                                Lärkan 14<br>
                                Ysby 3:4 m.fl.<br>
                                Fors 1:387<br>
                                Aranäs 10 och 15<br>
                                Store Lyckor 1 och 2
                        </td>
                        <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center; width:10%;'></td>
                        <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center; width:10%;'><strong>Xx st</strong></td>
                    </tr>
                    <tr>
                        <td rowspan='1' style='background:#c19a9a; color:black; font-weight:bold; padding:8px; font-size:0.85em; writing-mode:vertical-rl; text-orientation:mixed; text-align:center;'>Åsa</td>
                        <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.75em;'>
                                Åsa 5:197 och 5:70<br>
                                Åsa 5:161 och Åsa 5:101<br>
                                Åsa 5:96<br>
                                <u>Kläppa</u> 1:4 daterat 2023-10-28<br>
                                Åsa 4:146 och Åsa 4:152<br>
                                Åsa 5:153 och 5:89<br>
                                Åsa 3:14 och Åsa 5:219
                        </td>
                        <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                        <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                    </tr>
                    <tr>
                        <td rowspan='1' style='background:#c19a9a; color:black; font-weight:bold; padding:8px; font-size:0.85em; writing-mode:vertical-rl; text-orientation:mixed; text-align:center;'>Anneberg</td>
                        <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.75em;'>
                                Älafors 4:12<br>
                                Lerberg 16:40, 3:9 och 3:11<br>
                                Älafors 4:12 (Skifte 23)
                        </td>
                        <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                        <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                    </tr>
                </table>
            </div>
            <div style='flex:1;'>
                <table style='width:100%; border-collapse:collapse; border:1px solid #ccc;'>
                    <tr>
                        <td rowspan='2' style='background:#c19a9a; color:black; font-weight:bold; padding:10px; font-size:0.9em; writing-mode:vertical-rl; text-orientation:mixed; width:15%; text-align:center;'>BOSTÄDER</td>
                        <td rowspan='1' style='background:#c19a9a; color:black; font-weight:bold; padding:8px; font-size:0.85em; writing-mode:vertical-rl; text-orientation:mixed; width:15%; text-align:center;'>Övriga orter</td>
                        <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.75em; width:50%;'>
                                del av <u>Bångsbå</u> 4:1<br>
                                Lyngås 3:3<br>
                                Bäcken 1:31 m.fl.<br>
                                Vallda 5:11<br>
                                Frillesås-Rya 2:11<br>
                                Må 2:210<br>
                                Frillesås-rya 2:3 och <u>Lurendal</u> 1:3<br>
                                Kyvík 5:380
                        </td>
                        <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center; width:10%;'>Väg 158, C<br>Väg 158, utvidgad<br>ort</td>
                        <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center; width:10%;'><strong>Xx st</strong></td>
                    </tr>
                    <tr>
                        <td rowspan='1' style='background:#c19a9a; color:black; font-weight:bold; padding:8px; font-size:0.85em; writing-mode:vertical-rl; text-orientation:mixed; text-align:center;'>Utanför ort</td>
                        <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.75em;'>
                                Vallda 20:3, <u>Bröndom</u> 1:2 och del av Vallda 20:59*<br>
                                Bukärr 1:5*<br>
                                Gräppås 2:13<br>
                                Hede 1:53,
                        </td>
                        <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                        <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                    </tr>
                    <tr>
                        <td rowspan='4' style='background:#e6b3ff; color:black; font-weight:bold; padding:10px; font-size:0.75em; writing-mode:vertical-rl; text-orientation:mixed; text-align:center;'>MARK FÖR NÄRINGSLIV</td>
                        <td rowspan='1' style='background:#e6b3ff; color:black; font-weight:bold; padding:8px; font-size:0.75em; writing-mode:vertical-rl; text-orientation:mixed; text-align:center;'>Åsa stad</td>
                        <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.75em;'>
                                Åskatorp 21:1 mfl<br>
                                Varla 2:423<br>
                                Varla 2:412<br>
                                Hede 3:12 skifte 1<br>
                                Vallda 23:2<br>
                                Vallda 5:11*
                        </td>
                        <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                        <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.8em; text-align:center;'><strong>Xx ha</strong></td>
                    </tr>
                    <tr>
                        <td rowspan='1' style='background:#d9b3ff; color:black; font-weight:bold; padding:8px; font-size:0.75em; writing-mode:vertical-rl; text-orientation:mixed; text-align:center;'>Fjärås stn</td>
                        <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.75em;'>Väg 158,<br>trafikintensivt</td>
                        <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                        <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                    </tr>
                    <tr>
                        <td rowspan='1' style='background:#d9b3ff; color:black; font-weight:bold; padding:8px; font-size:0.75em; writing-mode:vertical-rl; text-orientation:mixed; text-align:center;'>KBA stad</td>
                        <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.75em;'></td>
                        <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                        <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                    </tr>
                    <tr>
                        <td rowspan='1' style='background:#d9b3ff; color:black; font-weight:bold; padding:8px; font-size:0.75em; writing-mode:vertical-rl; text-orientation:mixed; text-align:center;'>Vallda</td>
                        <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.75em;'></td>
                        <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                        <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                    </tr>
                </table>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_about():
    """Information om systemet"""
    
    st.header("ℹ️ Om systemet")
    
    st.markdown("""
    ### 🏛️ Kungsbacka Dashboard
    
    Detta system visar aktuell data för planering och utveckling i Kungsbacka kommun.
    
    #### 📊 Datakällor:
    - **SCB (Statistiska Centralbyrån)** - Befolkningsdata 2024
    - **Antura** - Planbesked (kommer)
    
    #### 🔄 Senast uppdaterat:
    - SCB-data: Automatisk hämtning
    - Systemversion: v2.0 (September 2025)
    
    #### 🛠️ Teknisk information:
    - Byggd med Streamlit och Python
    - Använder SCB:s öppna API
    - Realtidsuppdatering av befolkningsdata
    
    #### 📞 Kontakt:
    - Kungsbacka kommun IT-avdelning
    - Support via kommun.se
    """)
    
    # Visa systemstatus
    st.subheader("🔧 Systemstatus")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Testa SCB-anslutning
        scb = SCBDataSource()
        try:
            test_data = scb.fetch_population_data()
            if not test_data.empty:
                st.success("✅ SCB API - Fungerande")
                st.caption(f"Senaste data: {test_data['År'].max()}")
            else:
                st.warning("⚠️ SCB API - Begränsad funktion")
        except Exception as e:
            st.error(f"❌ SCB API - Ej tillgänglig")
    
    with col2:
        st.info("ℹ️ Antura API - Under utveckling")
        st.caption("Planerat: Q4 2025")

if __name__ == "__main__":
    main()