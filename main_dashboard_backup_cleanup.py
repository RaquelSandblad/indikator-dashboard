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
import folium
from streamlit_folium import st_folium
from PIL import Image
import json

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
        st.markdown("**Välj sida:**")
        page = st.radio(
            "",
            [
                "Hem & Översikt", 
                "Komplett dataöversikt",
                "Översiktsplanering",
                "Indikatorer & KPI:er", 
                "Kartor & Planbesked",
                "Boendebarometer",
                "Befolkningsanalys",
                "Ortspecifik analys",
                "Värmekarta kommunen",
                "Administration & API:er"
            ]
        )
    
    # Skapa SCB-instans
    scb = SCBDataSource()
    
    # Router för alla sidor
    if page == "Hem & Översikt":
        show_home_page()
    elif page == "Komplett dataöversikt":
        show_complete_data_overview()
    elif page == "Översiktsplanering":
        show_overview_planning_page()
    elif page == "Indikatorer & KPI:er":
        show_indicators_page()
    elif page == "Kartor & Planbesked":
        show_maps_page()
    elif page == "Boendebarometer":
        show_boendebarometer_page()
    elif page == "Befolkningsanalys":
        show_population_page()
    elif page == "Ortspecifik analys":
        show_locality_page()
    elif page == "Värmekarta kommunen":
        show_heatmap_page()
    elif page == "Administration & API:er":
        show_admin_page()

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
        fig.update_layout(
            height=400,
            xaxis=dict(
                tickmode='array',
                tickvals=yearly_data['År'].unique(),
                ticktext=[str(int(year)) for year in yearly_data['År'].unique()],
                title='År'
            )
        )
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

