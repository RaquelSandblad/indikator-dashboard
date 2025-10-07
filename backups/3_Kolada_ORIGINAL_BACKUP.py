"""
Kolada - Kommun- och landstingsdatabasen
Visar nyckeltal och KPI:er från Kolada för kommunjämförelser
"""

import streamlit as st
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Lägg till root directory till path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import av Kolada connector
from data.kolada_connector import kolada

st.set_page_config(
    page_title="Kolada - Kungsbacka",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Kolada - Kommunala Nyckeltal")
st.markdown("Aktuella nyckeltal och KPI:er för Kungsbacka kommun från Kolada-databasen")

# API Status i toppen
col_status1, col_status2 = st.columns([3, 1])
with col_status1:
    st.info("📊 **Live-data från Kolada API** - Uppdateras automatiskt varje vecka")
with col_status2:
    try:
        # Testa API-anslutning
        test_data = kolada.get_latest_value("N01951")  # Folkmängd
        if test_data:
            st.success("✅ API Aktiv")
        else:
            st.warning("⚠️ Ingen data")
    except:
        st.error("❌ API-fel")

st.markdown("---")

# === NYCKELTAL ÖVERSIKT ===
st.subheader("📊 Viktiga nyckeltal för Kungsbacka")

# Rad 1: Befolkning och demografi
col1, col2, col3, col4 = st.columns(4)

with col1:
    try:
        data = kolada.get_latest_value("N01951")  # Folkmängd
        if data:
            st.metric(
                "👥 Folkmängd",
                f"{int(data['värde']):,}".replace(',', ' '),
                help=f"Antal invånare 31 december ({data['år']})"
            )
        else:
            st.metric("👥 Folkmängd", "Data saknas")
    except Exception as e:
        st.metric("👥 Folkmängd", "Laddningsfel")

with col2:
    try:
        data = kolada.get_latest_value("N00913")  # Nybyggda lägenheter
        if data:
            st.metric(
                "🏗️ Nybyggda lägenheter",
                f"{int(data['värde'])} st",
                help=f"Färdigställda under året ({data['år']})"
            )
        else:
            st.metric("🏗️ Nybyggda lägenheter", "Data saknas")
    except Exception as e:
        st.metric("🏗️ Nybyggda lägenheter", "Laddningsfel")

with col3:
    try:
        data = kolada.get_latest_value("N07932")  # Bostadslägenheter totalt
        if data:
            st.metric(
                "🏠 Bostadslägenheter",
                f"{int(data['värde']):,}".replace(',', ' '),
                help=f"Totalt antal lägenheter ({data['år']})"
            )
        else:
            st.metric("🏠 Bostadslägenheter", "Data saknas")
    except Exception as e:
        st.metric("🏠 Bostadslägenheter", "Laddningsfel")

with col4:
    try:
        data = kolada.get_latest_value("N00945")  # Bygglov
        if data:
            st.metric(
                "📋 Bygglov bostäder",
                f"{int(data['värde'])} st",
                help=f"Antal beviljade bygglov ({data['år']})"
            )
        else:
            st.metric("📋 Bygglov", "Data saknas")
    except Exception as e:
        st.metric("📋 Bygglov", "Laddningsfel")

# Rad 2: Planering
st.markdown("###")
col1, col2, col3, col4 = st.columns(4)

with col1:
    try:
        data = kolada.get_latest_value("N07925")  # Antagna detaljplaner
        if data:
            st.metric(
                "✅ Antagna detaljplaner",
                f"{int(data['värde'])} st",
                help=f"Antal under året ({data['år']})"
            )
        else:
            st.metric("✅ Antagna detaljplaner", "Data saknas")
    except:
        st.metric("✅ Antagna detaljplaner", "Data saknas")

with col2:
    try:
        data = kolada.get_latest_value("N07924")  # Pågående detaljplaner
        if data:
            st.metric(
                "🔄 Pågående detaljplaner",
                f"{int(data['värde'])} st",
                help=f"Antal pågående ({data['år']})"
            )
        else:
            st.metric("🔄 Pågående detaljplaner", "Data saknas")
    except:
        st.metric("🔄 Pågående detaljplaner", "Data saknas")

with col3:
    try:
        data = kolada.get_latest_value("N00914")  # Påbörjade lägenheter
        if data:
            st.metric(
                "� Påbörjade lägenheter",
                f"{int(data['värde'])} st",
                help=f"Byggstart under året ({data['år']})"
            )
        else:
            st.metric("� Påbörjade lägenheter", "Data saknas")
    except:
        st.metric("� Påbörjade lägenheter", "Data saknas")

with col4:
    try:
        # Beräkna lägenheter per invånare
        bostader_data = kolada.get_latest_value("N07932")
        befolkning_data = kolada.get_latest_value("N01951")
        
        if bostader_data and befolkning_data:
            läg_per_inv = (bostader_data['värde'] / befolkning_data['värde']) * 1000
            st.metric(
                "🏘️ Lägenheter per 1000 inv",
                f"{läg_per_inv:.0f} st",
                help=f"Bostadstäthet ({bostader_data['år']})"
            )
        else:
            st.metric("🏘️ Bostadstäthet", "Data saknas")
    except:
        st.metric("🏘️ Bostadstäthet", "Beräkningsfel")

# Rad 3: Hållbarhet och demografi
st.markdown("###")
col1, col2, col3, col4 = st.columns(4)

with col1:
    try:
        data = kolada.get_latest_value("N00974")  # Hållbart resande
        if data:
            st.metric(
                "🚴 Hållbart resande",
                f"{data['värde']:.1f}%",
                help=f"Andel som reser hållbart till arbete ({data['år']})"
            )
        else:
            st.metric("🚴 Hållbart resande", "Data saknas")
    except:
        st.metric("🚴 Hållbart resande", "Data saknas")

with col2:
    try:
        data = kolada.get_latest_value("N00956")  # Avstånd till hållplats
        if data:
            st.metric(
                "🚏 Nära kollektivtrafik",
                f"{data['värde']:.1f}%",
                help=f"Andel inom gång-/cykelavstånd till hållplats ({data['år']})"
            )
        else:
            st.metric("🚏 Nära kollektivtrafik", "Data saknas")
    except:
        st.metric("🚏 Nära kollektivtrafik", "Data saknas")

with col3:
    try:
        # Beräkna befolkningstillväxt från trenddata
        trend = kolada.get_trend_data("N01951", years=2)
        if not trend.empty and len(trend) >= 2:
            aktuell = trend.iloc[-1]['värde']
            förra = trend.iloc[-2]['värde']
            tillvaxt = ((aktuell - förra) / förra) * 100
            
            st.metric(
                "📈 Befolkningstillväxt",
                f"{tillvaxt:+.2f}%",
                delta=f"Senaste året",
                help=f"Förändring {trend.iloc[-2]['år']} → {trend.iloc[-1]['år']}"
            )
        else:
            st.metric("📈 Befolkningstillväxt", "Data saknas")
    except:
        st.metric("📈 Befolkningstillväxt", "Beräkningsfel")

with col4:
    try:
        # Beräkna byggaktivitet (nybyggda per 1000 invånare)
        nybyggda = kolada.get_latest_value("N00913")
        befolkning = kolada.get_latest_value("N01951")
        
        if nybyggda and befolkning:
            per_1000 = (nybyggda['värde'] / befolkning['värde']) * 1000
            st.metric(
                "🏗️ Byggaktivitet",
                f"{per_1000:.1f}",
                help=f"Nybyggda lägenheter per 1000 invånare ({nybyggda['år']})"
            )
        else:
            st.metric("🏗️ Byggaktivitet", "Data saknas")
    except:
        st.metric("🏗️ Byggaktivitet", "Beräkningsfel")

# Rad 4: Ytterligare nyckeltal
st.markdown("###")
col1, col2, col3, col4 = st.columns(4)

with col1:
    try:
        # Beräkna genomsnittlig bygglovstid från trenddata
        bygglov_trend = kolada.get_trend_data("N00945", years=3)
        if not bygglov_trend.empty:
            genomsnitt = bygglov_trend['värde'].mean()
            st.metric(
                "📊 Bygglov (snitt 3 år)",
                f"{genomsnitt:.0f} st/år",
                help="Genomsnittligt antal bygglov senaste 3 åren"
            )
        else:
            st.metric("📊 Bygglov genomsnitt", "Data saknas")
    except:
        st.metric("📊 Bygglov genomsnitt", "Data saknas")

with col2:
    try:
        # Beräkna planaktivitet (antagna + pågående)
        antagna = kolada.get_latest_value("N07925")
        pagaende = kolada.get_latest_value("N07924")
        
        if antagna and pagaende:
            totalt = int(antagna['värde']) + int(pagaende['värde'])
            st.metric(
                "📋 Total planaktivitet",
                f"{totalt} st",
                help=f"Antagna + pågående detaljplaner ({antagna['år']})"
            )
        else:
            st.metric("📋 Planaktivitet", "Data saknas")
    except:
        st.metric("📋 Planaktivitet", "Beräkningsfel")

with col3:
    try:
        # Bostadstäckningsgrad från trenddata
        bostader_trend = kolada.get_trend_data("N07932", years=5)
        befolkning_trend = kolada.get_trend_data("N01951", years=5)
        
        if not bostader_trend.empty and not befolkning_trend.empty and len(bostader_trend) >= 2:
            bostader_tillvaxt = ((bostader_trend.iloc[-1]['värde'] - bostader_trend.iloc[0]['värde']) / bostader_trend.iloc[0]['värde']) * 100
            
            st.metric(
                "🏘️ Bostadstillväxt 5 år",
                f"{bostader_tillvaxt:+.1f}%",
                help=f"Förändring i bostadsbestånd {bostader_trend.iloc[0]['år']}-{bostader_trend.iloc[-1]['år']}"
            )
        else:
            st.metric("🏘️ Bostadstillväxt", "Data saknas")
    except:
        st.metric("🏘️ Bostadstillväxt", "Beräkningsfel")

with col4:
    try:
        # Hållbarhetsindex (kombinerat mått)
        hallbart = kolada.get_latest_value("N00974")
        kollektiv = kolada.get_latest_value("N00956")
        
        if hallbart and kollektiv:
            index = (hallbart['värde'] + kollektiv['värde']) / 2
            st.metric(
                "♻️ Hållbarhetsindex",
                f"{index:.1f}%",
                help="Genomsnitt av hållbart resande och närhet till kollektivtrafik"
            )
        else:
            st.metric("♻️ Hållbarhetsindex", "Data saknas")
    except:
        st.metric("♻️ Hållbarhetsindex", "Beräkningsfel")

st.markdown("---")

# === TRENDANALYS ===
st.subheader("� Trendanalys - Befolkningsutveckling")

try:
    trend_data = kolada.get_trend_data("N01951", years=10)  # Folkmängd senaste 10 åren
    
    if not trend_data.empty:
        fig = px.line(
            trend_data,
            x='år',
            y='värde',
            title='Folkmängd i Kungsbacka kommun (senaste 10 åren)',
            labels={'år': 'År', 'värde': 'Antal invånare'}
        )
        fig.update_traces(mode='lines+markers', line_color='#1f77b4', marker_size=8)
        fig.update_layout(hovermode='x unified', height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Ingen trenddata tillgänglig för befolkning")
except Exception as e:
    st.error(f"❌ Kunde inte hämta trenddata: {e}")

st.markdown("---")

# === BOSTADSBYGGANDE ===
st.subheader("🏘️ Bostadsbyggande")

col1, col2 = st.columns(2)

with col1:
    try:
        bygglov_data = kolada.get_trend_data("N00945", years=5)  # Bygglov för bostäder
        if not bygglov_data.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=bygglov_data['år'],
                y=bygglov_data['värde'],
                name='Bygglov',
                marker_color='#2ca02c'
            ))
            fig.update_layout(
                title='Antal bygglov för bostäder',
                xaxis_title='År',
                yaxis_title='Antal',
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Bygglovsdata ej tillgänglig")
    except:
        st.warning("⚠️ Kunde inte hämta bygglovsdata")

with col2:
    try:
        nybyggda_data = kolada.get_trend_data("N00913", years=5)  # Nybyggda lägenheter
        if not nybyggda_data.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=nybyggda_data['år'],
                y=nybyggda_data['värde'],
                name='Nybyggda',
                marker_color='#ff7f0e'
            ))
            fig.update_layout(
                title='Nybyggda lägenheter',
                xaxis_title='År',
                yaxis_title='Antal',
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nybyggnadsdata ej tillgänglig")
    except:
        st.warning("⚠️ Kunde inte hämta nybyggnadsdata")

st.markdown("---")

# === KOMMUNJÄMFÖRELSE ===
st.subheader("📊 Regionala jämförelser")

st.markdown("**Jämför Kungsbacka med kommuner i Halland och Göteborgsregionen**")

# Tabs för olika jämförelser
tab1, tab2 = st.tabs(["Hallands kommuner", "Göteborgsregionen (GR)"])

with tab1:
    st.markdown("### Jämförelse med kommuner i Halland")
    try:
        # Hämta folkmängd för Hallands kommuner
        jamforelse_halland = kolada.compare_municipalities(
            "N01951", 
            kommun_koder=list(kolada.HALLAND_KOMMUNER.keys())
        )
        
        if not jamforelse_halland.empty:
            jamforelse_halland_sorted = jamforelse_halland.sort_values('värde', ascending=False)
            
            # Stapeldiagram
            fig = px.bar(
                jamforelse_halland_sorted,
                x='kommun_namn',
                y='värde',
                title=f'Folkmängd - Hallands kommuner ({jamforelse_halland_sorted["år"].iloc[0]})',
                labels={'kommun_namn': 'Kommun', 'värde': 'Antal invånare'},
                color='kommun_namn',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            # Markera Kungsbacka med röd kant
            fig.update_traces(
                marker_line_color=['red' if x == 'Kungsbacka' else 'white' for x in jamforelse_halland_sorted['kommun_namn']],
                marker_line_width=[4 if x == 'Kungsbacka' else 0 for x in jamforelse_halland_sorted['kommun_namn']],
                selector=dict(type='bar')
            )
            
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabell
            st.markdown("**Detaljerad jämförelse:**")
            display_df = jamforelse_halland_sorted[['kommun_namn', 'värde', 'år']].copy()
            display_df.columns = ['Kommun', 'Folkmängd', 'År']
            display_df['Folkmängd'] = display_df['Folkmängd'].apply(lambda x: f"{int(x):,}".replace(',', ' '))
            
            # Lägg till ranking
            display_df.insert(0, 'Placering', range(1, len(display_df) + 1))
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Hitta Kungsbackas position
            kb_position = jamforelse_halland_sorted.reset_index(drop=True)
            kb_index = kb_position[kb_position['kommun_namn'] == 'Kungsbacka'].index[0]
            st.info(f"🏅 Kungsbacka är **placering {kb_index + 1}** av {len(jamforelse_halland_sorted)} kommuner i Halland")
        else:
            st.warning("⚠️ Ingen data tillgänglig för Halland")
    except Exception as e:
        st.error(f"❌ Kunde inte hämta data: {e}")

with tab2:
    st.markdown("### Jämförelse med Göteborgsregionen (GR)")
    st.info("""
    **Göteborgsregionen omfattar 13 kommuner:** Ale, Alingsås, Göteborg, Härryda, Kungsbacka, 
    Kungälv, Lerum, Lilla Edet, Mölndal, Partille, Stenungsund, Tjörn och Öckerö.
    """)
    
    # Selector för vilken KPI att jämföra
    kpi_choice = st.selectbox(
        "Välj nyckeltal att jämföra:",
        options=[
            ("N01951", "Folkmängd"),
            ("N00913", "Nybyggda lägenheter"),
            ("N07932", "Bostadslägenheter totalt"),
            ("N00945", "Bygglov för bostäder")
        ],
        format_func=lambda x: x[1],
        key="gr_kpi"
    )
    
    try:
        # Hämta data för valda KPI:n
        jamforelse_gr = kolada.compare_municipalities(
            kpi_choice[0], 
            kommun_koder=list(kolada.GOTEBORGSREGIONEN_KOMMUNER.keys())
        )
        
        if not jamforelse_gr.empty:
            jamforelse_gr_sorted = jamforelse_gr.sort_values('värde', ascending=False)
            
            # Stapeldiagram - visa alla 13 kommuner
            fig = px.bar(
                jamforelse_gr_sorted,
                x='kommun_namn',
                y='värde',
                title=f'{kpi_choice[1]} - GR:s 13 kommuner ({jamforelse_gr_sorted["år"].iloc[0]})',
                labels={'kommun_namn': 'Kommun', 'värde': kpi_choice[1]},
                color='kommun_namn',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            
            # Markera Kungsbacka
            fig.update_traces(
                marker_line_color=['red' if x == 'Kungsbacka' else 'white' for x in jamforelse_gr_sorted['kommun_namn']],
                marker_line_width=[4 if x == 'Kungsbacka' else 0 for x in jamforelse_gr_sorted['kommun_namn']],
                selector=dict(type='bar')
            )
            
            fig.update_layout(showlegend=False, height=450, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Hitta Kungsbackas position
            kb_in_list = jamforelse_gr_sorted[jamforelse_gr_sorted['kommun_namn'] == 'Kungsbacka']
            if not kb_in_list.empty:
                kb_index = jamforelse_gr_sorted.reset_index(drop=True)[jamforelse_gr_sorted.reset_index(drop=True)['kommun_namn'] == 'Kungsbacka'].index[0]
                kb_value = kb_in_list.iloc[0]['värde']
                st.success(f"🎯 Kungsbacka: **Placering {kb_index + 1}** av 13 kommuner i GR med värde: **{int(kb_value):,}".replace(',', ' '))
            
            # Tabell med alla 13 kommuner
            st.markdown("**Detaljerad jämförelse:**")
            display_df_all = jamforelse_gr_sorted[['kommun_namn', 'värde', 'år']].copy()
            display_df_all.columns = ['Kommun', kpi_choice[1], 'År']
            display_df_all[kpi_choice[1]] = display_df_all[kpi_choice[1]].apply(lambda x: f"{int(x):,}".replace(',', ' '))
            display_df_all.insert(0, 'Placering', range(1, len(display_df_all) + 1))
            st.dataframe(display_df_all, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ Ingen data tillgänglig för Göteborgsregionen")
    except Exception as e:
        st.error(f"❌ Kunde inte hämta data: {e}")

st.markdown("---")

# === INFO OM KOLADA ===
with st.expander("ℹ️ Om Kolada och datakällan"):
    st.markdown("""
    ### Om Kolada
    
    **Kolada** (Kommun- och landstingsdatabasen) är Sveriges största databas för kommunal och regional data.
    
    **Datakällor:**
    - SCB (Statistiska centralbyrån)
    - SKR (Sveriges Kommuner och Regioner)
    - Kommunernas egna rapporteringar
    
    **API-dokumentation:**  
    [https://www.kolada.se/verktyg/api](https://www.kolada.se/verktyg/api)
    
    **Uppdateringsfrekvens:**
    - Data cachas lokalt i 7 dagar
    - Automatisk uppdatering från API
    - Majoriteten av nyckeltal uppdateras årligen
    
    **Jämförelsekommuner:**
    Kungsbacka jämförs med närliggande och liknande kommuner som Kungälv, Härryda, Ale, Stenungsund, och Tjörn.
    """)
