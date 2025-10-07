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
        data = kolada.get_latest_value("N00945")  # Bygglov
        if data:
            st.metric(
                "📋 Beviljade bygglov",
                f"{int(data['värde'])} st",
                help=f"Antal beviljade bygglov för bostäder ({data['år']})"
            )
        else:
            st.metric("📋 Beviljade bygglov", "Data saknas")
    except Exception as e:
        st.metric("📋 Beviljade bygglov", "Laddningsfel")

with col3:
    try:
        data = kolada.get_latest_value("N07925")  # Antagna detaljplaner
        if data:
            st.metric(
                "✅ Antagna detaljplaner",
                f"{data['värde']:.1f}",
                help=f"Antal detaljplaner som antagits ({data['år']})"
            )
        else:
            st.metric("✅ Antagna detaljplaner", "Data saknas")
    except:
        st.metric("✅ Antagna detaljplaner", "Data saknas")

with col4:
    try:
        data = kolada.get_latest_value("N07924")  # Pågående detaljplaner
        if data:
            st.metric(
                "🔄 Pågående detaljplaner",
                f"{data['värde']:.1f}",
                help=f"Antal pågående detaljplaner ({data['år']})"
            )
        else:
            st.metric("🔄 Pågående detaljplaner", "Data saknas")
    except:
        st.metric("🔄 Pågående detaljplaner", "Data saknas")

# Rad 2: Hållbarhet och tillväxt
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
        # Beräkna planaktivitet (antagna + pågående)
        antagna = kolada.get_latest_value("N07925")
        pagaende = kolada.get_latest_value("N07924")
        
        if antagna and pagaende:
            totalt = antagna['värde'] + pagaende['värde']
            st.metric(
                "📋 Total planaktivitet",
                f"{totalt:.1f}",
                help=f"Antagna + pågående detaljplaner ({antagna['år']})"
            )
        else:
            st.metric("📋 Planaktivitet", "Data saknas")
    except:
        st.metric("📋 Planaktivitet", "Beräkningsfel")

# Rad 3: Data som saknas - placeras sist
st.markdown("###")
st.markdown("**⚠️ Följande nyckeltal saknar data i Kolada:**")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("�️ Nybyggda lägenheter", "Data saknas", help="KPI N00913 - Ingen data tillgänglig för Kungsbacka")

with col2:
    st.metric("🔨 Påbörjade lägenheter", "Data saknas", help="KPI N00914 - Ingen data tillgänglig för Kungsbacka")

with col3:
    st.info("Kontakta Kolada för att rapportera in denna data")

with col4:
    pass

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

# ============================================================
# DETALJERADE ANALYSER - FLIKAR
# ============================================================

st.markdown("---")
st.markdown("## 📑 Detaljerade analyser")
st.markdown("**Utforska djupare inom varje område:**")

# Skapa flikar för detaljerade analyser
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💼 Arbetsmarknad",
    "🎓 Utbildning",
    "👶👵 Omsorg & Välfärd",
    "🌱 Miljö & Hållbarhet",
    "🎭 Kultur & Fritid"
])