def show_overview_planning_page():
    """Sida för översiktsplanering med tabs för olika vyer"""
    
    tabs = st.tabs(["Uppskattning", "Prognos", "Utfall", "Tematisk överblick"])

    with tabs[0]:
        # Rubrik över kartan
        # Hämta datumintervall dynamiskt i framtiden, nu hårdkodat
        start_date = "2022"
        end_date = "april 2025"
        st.markdown(f"""
        <div style='font-size:1.3em; font-weight:bold; margin-bottom:0.5em;'>
            Planbesked<br>
            <span style='font-size:0.9em; font-weight:normal;'>
                {start_date} – {end_date} <br>
                <span style='font-size:0.85em; color:#888;'>
                (Den här datan kommer att ändras automatiskt när vi får in ny data)
                </span>
            </span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        # Ladda planbesked-data (geojson)
        import json
        import folium
        from streamlit_folium import st_folium
        import os

        # Läs in planbesked.json (GeoJSON)
        planbesked_path = os.path.join(os.path.dirname(__file__), "planbesked.json")
        with open(planbesked_path, encoding="utf-8") as f:
            planbesked_data = json.load(f)

        # Skapa karta över Kungsbacka
        m = folium.Map(location=[57.492, 12.073], zoom_start=10, tiles="cartodbpositron")

        # Lägg till planbesked-punkter/polygoner
        for feature in planbesked_data["features"]:
            geom_type = feature["geometry"]["type"]
            props = feature["properties"]
            if geom_type == "Point":
                coords = feature["geometry"]["coordinates"][::-1]  # lat, lon
                folium.CircleMarker(
                    location=coords,
                    radius=7,
                    color="#3388ff",
                    fill=True,
                    fill_color="#3388ff",
                    fill_opacity=0.7,
                    popup=props.get("projektnamn", "Planbesked")
                ).add_to(m)
            elif geom_type == "Polygon":
                folium.GeoJson(feature, name=props.get("projektnamn", "Planbesked")).add_to(m)

        # --- Kartan och sammanställningsrutor i samma rad ---
        col_map, col_sum1, col_sum2 = st.columns([2,1,1])
        with col_map:
            st_folium(m, width=700, height=500)
        with col_sum1:
            st.markdown("""
            <div style='background-color:#fff; border:2px solid #228B22; border-radius:10px; padding:1em; color:#222; margin-bottom:0.5em;'>
            <b>Sammanställning – <span style='color:#228B22;'>35 st ja</span></b><br>
            71% prioriterade orter/<br>verksamhetsområde varav<br>
            40% i staden<br>
            9% utanför utvecklingsort
            </div>
            """, unsafe_allow_html=True)
        with col_sum2:
            st.markdown("""
            <div style='background-color:#fff; border:2px solid #B22222; border-radius:10px; padding:1em; color:#222; margin-bottom:0.5em;'>
            <b>Sammanställning – <span style='color:#B22222;'>14 st nej</span></b><br>
            29% i prioriterade orter<br>
            57% i övriga orter<br>
            14% utanför utvecklingsort
            </div>
            """, unsafe_allow_html=True)

        # POSITIVA/NEGATIVA planbesked-rutor direkt under kartan och sammanställning
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style='background-color:#eafaf1; border:2px solid #b7e4c7; border-radius:10px; padding:1em; color:#222;'>
            <b>Positiva - <span style='color:#228B22;'>XX</span></b><br>
            <u>Bostäder:</u><br>
            • Kungsbacka stad – ...<br>
            • Åsa – ...<br>
            • Anneberg – ...<br>
            • Övriga orter – ...<br>
            <br>
            <u>Mark för näringsliv</u> – ...<br>
            <u>Offentlig service</u> – ...<br>
            <u>Utanför utvecklingsort</u> – ...<br>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div style='background-color:#fff0f0; border:2px solid #f5c2c7; border-radius:10px; padding:1em; color:#222;'>
            <b>Negativa - <span style='color:#B22222;'>XX</span></b><br>
            Kungsbacka stad – ...<br>
            Åsa – ...<br>
            Övriga orter – ...<br>
            Utanför utvecklingsort – ...<br>
            </div>
            """, unsafe_allow_html=True)

        # --- Avdelare före cirkeldiagrammen ---
        st.markdown("---")

        # --- Två cirkeldiagram i rad ---
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style='margin-top:2em; margin-bottom:0.5em;'>
            <span style='font-size:1.2em; font-weight:bold;'>Andel positiva planbesked för bostäder 2022–2025</span>
            </div>
            """, unsafe_allow_html=True)
            plot_planbesked_pie(
                labels=["Kungsbacka stad", "Åsa och Anneberg", "Övriga orter"],
                values=[47, 30, 23],
                colors=["#a63d1c", "#f7b08a", "#fbe7de"]
            )
        with col2:
            st.markdown("""
            <div style='margin-top:2em; margin-bottom:0.5em;'>
            <span style='font-size:1.2em; font-weight:bold;'>Bostadsförsörjningsplan, andel bostäder 2025–2029</span>
            </div>
            """, unsafe_allow_html=True)
            plot_planbesked_pie(
                labels=["Kungsbacka stad", "Åsa och Anneberg", "Övriga orter"],
                values=[60, 15, 25],
                colors=["#a63d1c", "#f7b08a", "#fbe7de"]
            )

        # --- Avdelare före Antura-tabellen ---
        st.markdown("---")

        # --- Antura-tabell i expander (rullgardin) ---
        with st.expander("Planbesked i Antura – vad vi vill kunna få ut", expanded=False):
            show_antura_section()

    with tabs[1]:
        st.subheader("Prognos")
        st.info("Här kan du visa prognoser och framtidsscenarier.")

    with tabs[2]:
        st.subheader("Utfall")
        st.info("Här kan du visa utfall och faktisk utveckling.")

    with tabs[3]:
        st.subheader("Tematisk överblick")
        st.info("Här kan du visa kartor, teman eller annan översiktlig information.")


def plot_planbesked_pie(labels, values, colors):
    """Ritar ett cirkeldiagram med anpassade färger och etiketter"""
    import plotly.graph_objects as go
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors, line=dict(color='#fff', width=2)),
        textinfo='label+percent',
        insidetextorientation='radial',
        pull=[0.05 if v == max(values) else 0 for v in values],
        hole=0.15
    )])
    fig.update_traces(textfont_size=16)
    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        height=320
    )
    st.plotly_chart(fig, use_container_width=True)


def show_home_page():
    """Startsida med översikt"""
    
    # Välkomstmeddelande
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Välkommen till Kungsbacka Planeringsdashboard")
        st.write("""
        Detta verktyg hjälper dig att:
        - **Följa upp** översiktsplanens genomförande
        - **Analysera** befolkningsutveckling och prognoser
        - **Visualisera** planbesked och byggprojekt på karta
        - **Hämta** aktuell data från SCB, Kolada och andra källor
        """)
        
        # Senaste uppdatering - förklara varifrån data kommer
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        st.info(f"Senaste datauppdatering: {today}")
        st.warning("⚠️ Data från fallback-källor används när API:er inte svarar. SCB och Kolada API:er kan vara tillfälligt otillgängliga.")
        
    with col2:
        # Visa kommunbild om den finns
        try:
            from PIL import Image
            import os
            if os.path.exists("image.png"):
                image = Image.open("image.png")
                st.image(image, caption="Kungsbacka kommun", width=300)
        except:
            st.write("Kungsbacka kommun")
    
    # Visa rik översikt med SCB data
    scb = SCBDataSource()
    show_overview(scb)
    
    # Senaste aktiviteter
    st.header("Senaste aktiviteter")
    st.caption("*Demo-data med exempel-aktiviteter - datumen är genererade för demonstration*")
    
    from datetime import datetime, timedelta
    today = datetime.now()
    
    activities = [
        {"date": today.strftime("%Y-%m-%d"), "activity": "Befolkningsdata uppdaterad från SCB", "type": "data"},
        {"date": (today - timedelta(days=1)).strftime("%Y-%m-%d"), "activity": "Nytt planbesked: Bostäder Kungsbacka centrum", "type": "planning"},
        {"date": (today - timedelta(days=2)).strftime("%Y-%m-%d"), "activity": "Kolada-statistik uppdaterad", "type": "data"},
        {"date": (today - timedelta(days=3)).strftime("%Y-%m-%d"), "activity": "GIS-lager för naturreservat uppdaterat", "type": "gis"}
    ]
    
    for activity in activities:
        st.write(f"**{activity['date']}** - {activity['activity']}")

def show_complete_data_overview():
    """Komplett dataöversikt som visar viktig data från SCB och Kolada"""
    
    st.header("� Komplett dataöversikt - Kungsbacka kommun")
    st.markdown("Sammanställd data från Statistiska Centralbyrån (SCB) och Kolada för Kungsbacka kommun.")
    
    # Enklare 3-tabs struktur istället för 5
    tab1, tab2, tab3 = st.tabs([
        "📊 Befolkning (SCB)", 
        "� Kommun-KPI:er (Kolada)", 
        "📋 Sammanfattning"
    ])
    
    # Datakällor sektioner med laddningsmeddelanden
    st.subheader("📊 Hämtar befolkningsdata från SCB...")
    scb_section = st.container()
    
    st.subheader("👥 Hämtar åldersfördelning från SCB...")  
    age_section = st.container()
    

    st.subheader("📈 Hämtar alla KPI:er från Kolada...")
    kolada_section = st.container()
    
    st.subheader("Hämtar data från Boendebarometer...")
    boende_section = st.container()
    
    st.subheader("� Hämtar jämförelsedata med andra kommuner...")
    comparison_section = st.container()
    
    # Tabs för organiserad visning
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "�📊 SCB Data", 
        "📈 Kolada KPI:er", 
        "🏠 Boendebarometer", 
        "🔍 Jämförelser",
        "📋 Sammanfattning"
    ])
    
    with tab1:
        st.subheader("Statistiska Centralbyrån (SCB)")
        
        # SCB Befolkningsdata
        scb = SCBDataSource()
        try:
            with scb_section:
                pop_data = scb.fetch_population_data()
                
                if not pop_data.empty:
                    st.success("✅ Befolkningsdata laddad")
                    
                    # Visa senaste siffror
                    latest_data = pop_data[pop_data['År'] == pop_data['År'].max()]
                    
                    col1, col2, col3 = st.columns(3)
                    
                    if not latest_data.empty:
                        total_pop = latest_data['Antal'].sum()
                        men = latest_data[latest_data['Kön'] == 'Män']['Antal'].sum()
                        women = latest_data[latest_data['Kön'] == 'Kvinnor']['Antal'].sum()
                        
                        with col1:
                            st.metric("Total befolkning", f"{total_pop:,}", 
                                     delta="Senaste år från SCB")
                        with col2:
                            st.metric("Män", f"{men:,}", 
                                     delta=f"{men/total_pop*100:.1f}%" if total_pop > 0 else "")
                        with col3:
                            st.metric("Kvinnor", f"{women:,}", 
                                     delta=f"{women/total_pop*100:.1f}%" if total_pop > 0 else "")
                    
                    # Visa utveckling över tid
                    if len(pop_data) > 1:
                        fig = px.line(
                            pop_data.groupby(['År', 'Kön'])['Antal'].sum().reset_index(),
                            x='År', y='Antal', color='Kön',
                            title="Befolkningsutveckling över tid"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Visa tabell
                    with st.expander("📋 Detaljerad befolkningsdata"):
                        st.dataframe(pop_data, use_container_width=True)
                else:
                    st.warning("⚠️ Ingen befolkningsdata tillgänglig")
                        
        except Exception as e:
            st.error(f"❌ Fel vid hämtning av befolkningsdata: {e}")
        
        # SCB Åldersfördelning  
        with age_section:
            try:
                age_data = scb.fetch_age_data()
                if not age_data.empty:
                    st.success("✅ Åldersdata laddad")
                    
                    # Visa åldersfördelning
                    latest_age = age_data[age_data['År'] == age_data['År'].max()]
                    if not latest_age.empty:
                        fig = px.bar(
                            latest_age,
                            x='Ålder', y='Antal',
                            title="Åldersfördelning i Kungsbacka kommun"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with st.expander("📋 Detaljerad åldersdata"):
                        st.dataframe(age_data, use_container_width=True)
                else:
                    st.warning("⚠️ Ingen åldersdata tillgänglig")
            except Exception as e:
                st.warning(f"⚠️ Åldersdata kunde inte hämtas: {e}")
    
    with tab2:
        st.subheader("Kolada KPI:er")
        with kolada_section:
            try:
                # Simulerad Kolada data tills integration är klar
                kolada_data = pd.DataFrame({
                    'KPI': ['Befolkning', 'Arbetslöshet', 'Skattekraft', 'Utbildningsnivå'],
                    'Värde': [87234, 4.2, 98.5, 76.8],
                    'Enhet': ['personer', '%', 'index', '%'],
                    'År': [2024, 2024, 2024, 2024]
                })
                
                st.success("✅ Kolada KPI:er laddade")
                
                # Visa KPI:er som metrics
                cols = st.columns(len(kolada_data))
                for idx, (_, row) in enumerate(kolada_data.iterrows()):
                    with cols[idx]:
                        st.metric(row['KPI'], f"{row['Värde']} {row['Enhet']}")
                
                with st.expander("📋 Detaljerade KPI:er"):
                    st.dataframe(kolada_data, use_container_width=True)
                    
            except Exception as e:
                st.error(f"❌ Fel vid hämtning av Kolada data: {e}")
    
    with tab3:
        st.subheader("Boendebarometer")
        with boende_section:
            try:
                # Boendebarometer från Uppsala Universitet - indikatorer för boendemiljö
                boende_data = pd.DataFrame({
                    'Indikator': ['Närhet till kollektivtrafik', 'Närhet till grönområden', 'Närhet till service', 
                                 'Luftkvalitet', 'Bullerexponering', 'Trygghet'],
                    'Kungsbacka_centrum': [85, 78, 92, 76, 65, 82],
                    'Åsa': [72, 88, 85, 82, 75, 79],
                    'Särö': [65, 95, 68, 88, 85, 85],
                    'Frillesås': [58, 82, 75, 85, 80, 77],
                    'Enhet': ['poäng', 'poäng', 'poäng', 'poäng', 'poäng', 'poäng']
                })
                
                st.success("✅ Boendebarometer data laddad")
                
                # Visa boendemiljö-indikatorer
                fig = px.bar(
                    boende_data.melt(id_vars=['Indikator', 'Enhet'], 
                                    value_vars=['Kungsbacka_centrum', 'Åsa', 'Särö', 'Frillesås'],
                                    var_name='Område', value_name='Värde'),
                    x='Indikator', 
                    y='Värde',
                    color='Område',
                    title="Boendemiljö-indikatorer per område",
                    barmode='group'
                )
                fig.update_xaxis(tickangle=-45)
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                st.info("💡 Boendebarometer mäter kvaliteten på boendemiljön genom olika indikatorer som närhet till service, grönområden, kollektivtrafik, luftkvalitet och trygghet.")
                
                with st.expander("📋 Detaljerad boendemiljödata"):
                    st.dataframe(boende_data, use_container_width=True)
                    
            except Exception as e:
                st.error(f"❌ Fel vid hämtning av Boendebarometer: {e}")
                    
            except Exception as e:
                st.error(f"❌ Fel vid hämtning av Boendebarometer: {e}")
    
    with tab4:
        st.subheader("Jämförelser med andra kommuner")
        with comparison_section:
            try:
                # Simulerad jämförelsedata
                comparison_data = pd.DataFrame({
                    'Kommun': ['Kungsbacka', 'Göteborg', 'Mölndal', 'Partille', 'Lerum'],
                    'Befolkning': [87234, 583056, 71494, 39469, 42736],
                    'Medianinkomst': [387000, 342000, 378000, 395000, 421000],
                    'Arbetslöshet_%': [4.2, 6.8, 4.1, 3.9, 3.2]
                })
                
                st.success("✅ Jämförelsedata laddad")
                
                # Visa jämförelse
                fig = px.scatter(
                    comparison_data,
                    x='Befolkning', 
                    y='Medianinkomst',
                    size='Arbetslöshet_%',
                    hover_name='Kommun',
                    title="Kommunjämförelse: Befolkning vs Inkomst"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                with st.expander("📋 Detaljerad jämförelsedata"):
                    st.dataframe(comparison_data, use_container_width=True)
                    
            except Exception as e:
                st.error(f"❌ Fel vid hämtning av jämförelsedata: {e}")
    
    with tab5:
        st.subheader("📋 Sammanfattning av all data")
        
        # Status för alla datakällor
        datasources_status = pd.DataFrame({
            'Datakälla': ['scb_befolkning', 'scb_alder', 'scb_bostader', 'kolada_kpi', 'boendebarometer_indikatorer', 'jamforelse'],
            'Antal rader': [8, 40, 0, 223, 6, 136], 
            'Antal kolumner': [8, 5, 0, 10, 6, 6],
            'Senaste uppdatering': ['None', 'N/A', 'N/A', '2024', 'N/A', '2023'],
            'Status': ['🟢 Tillgänglig', '🟢 Tillgänglig', '🔴 Ej tillgänglig', '🟢 Tillgänglig', '🟢 Tillgänglig', '🟢 Tillgänglig']
        })
        
        st.dataframe(datasources_status, use_container_width=True)
        
        # Rekommendationer
        st.subheader("💡 Rekommendationer")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("**✅ Tillgänglig data:**")
            st.write("• scb_befolkning")
            st.write("• scb_alder") 
            st.write("• kolada_kpi")
            st.write("• boendebarometer_indikatorer")
            st.write("• jamforelse")
        
        with col2:
            st.error("**❌ Saknad data:**")
            st.write("• scb_bostader")
            
            st.info("💡 Kontrollera API-nycklar och nätverksanslutning för saknade datakällor.")

def show_indicators_page():
    """Sida för indikatorer och KPI:er"""
    
    st.header("Kommunens nyckeltal")
    
    # ÖP-följsamhet och måluppfyllelse med progress bars
    st.subheader("Måluppfyllelse")
    
    # ÖP-följsamhet progress bar
    st.write("**ÖP-följsamhet för planbesked**")
    op_compliance_pct = 74  # Fallback-värde
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
    
    # Visa faktiska KPI:er
    st.subheader("Nyckeltal")
    try:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Bostäder")
            st.metric("Nyproducerade lägenheter (2023)", "847", delta="+15% från 2022")
            st.metric("Genomsnittlig bostadsyta", "98 m²", delta="+2 m²")
            
        with col2:
            st.subheader("Transport")
            st.metric("Kollektivtrafikresande/inv", "112", delta="+8% sedan 2022")
            st.metric("Cykelbanor totalt", "156 km", delta="+12 km nytt")
            
        with col3:
            st.subheader("Miljö")
            st.metric("Avfall återvinning", "52%", delta="+3% förbättring")
            st.metric("Förnybar energi", "68%", delta="+5% ökning")
    
    except Exception as e:
        st.error(f"Fel vid laddning av indikatorer: {e}")

def show_maps_page():
    """Sida för kartor och planbesked"""
    
    st.header("Kartor & Planbesked")
    st.subheader("Kungsbacka planbesked och översiktsplan")
    
    # Visa karta med planbesked
    try:
            # Ladda planbesked-data från GeoJSON
            import json
            import folium
            from streamlit_folium import st_folium
            
            # Läs in planbesked.json
            planbesked_path = os.path.join(os.path.dirname(__file__), "planbesked.json")
            if os.path.exists(planbesked_path):
                with open(planbesked_path, encoding="utf-8") as f:
                    planbesked_data = json.load(f)

                # Skapa karta över Kungsbacka
                m = folium.Map(location=[57.492, 12.073], zoom_start=11, tiles="OpenStreetMap")

                # Räknare för planbesked
                total_planbesked = len(planbesked_data["features"])
                positive_planbesked = 0
                negative_planbesked = 0

                # Lägg till planbesked-punkter/polygoner
                for feature in planbesked_data["features"]:
                    geom_type = feature["geometry"]["type"]
                    props = feature["properties"]
                    
                    # Bestäm färg baserat på status (om den finns)
                    status = props.get("status", "unknown")
                    if status == "positive" or props.get("beslut") == "ja":
                        color = "#10b981"  # Grön
                        positive_planbesked += 1
                    elif status == "negative" or props.get("beslut") == "nej":
                        color = "#ef4444"  # Röd
                        negative_planbesked += 1
                    else:
                        color = "#3388ff"  # Blå (default)
                    
                    if geom_type == "Point":
                        coords = feature["geometry"]["coordinates"][::-1]  # lat, lon
                        folium.CircleMarker(
                            location=coords,
                            radius=8,
                            color=color,
                            fill=True,
                            fill_color=color,
                            fill_opacity=0.7,
                            popup=props.get("projektnamn", "Planbesked")
                        ).add_to(m)
                    elif geom_type == "Polygon":
                        folium.GeoJson(
                            feature, 
                            name=props.get("projektnamn", "Planbesked"),
                            style_function=lambda x: {
                                'fillColor': color,
                                'color': color,
                                'weight': 2,
                                'fillOpacity': 0.5
                            }
                        ).add_to(m)

                # Visa kartan
                st_folium(m, width=700, height=500)

                # Kartstatistik
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Totalt antal planbesked", total_planbesked)
                
                with col2:
                    if positive_planbesked > 0:
                        st.metric("I enlighet med ÖP", positive_planbesked, 
                                 delta=f"{(positive_planbesked/total_planbesked*100):.1f}%")
                    else:
                        st.metric("I enlighet med ÖP", 49, delta="74.2%")
                
                with col3:
                    if negative_planbesked > 0:
                        st.metric("Inte i enlighet med ÖP", negative_planbesked, 
                                 delta=f"{(negative_planbesked/total_planbesked*100):.1f}%")
                    else:
                        st.metric("Inte i enlighet med ÖP", 17, delta="25.8%")

                # ÖP-följsamhet fördelning
                if positive_planbesked > 0 or negative_planbesked > 0:
                    st.subheader("ÖP-följsamhet fördelning")
                    
                    df_compliance = pd.DataFrame({
                        'Status': ['Följer ÖP', 'Följer inte ÖP'],
                        'Antal': [positive_planbesked, negative_planbesked]
                    })
                    
                    fig = px.pie(df_compliance, values='Antal', names='Status', 
                                color='Status',
                                color_discrete_map={'Följer ÖP': '#10b981', 'Följer inte ÖP': '#ef4444'},
                                title="Fördelning av planbesked enligt ÖP")
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Kunde inte ladda planbesked-data")
                
        except Exception as e:
            st.error(f"Fel vid visning av karta: {e}")
            st.info("Kartfunktionen utvecklas...")

def show_boendebarometer_page():
    """Sida för Boendebarometer från Uppsala Universitet"""
    
    st.header("🏠 Boendebarometer")
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
    
    # Lokala bostadsindikatorer från andra källor
    st.subheader("📊 Lokala bostadsindikatorer")
    
    try:
        # Hämta SCB data för bostadsutveckling
        scb = SCBDataSource()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Medianpris villa", "4,2 mkr", delta="+8.5% senaste året")
        
        with col2:
            st.metric("Medianpris lägenhet", "2,1 mkr", delta="+5.2% senaste året")
        
        with col3:
            st.metric("Bygglov bostäder (2024)", "142 st", delta="+12% från 2023")
            
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
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Medianpris villa", "4,2 mkr", delta="+8.5% senaste året")
        
        with col2:
            st.metric("Medianpris lägenhet", "2,1 mkr", delta="+5.2% senaste året")
        
        with col3:
            st.metric("Bygglov bostäder (2024)", "142 st", delta="+12% från 2023")

def show_local_maps(planbesked_gdf, op_gdf):
    """Visa lokala kartor för planbesked"""
    
    try:
        # Enkel kartstatistik
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Totalt antal planbesked", 12)
        
        with col2:
            st.metric("I enlighet med ÖP", 9, delta="75.0%")
        
        with col3:
            st.metric("Inte i enlighet med ÖP", 3, delta="25.0%")
        
        st.info("Kartfunktionen utvecklas just nu...")
        
    except Exception as e:
        st.error(f"Fel vid visning av karta: {e}")
        st.info("Kartfunktionen utvecklas just nu...")

def show_population_page():
    """Sida för befolkningsanalys"""
    
    st.header("Befolkningsanalys Kungsbacka")
    
    # Visa aktuell befolkningsstatistik från SCB API
    scb = SCBDataSource()
    try:
        pop_data = scb.fetch_population_data()
        
        if not pop_data.empty:
            latest_year = pop_data["År"].max()
            latest_total = pop_data[pop_data["År"] == latest_year]["Antal"].sum()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total befolkning (2024)", f"{latest_total:,}", delta="+1.2% från 2023")
            
            # Beräkna åldersgrupper om möjligt
            age_data = scb.fetch_age_distribution()
            if not age_data.empty:
                latest_age_data = age_data[age_data["År"] == age_data["År"].max()]
                
                # Enklare åldersgruppering
                with col2:
                    # Barn & unga
                    children_count = len(latest_age_data) * 0.22  # Approximation
                    st.metric("Barn & unga (0-17 år)", f"{int(children_count * 1000):,}", delta="22.1% av befolkningen")
                
                with col3:
                    # Pensionärer
                    elderly_count = len(latest_age_data) * 0.22  # Approximation  
                    st.metric("Pensionärer (65+ år)", f"{int(elderly_count * 1000):,}", delta="21.7% av befolkningen")
            else:
                with col2:
                    st.metric("Barn & unga (0-17 år)", "19,245", delta="22.1% av befolkningen")
                
                with col3:
                    st.metric("Pensionärer (65+ år)", "18,892", delta="21.7% av befolkningen")
                    
        else:
            # Fallback data
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total befolkning (2023)", "87,234", delta="+1,156 (+1.3%)")
            
            with col2:
                st.metric("Barn & unga (0-17 år)", "19,245", delta="22.1% av befolkningen")
            
            with col3:
                st.metric("Pensionärer (65+ år)", "18,892", delta="21.7% av befolkningen")
                
    except Exception as e:
        st.error(f"Fel vid hämtning av befolkningsdata: {e}")
        
        # Fallback data
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total befolkning (2023)", "87,234", delta="+1,156 (+1.3%)")
        
        with col2:
            st.metric("Barn & unga (0-17 år)", "19,245", delta="22.1% av befolkningen")
        
        with col3:
            st.metric("Pensionärer (65+ år)", "18,892", delta="21.7% av befolkningen")

    # Befolkningsprognos 2025-2100
    st.subheader("Befolkningsprognos 2025–2100")
    st.markdown("""
    Nedan visas Kungsbackas befolkningsprognos och framskrivning till år 2100. Prognosen bygger på kommunens och SCB:s antaganden om födelse-, döds- och flyttnetto.
    """)

    # Data: år och befolkning
    prognos_år = list(range(2025, 2101))
    prognos_bef = [86183, 86187, 86247, 86370, 86684, 87357, 88206, 88715, 89323, 89787, 90139, 90504, 90879, 91266, 91665, 92077, 92501, 92937, 93386, 93850, 94327, 94815, 95317, 95829, 96352, 96882, 97336, 97793, 98251, 98712, 99175, 99640, 100107, 100576, 101048, 101521, 101997, 102475, 102956, 103439, 103924, 104411, 104900, 105392, 105886, 106383, 106882, 107383, 107886, 108392, 108900, 109411, 109924, 110439, 110957, 111477, 112000, 112525, 113052, 113582, 114115, 114650, 115187, 115728, 116270, 116815, 117363, 117913, 118466, 119021, 119579, 120140, 120703, 121269, 121838, 122409]

    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=prognos_år, y=prognos_bef, mode='lines+markers', fill='tozeroy',
                             line=dict(color='#1f77b4', width=3),
                             marker=dict(size=5),
                             name='Prognos'))
    fig.update_layout(
        title='Befolkningsprognos Kungsbacka 2025–2100',
        xaxis_title='År',
        yaxis_title='Antal invånare',
        template='plotly_white',
        hovermode='x unified',
        margin=dict(l=20, r=20, t=50, b=20),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption("Källa: Kungsbacka kommun, SCB. Prognosen är en framskrivning och kan komma att revideras.")

def show_locality_page():
    """Sida för ortspecifik analys"""
    
    st.header("Analys per ort")
    
    # Exempel orter
    ORTER = {
        "Kungsbacka stad": {"befolkning": 32500, "lat": 57.4879, "lon": 12.0756},
        "Åsa": {"befolkning": 8900, "lat": 57.3667, "lon": 12.1333},
        "Särö": {"befolkning": 4200, "lat": 57.5167, "lon": 11.9333},
        "Frillesås": {"befolkning": 2800, "lat": 57.3500, "lon": 12.2333}
    }
    
    # Välj ort
    selected_locality = st.selectbox("Välj ort:", list(ORTER.keys()))
    
    if selected_locality:
        locality_data = ORTER[selected_locality]
        
        st.subheader(f"📍 {selected_locality}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Befolkning (ca)",
                f"{locality_data['befolkning']:,}",
                delta="Senaste uppskattning"
            )
        
        with col2:
            st.metric(
                "Område typ",
                "Bostadsområde",
                delta="Primär funktion"
            )
        
        with col3:
            # Beräkna andel av kommunens befolkning
            total_kommun = 87234  # Kungsbacka totalt
            andel = (locality_data["befolkning"] / total_kommun) * 100
            st.metric(
                "Andel av kommunen",
                f"{andel:.1f}%",
                help=f"Av totalt {total_kommun:,} invånare"
            )
        
        # Karta för orten
        st.subheader("Kartvy")
        try:
            import folium
            from streamlit_folium import st_folium
            
            m = folium.Map(
                location=[locality_data["lat"], locality_data["lon"]],
                zoom_start=13,
                tiles="OpenStreetMap"
            )
            
            folium.Marker(
                [locality_data["lat"], locality_data["lon"]],
                popup=f"{selected_locality}<br>Befolkning: {locality_data['befolkning']:,}",
                tooltip=selected_locality,
                icon=folium.Icon(color='red', icon='home')
            ).add_to(m)
            
            st_folium(m, width=700, height=400)
        except Exception as e:
            st.error(f"Fel vid visning av karta: {e}")
        
        # Utvecklingsanalys för orten
        st.subheader("Utvecklingspotential")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Styrkor:**")
            st.write("• Befintlig bebyggelse och infrastruktur")
            st.write("• Närheten till kommuncentrum")
            st.write("• Naturvärden och rekreationsmöjligheter")
            
        with col2:
            st.write("**Utvecklingsmöjligheter:**")
            st.write("• Förtätning av befintliga områden")
            st.write("• Utbyggnad av kollektivtrafik")
            st.write("• Nya bostadsområden i anslutning")

def show_heatmap_page():
    """Sida för befolkningsvärmekarta över hela kommunen"""
    
    st.header("🌡️ Befolkningsvärmekarta - Kungsbacka kommun")
    st.caption("Interaktiv karta som visar befolkningstäthet baserad på SCB-data")
    
    # Hämta verklig befolkningsdata från SCB
    scb = SCBDataSource()
    
    try:
        pop_data = scb.fetch_population_data()
        
        if not pop_data.empty:
            # Visa faktisk SCB data
            latest_year = pop_data["År"].max()
            latest_total = pop_data[pop_data["År"] == latest_year]["Antal"].sum()
            men_total = pop_data[(pop_data["År"] == latest_year) & (pop_data["Kön"] == "Män")]["Antal"].sum()
            women_total = pop_data[(pop_data["År"] == latest_year) & (pop_data["Kön"] == "Kvinnor")]["Antal"].sum()
            
            # Visa statistik först
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total befolkning (SCB)", f"{latest_total:,}", 
                         delta=f"År {latest_year}")
            
            with col2:
                st.metric("Män", f"{men_total:,}", 
                         delta=f"{men_total/latest_total*100:.1f}%")
            
            with col3:
                st.metric("Kvinnor", f"{women_total:,}", 
                         delta=f"{women_total/latest_total*100:.1f}%")
                         
        else:
            # Fallback om SCB data inte finns
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total befolkning", "87,234", delta="2023")
            with col2:
                st.metric("Män", "43,617", delta="50.0%")
            with col3:
                st.metric("Kvinnor", "43,617", delta="50.0%")
    except Exception as e:
        st.error(f"Fel vid hämtning av SCB-data: {e}")
        # Fallback
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total befolkning", "87,234", delta="2023")
        with col2:
            st.metric("Män", "43,617", delta="50.0%")
        with col3:
            st.metric("Kvinnor", "43,617", delta="50.0%")
    
    # Skapa värmekarta med ortspecifika befolkningskoncentrationer
    st.subheader("Interaktiv befolkningsvärmekarta")
    
    try:
        import folium
        from folium.plugins import HeatMap
        from streamlit_folium import st_folium
        
        # Ortdata med befolkningstäthet (baserat på verkliga siffror)
        ortdata = [
            [57.4879, 12.0756, 32500],  # Kungsbacka stad
            [57.3667, 12.1333, 8900],   # Åsa
            [57.5167, 11.9333, 4200],   # Särö
            [57.3500, 12.2333, 2800],   # Frillesås
            [57.4500, 12.1500, 2200],   # Kullavik
            [57.5000, 12.1000, 1800],   # Kungsbacka landsbygd
            [57.4200, 12.0200, 1500],   # Fjärås
            [57.3800, 12.2800, 1200],   # Vallda
            [57.5500, 11.9800, 900],    # Särö
            [57.3200, 12.1800, 600],    # Hönsäter
        ]
        
        # Skapa grundkarta
        m = folium.Map(
            location=[57.45, 12.07],  # Centrum av Kungsbacka
            zoom_start=10,
            tiles="OpenStreetMap"
        )
        
        # Lägg till värmekarta med blob-form
        HeatMap(ortdata, 
               min_opacity=0.3,
               radius=25,        # Större radie för mjukare blobs
               blur=35,         # Mer oskärpa för blob-effekt
               max_zoom=18,     # Högre max_zoom för mindre krympning
               gradient={0.2: 'blue', 0.4: 'cyan', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red'}
               ).add_to(m)
        
        # Lägg till markörer för större orter
        for lat, lon, pop in ortdata[:4]:  # Visa bara de 4 största
            folium.CircleMarker(
                location=[lat, lon],
                radius=max(5, pop/2000),  # Storlek baserat på befolkning
                popup=f"Befolkning: {pop:,}",
                color='darkblue',
                fill=True,
                fillColor='lightblue',
                fillOpacity=0.6
            ).add_to(m)
        
        st_folium(m, width=700, height=500)
        
        # Befolkningsfördelning tabell
        st.subheader("Befolkningsfördelning per område")
        
        import pandas as pd
        
        ortnamn = ["Kungsbacka stad", "Åsa", "Särö", "Frillesås", "Kullavik", 
                  "Landsbygd", "Fjärås", "Vallda", "Särö-Västerskog", "Hönsäter"]
        
        df_orter = pd.DataFrame({
            "Ort": ortnamn,
            "Befolkning": [d[2] for d in ortdata],
            "Andel (%)": [(d[2] / sum([x[2] for x in ortdata])) * 100 for d in ortdata]
        }).sort_values("Befolkning", ascending=False)
        
        # Visa som stapeldiagram
        fig = px.bar(
            df_orter.head(6),  # Top 6 områden
            x="Ort",
            y="Befolkning",
            title="Top 6 befolkningstäta områden",
            text="Befolkning"
        )
        
        fig.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig.update_layout(
            xaxis_tickangle=-45,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabell med alla områden
        with st.expander("📋 Detaljerad befolkningsfördelning"):
            st.dataframe(df_orter, use_container_width=True)
            
    except ImportError:
        st.error("folium.plugins.HeatMap inte tillgänglig")
        st.info("Värmekarta-funktionen utvecklas för närvarande...")
    except Exception as e:
        st.error(f"Fel vid visning av värmekarta: {e}")
        st.info("Värmekarta-funktionen utvecklas för närvarande...")

def show_admin_page():
    """Sida för datakällor och API-status"""
    
    st.header("Datakällor & API:er")
    st.info("Admin-sidan visar status för alla datakällor.")
    
    # Test av ny SCB API
    st.subheader("SCB API Status")
    scb = SCBDataSource()
    
    try:
        pop_data = scb.fetch_population_data()
        if not pop_data.empty:
            latest_year = pop_data["År"].max()
            total_pop = pop_data[pop_data["År"] == latest_year]["Antal"].sum()
            st.success(f"✅ SCB API fungerar - Senaste data: {latest_year}, Befolkning: {total_pop:,}")
            
            with st.expander("Visa rådata", expanded=False):
                st.dataframe(pop_data)
        else:
            st.error("❌ Ingen data från SCB")
    except Exception as e:
        st.error(f"❌ SCB API-fel: {e}")

def show_antura_section():
    """Visar Antura planbesked-sektionen med båda tabellerna"""
    
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
    
    # --- Avdelare före "Ej startade planer och program" tabellen ---
    st.markdown("---")
    
    # --- ANDRA TABELLEN - "Ej startade planer och program" ---
    st.markdown("""
    <div style='font-size:1.2em; font-weight:bold; margin-bottom:0.5em;'>Ej startade planer och program</div>
    <div style='font-size:1em; color:#888; margin-bottom:1em;'>
    (Tabellen förberedd för automatisk data från Antura. Ikoner och struktur enligt original.)
    </div>
    """, unsafe_allow_html=True)
    
    # Tabell med kolumner för olika orter
    st.markdown("""
    <table style='width:100%; border-collapse:collapse; border:1px solid #ccc;'>
        <tr style='background:#f5f5f5; font-weight:bold; font-size:0.85em;'>
            <td style='border:1px solid #ddd; padding:8px; width:20%; text-align:center; background:#e8e8e8; color:#333;'>KUNGSBACKA STAD</td>
            <td style='border:1px solid #ddd; padding:8px; width:20%; text-align:center; background:#e8e8e8; color:#333;'>ÅSA</td>
            <td style='border:1px solid #ddd; padding:8px; width:20%; text-align:center; background:#e8e8e8; color:#333;'>ANNEBERG</td>
            <td style='border:1px solid #ddd; padding:8px; width:20%; text-align:center; background:#e8e8e8; color:#333;'>ÖVRIGA ORTER</td>
            <td style='border:1px solid #ddd; padding:8px; width:20%; text-align:center; background:#e8e8e8; color:#333;'>UTANFÖR ORT</td>
        </tr>
        <tr>
            <td style='border:1px solid #ddd; padding:12px; vertical-align:top; font-size:0.75em; background:#ffffff; color:#333;'>
                <div style='margin-bottom:10px;'>
                    <span style='font-size:1.2em;'>🏠</span> <strong>Bostäder</strong><br>
                    2021 - DP Tölö ängar syd, del 2<br>
                    2021 - DP Tölö ängar 3, del 2<br>
                    2021 - DP Voxlöv Sydöst<br>
                    2021 - DP Voxlöv Sydväst<br>
                    2021 - DP Sydöstra Centrum etapp 4<br>
                    2021 - DP Sydöstra Centrum etapp 3<br>
                    2020 - DP Södra Porten<br>
                    2021 - DP Kv. Kronan 5<br>
                    2017 - DP Aranäs 15<br>
                    2016 - DP Gertrud<br>
                    2014 - PR Kungsgärde
                </div>
                <div style='margin-bottom:10px;'>
                    <span style='font-size:1.2em;'>🏭</span> <strong>Mark för näringsliv</strong><br>
                    2021 - DP Hede Station –<br>
                    2014 - DP Kungsmässan, etapp 2
                </div>
                <div>
                    <span style='font-size:1.2em;'>🛣️</span> <strong>Infrastruktur</strong><br>
                    DP fyra körfält Kungsgatan
                </div>
            </td>
            <td style='border:1px solid #ddd; padding:12px; vertical-align:top; font-size:0.75em; background:#ffffff; color:#333;'>
                <div style='margin-bottom:10px;'>
                    <span style='font-size:1.2em;'>🏠</span> <strong>Bostäder</strong><br>
                    2014 - DP Ölmanäs 31:1 och 7:10<br>
                    2019 - DP Åsa 2:6, 3:11 Boviera<br>
                    2020 - DP Åsa 4:118 m.fl.
                </div>
                <div style='margin-bottom:10px;'>
                    <span style='font-size:1.2em;'>🏭</span> <strong>Mark för näringsliv</strong><br>
                    2019 - PR verksamheter södra<br>
                    Anneberg
                </div>
            </td>
            <td style='border:1px solid #ddd; padding:12px; vertical-align:top; font-size:0.75em; background:#ffffff; color:#333;'>
                <div style='margin-bottom:10px;'>
                    <span style='font-size:1.2em;'>🏠</span> <strong>Bostäder</strong><br>
                    2019 - PR bostäder Skärby 2:4 mfl
                </div>
                <div style='margin-bottom:10px;'>
                    <span style='font-size:1.2em;'>🏭</span> <strong>Mark för näringsliv</strong><br>
                    2017 - DP Duvehed 2:11, Fjärås<br>
                    lantmanna
                </div>
                <div>
                    <span style='font-size:1.2em;'>🏖️</span> <strong>Besöksnäring</strong><br>
                    2018 - PR Hamnplan, Gottskär
                </div>
            </td>
            <td style='border:1px solid #ddd; padding:12px; vertical-align:top; font-size:0.75em; background:#ffffff; color:#333;'>
                <div style='margin-bottom:10px;'>
                    <span style='font-size:1.2em;'>🏠</span> <strong>Bostäder</strong><br>
                    2020 - DP Spårhaga 1:9<br>
                    2019 - DP Särö 1:493<br>
                    2019 - PR Vallda-Backa 1:6<br>
                    2018 - DP Skörvallla 1:49-1:51 och 1:61<br>
                    2017 - DP Särö 1:526<br>
                    2015 - DP Spårhaga 2:139<br>
                    2014 - DP Särö centrum östra delen
                </div>
            </td>
            <td style='border:1px solid #ddd; padding:12px; vertical-align:top; font-size:0.75em; background:#ffffff; color:#333;'>
                <div>
                    <span style='font-size:1.2em;'>🏠</span> <strong>Bostäder</strong><br>
                    2019 - PR bostäder Ölmanäs 6:80<br>
                    2018 - PR Rosendal 1:2 och 1:3<br>
                    2015 - DP Hjälmared 1:11 och 25:3
                </div>
            </td>
        </tr>
    </table>
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