# ==================== FLIK 1: ARBETSMARKNAD ====================
with tab1:
    st.header("💼 Arbetsmarknad")
    st.markdown("**Sysselsättning, arbetslöshet och företagande**")
    
    with st.spinner("Hämtar arbetsmarknadsdata från Kolada..."):
        # Senaste värden
        sysselsattning = kolada.get_latest_value("N11800")
        arbetslosa = kolada.get_latest_value("N01720")
        nystartade = kolada.get_latest_value("N01004")
        sysselsatta_antal = kolada.get_latest_value("N02201")
        
        # Trenddata
        syss_trend = kolada.get_sysselsattning(years=10)
        arblos_trend = kolada.get_arbetslöshet(years=10)
        
        # Jämförelsedata
        syss_jamfor = kolada.compare_municipalities("N11800")
        arblos_jamfor = kolada.compare_municipalities("N01720")
    
    # Nyckeltal
    st.subheader("📊 Nyckeltal Kungsbacka")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if sysselsattning:
            st.metric(
                "Förvärvsarbetande 20-64 år",
                f"{sysselsattning['värde']:.1f}%",
                help=f"Data från {sysselsattning['år']}"
            )
    
    with col2:
        if arbetslosa:
            st.metric(
                "Arbetslösa eller i åtgärd",
                f"{arbetslosa['värde']:.1f}%",
                help=f"Data från {arbetslosa['år']}"
            )
    
    with col3:
        if nystartade:
            st.metric(
                "Nystartade arbetsställen",
                f"{nystartade['värde']:.1f}",
                help=f"Antal per 1000 inv 16-64 år ({nystartade['år']})"
            )
    
    with col4:
        if sysselsatta_antal:
            st.metric(
                "Sysselsatta totalt",
                f"{int(sysselsatta_antal['värde']):,}",
                help=f"Efter arbetsställets belägenhet ({sysselsatta_antal['år']})"
            )
    
    # Trender
    st.subheader("📈 Utveckling över tid")
    
    tab_syss, tab_arblos = st.tabs(["Sysselsättning", "Arbetslöshet"])
    
    with tab_syss:
        if not syss_trend.empty:
            fig = px.line(syss_trend, x='år', y='värde',
                         title='Förvärvsarbetande 20-64 år (%)', markers=True)
            fig.update_layout(xaxis_title="År", yaxis_title="Andel (%)", hovermode='x unified')
            fig.update_traces(line_color='#2E86AB', marker=dict(size=8))
            st.plotly_chart(fig, use_container_width=True)
            
            if len(syss_trend) >= 2:
                forsta = syss_trend.iloc[0]['värde']
                senaste = syss_trend.iloc[-1]['värde']
                forandring = senaste - forsta
                st.info(f"📊 **Förändring:** {forsta:.1f}% ({syss_trend.iloc[0]['år']}) → {senaste:.1f}% ({syss_trend.iloc[-1]['år']}) = **{forandring:+.1f}%-enheter**")
    
    with tab_arblos:
        if not arblos_trend.empty:
            fig = px.line(arblos_trend, x='år', y='värde',
                         title='Arbetslösa eller i åtgärd 16-64 år (%)', markers=True)
            fig.update_layout(xaxis_title="År", yaxis_title="Andel (%)", hovermode='x unified')
            fig.update_traces(line_color='#E63946', marker=dict(size=8))
            st.plotly_chart(fig, use_container_width=True)
            
            if len(arblos_trend) >= 2:
                forsta = arblos_trend.iloc[0]['värde']
                senaste = arblos_trend.iloc[-1]['värde']
                forandring = senaste - forsta
                emoji = "🟢" if forandring < 0 else "🔴"
                st.info(f"{emoji} **Förändring:** {forsta:.1f}% ({arblos_trend.iloc[0]['år']}) → {senaste:.1f}% ({arblos_trend.iloc[-1]['år']}) = **{forandring:+.1f}%-enheter**")
    
    # Jämförelser
    st.subheader("🔄 Jämförelse med andra kommuner")
    
    if not syss_jamfor.empty:
        syss_jamfor_sorted = syss_jamfor.sort_values('värde', ascending=False)
        colors = ['#2E86AB' if x == 'Kungsbacka' else '#A8DADC' for x in syss_jamfor_sorted['kommun_namn']]
        
        fig = go.Figure(data=[go.Bar(
            x=syss_jamfor_sorted['kommun_namn'], y=syss_jamfor_sorted['värde'],
            marker_color=colors, text=syss_jamfor_sorted['värde'].round(1), textposition='outside'
        )])
        fig.update_layout(
            title=f"Förvärvsarbetande 20-64 år ({syss_jamfor_sorted['år'].iloc[0]})",
            xaxis_title="Kommun", yaxis_title="Andel (%)", showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

# ==================== FLIK 2: UTBILDNING ====================
with tab2:
    st.header("🎓 Utbildning & Skola")
    st.markdown("**Skolresultat, gymnasieexamen och utbildningskvalitet**")
    
    with st.spinner("Hämtar utbildningsdata från Kolada..."):
        meritvarde = kolada.get_latest_value("N15413")
        behoriga_yrke = kolada.get_latest_value("N15446")
        behoriga_estet = kolada.get_latest_value("N15447")
        examen_3ar = kolada.get_latest_value("N15533")
        examen_4ar = kolada.get_latest_value("N15427")
        matematik_ak6 = kolada.get_latest_value("N18216")
        svenska_ak6 = kolada.get_latest_value("N18605")
        
        merit_trend = kolada.get_skolresultat_ak9(years=10)
        examen_trend = kolada.get_gymnasie_examen(years=10)
        merit_jamfor = kolada.compare_municipalities("N15413")
    
    # Grundskola
    st.subheader("📚 Grundskola - Årskurs 9")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if meritvarde:
            st.metric("Genomsnittligt meritvärde", f"{meritvarde['värde']:.1f}",
                     help=f"Elever i åk 9 ({meritvarde['år']})")
    
    with col2:
        if behoriga_yrke:
            st.metric("Behöriga till yrkesprogram", f"{behoriga_yrke['värde']:.1f}%",
                     help=f"Andel elever ({behoriga_yrke['år']})")
    
    with col3:
        if behoriga_estet:
            st.metric("Behöriga till estetiska pgm", f"{behoriga_estet['värde']:.1f}%",
                     help=f"Andel elever ({behoriga_estet['år']})")
    
    # Gymnasium
    st.subheader("🎓 Gymnasieskola")
    col4, col5 = st.columns(2)
    
    with col4:
        if examen_3ar:
            st.metric("Examen inom 3 år", f"{examen_3ar['värde']:.1f}%",
                     help=f"Gymnasieelever ({examen_3ar['år']})")
    
    with col5:
        if examen_4ar:
            st.metric("Examen inom 4 år", f"{examen_4ar['värde']:.1f}%",
                     help=f"Gymnasieelever ({examen_4ar['år']})")
    
    # Lågstadiet
    st.subheader("📖 Lågstadiet - Årskurs 6")
    col6, col7 = st.columns(2)
    
    with col6:
        if matematik_ak6:
            st.metric("Matematik - Minst E", f"{matematik_ak6['värde']:.1f}%",
                     help=f"Åk 6 ({matematik_ak6['år']})")
    
    with col7:
        if svenska_ak6:
            st.metric("Svenska - Minst E", f"{svenska_ak6['värde']:.1f}%",
                     help=f"Åk 6 ({svenska_ak6['år']})")
    
    # Trend
    st.subheader("📈 Utveckling meritvärde åk 9")
    if not merit_trend.empty:
        fig = px.line(merit_trend, x='år', y='värde', markers=True)
        fig.update_layout(xaxis_title="År", yaxis_title="Meritvärde", hovermode='x unified')
        fig.update_traces(line_color='#457B9D', marker=dict(size=8))
        st.plotly_chart(fig, use_container_width=True)

# ==================== FLIK 3: OMSORG & VÄLFÄRD ====================
with tab3:
    st.header("👶👵 Omsorg & Välfärd")
    st.markdown("**Barnomsorg, förskola och äldreomsorg**")
    
    with st.spinner("Hämtar omsorgsdata från Kolada..."):
        barn_forskola = kolada.get_latest_value("N15011")
        forskola_fungerar = kolada.get_latest_value("N00530")
        kostnad_forskola = kolada.get_latest_value("N03201")
        aldre_65 = kolada.get_latest_value("N00204")
        aldre_80 = kolada.get_latest_value("N00205")
        hemtjanst_65 = kolada.get_latest_value("N00911")
        sarskilt_65 = kolada.get_latest_value("N00910")
        hemtjanst_80 = kolada.get_latest_value("N00909")
        sarskilt_80 = kolada.get_latest_value("N00908")
        
        barn_trend = kolada.get_forskola_andel(years=10)
        hemtjanst_trend = kolada.get_aldreomsorg_hemtjanst(years=10)
    
    # Barnomsorg
    st.subheader("👶 Barnomsorg & Förskola")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if barn_forskola:
            st.metric("Barn 1-5 år i förskola", f"{barn_forskola['värde']:.1f}%",
                     help=f"Andel ({barn_forskola['år']})")
    
    with col2:
        if forskola_fungerar:
            st.metric("Förskolan fungerar bra", f"{forskola_fungerar['värde']:.1f}%",
                     help=f"Medborgarundersökning ({forskola_fungerar['år']})")
    
    with col3:
        if kostnad_forskola:
            st.metric("Kostnad förskola", f"{kostnad_forskola['värde']:,.0f} kr/inv",
                     help=f"Kr per inv 1-5 år ({kostnad_forskola['år']})")
    
    # Äldreomsorg
    st.subheader("👵 Äldreomsorg")
    col4, col5 = st.columns(2)
    
    with col4:
        if aldre_65:
            st.metric("Invånare 65+ år", f"{int(aldre_65['värde']):,}",
                     help=f"Antal ({aldre_65['år']})")
    
    with col5:
        if aldre_80:
            st.metric("Invånare 80+ år", f"{int(aldre_80['värde']):,}",
                     help=f"Antal ({aldre_80['år']})")
    
    st.subheader("📊 Omsorgsnivåer")
    col6, col7, col8, col9 = st.columns(4)
    
    with col6:
        if hemtjanst_65:
            st.metric("Hemtjänst 65+", f"{hemtjanst_65['värde']:.1f}%",
                     help=f"Andel ({hemtjanst_65['år']})")
    
    with col7:
        if sarskilt_65:
            st.metric("Särskilt boende 65+", f"{sarskilt_65['värde']:.1f}%",
                     help=f"Andel ({sarskilt_65['år']})")
    
    with col8:
        if hemtjanst_80:
            st.metric("Hemtjänst 80+", f"{hemtjanst_80['värde']:.1f}%",
                     help=f"Andel ({hemtjanst_80['år']})")
    
    with col9:
        if sarskilt_80:
            st.metric("Särskilt boende 80+", f"{sarskilt_80['värde']:.1f}%",
                     help=f"Andel ({sarskilt_80['år']})")
    
    # Trend
    if not hemtjanst_trend.empty:
        st.subheader("📈 Utveckling hemtjänst 65+")
        fig = px.line(hemtjanst_trend, x='år', y='värde', markers=True)
        fig.update_layout(xaxis_title="År", yaxis_title="Andel (%)", hovermode='x unified')
        fig.update_traces(line_color='#06A77D', marker=dict(size=8))
        st.plotly_chart(fig, use_container_width=True)

# ==================== FLIK 4: MILJÖ & HÅLLBARHET ====================
with tab4:
    st.header("🌱 Miljö & Hållbarhet")
    st.markdown("**Utsläpp, återvinning och hållbart resande**")
    
    with st.spinner("Hämtar miljödata från Kolada..."):
        miljoindex = kolada.get_latest_value("N00302")
        hallbarhet_index = kolada.get_latest_value("N00371")
        hallbart_resande = kolada.get_latest_value("N00974")
        atervinning = kolada.get_latest_value("N17425")
        vaxthusgas = kolada.get_latest_value("N00304")
        vaxthusgas_transport = kolada.get_latest_value("N00305")
        fornybar = kolada.get_latest_value("N07951")
        
        hallbart_trend = kolada.get_hallbart_resande(years=10)
        vaxthusgas_trend = kolada.get_vaxthusgas(years=10)
        atervinning_trend = kolada.get_atervinning(years=10)
    
    # Miljöindikatorer
    st.subheader("📊 Miljöindikatorer")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if miljoindex:
            st.metric("Miljökvalitet", f"{miljoindex['värde']:.1f}",
                     help=f"Kommunindex ({miljoindex['år']})")
    
    with col2:
        if hallbarhet_index:
            st.metric("Miljömässig hållbarhet", f"{hallbarhet_index['värde']:.1f}",
                     help=f"Kommunindex ({hallbarhet_index['år']})")
    
    with col3:
        if hallbart_resande:
            st.metric("Hållbart resande", f"{hallbart_resande['värde']:.1f}%",
                     help=f"Till arbetsplatsen ({hallbart_resande['år']})")
    
    with col4:
        if atervinning:
            st.metric("Återvinning", f"{atervinning['värde']:.1f}%",
                     help=f"Hushållsavfall ({atervinning['år']})")
    
    # Utsläpp
    st.subheader("💨 Utsläpp växthusgaser")
    col5, col6, col7 = st.columns(3)
    
    with col5:
        if vaxthusgas:
            st.metric("Totala utsläpp", f"{vaxthusgas['värde']:.2f}",
                     help=f"Ton CO₂-ekv/inv ({vaxthusgas['år']})")
    
    with col6:
        if vaxthusgas_transport:
            st.metric("Utsläpp transporter", f"{vaxthusgas_transport['värde']:.2f}",
                     help=f"Ton CO₂-ekv/inv ({vaxthusgas_transport['år']})")
    
    with col7:
        if vaxthusgas and vaxthusgas_transport:
            andel = (vaxthusgas_transport['värde'] / vaxthusgas['värde']) * 100
            st.metric("Andel från transporter", f"{andel:.1f}%",
                     help="Transporternas andel av totala utsläpp")
    
    # Trender
    st.subheader("📈 Utveckling över tid")
    
    tab_hallbart, tab_utslapp, tab_ater = st.tabs(["Hållbart resande", "Växthusgaser", "Återvinning"])
    
    with tab_hallbart:
        if not hallbart_trend.empty:
            fig = px.line(hallbart_trend, x='år', y='värde', markers=True,
                         title='Andel som reser hållbart till arbetsplatsen (%)')
            fig.update_layout(xaxis_title="År", yaxis_title="Andel (%)", hovermode='x unified')
            fig.update_traces(line_color='#38b000', marker=dict(size=8))
            st.plotly_chart(fig, use_container_width=True)
    
    with tab_utslapp:
        if not vaxthusgas_trend.empty:
            fig = px.line(vaxthusgas_trend, x='år', y='värde', markers=True,
                         title='Utsläpp växthusgaser totalt (ton CO₂-ekv/inv)')
            fig.update_layout(xaxis_title="År", yaxis_title="Ton CO₂-ekv/inv", hovermode='x unified')
            fig.update_traces(line_color='#dc2f02', marker=dict(size=8))
            st.plotly_chart(fig, use_container_width=True)
    
    with tab_ater:
        if not atervinning_trend.empty:
            fig = px.line(atervinning_trend, x='år', y='värde', markers=True,
                         title='Andel hushållsavfall som återvinns (%)')
            fig.update_layout(xaxis_title="År", yaxis_title="Andel (%)", hovermode='x unified')
            fig.update_traces(line_color='#588157', marker=dict(size=8))
            st.plotly_chart(fig, use_container_width=True)

# ==================== FLIK 5: KULTUR & FRITID ====================
with tab5:
    st.header("🎭 Kultur & Fritid")
    st.markdown("**Bibliotek, kulturaktiviteter och fritidsverksamhet**")
    
    with st.spinner("Hämtar kultur- och fritidsdata från Kolada..."):
        kultur_nojeslivs = kolada.get_latest_value("N00593")
        kultur_framja = kolada.get_latest_value("N00594")
        bibliotek_besok = kolada.get_latest_value("N11801")
        bibliotek_lan = kolada.get_latest_value("N11929")
        fritid_barn = kolada.get_latest_value("N00595")
        idrott_anlaggning = kolada.get_latest_value("N00596")
        kostnad_musikskola = kolada.get_latest_value("N09001")
        kostnad_kultur = kolada.get_latest_value("N09007")
        
        besok_trend = kolada.get_biblioteksbesok(years=10)
        lan_trend = kolada.get_bibliotekslan(years=10)
    
    # Medborgarupplevelse
    st.subheader("🗣️ Medborgarnas upplevelse")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if kultur_nojeslivs:
            st.metric("Kultur & nöjesliv bra", f"{kultur_nojeslivs['värde']:.1f}%",
                     help=f"Andel ({kultur_nojeslivs['år']})")
    
    with col2:
        if kultur_framja:
            st.metric("Kulturarbete bra", f"{kultur_framja['värde']:.1f}%",
                     help=f"Kommunens arbete ({kultur_framja['år']})")
    
    with col3:
        if fritid_barn:
            st.metric("Fritid barn & unga", f"{fritid_barn['värde']:.1f}%",
                     help=f"Nöjdhet ({fritid_barn['år']})")
    
    with col4:
        if idrott_anlaggning:
            st.metric("Idrottsanläggningar", f"{idrott_anlaggning['värde']:.1f}%",
                     help=f"Nöjdhet ({idrott_anlaggning['år']})")
    
    # Bibliotek
    st.subheader("📚 Biblioteksverksamhet")
    col5, col6 = st.columns(2)
    
    with col5:
        if bibliotek_besok:
            st.metric("Biblioteksbesök per invånare", f"{bibliotek_besok['värde']:.1f}",
                     help=f"Antal ({bibliotek_besok['år']})")
    
    with col6:
        if bibliotek_lan:
            st.metric("Bibliotekslån per invånare", f"{bibliotek_lan['värde']:.1f}",
                     help=f"Antal ({bibliotek_lan['år']})")
    
    # Trender
    st.subheader("📈 Utveckling över tid")
    
    tab_besok, tab_lan = st.tabs(["Biblioteksbesök", "Bibliotekslån"])
    
    with tab_besok:
        if not besok_trend.empty:
            fig = px.line(besok_trend, x='år', y='värde', markers=True,
                         title='Biblioteksbesök per invånare')
            fig.update_layout(xaxis_title="År", yaxis_title="Besök/inv", hovermode='x unified')
            fig.update_traces(line_color='#6a4c93', marker=dict(size=8))
            st.plotly_chart(fig, use_container_width=True)
    
    with tab_lan:
        if not lan_trend.empty:
            fig = px.line(lan_trend, x='år', y='värde', markers=True,
                         title='Bibliotekslån per invånare')
            fig.update_layout(xaxis_title="År", yaxis_title="Lån/inv", hovermode='x unified')
            fig.update_traces(line_color='#1982c4', marker=dict(size=8))
            st.plotly_chart(fig, use_container_width=True)
    
    # Kostnader
    st.subheader("💰 Kostnader")
    col7, col8 = st.columns(2)
    
    with col7:
        if kostnad_musikskola:
            st.metric("Musik & kulturskola", f"{kostnad_musikskola['värde']:,.0f} kr/inv",
                     help=f"Per inv 7-15 år ({kostnad_musikskola['år']})")
    
    with col8:
        if kostnad_kultur:
            st.metric("Allmän kulturverksamhet", f"{kostnad_kultur['värde']:,.0f} kr/inv",
                     help=f"Per invånare ({kostnad_kultur['år']})")
