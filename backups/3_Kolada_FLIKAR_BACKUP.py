"""
Kolada - Kommunala Nyckeltal
Analys från Sveriges största databas för kommunal statistik
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.kolada_connector import KoladaConnector

st.set_page_config(page_title="Kolada", page_icon="📊", layout="wide")

st.title("📊 Kolada - Kommunala Nyckeltal")
st.markdown("**Analys från Sveriges största databas för kommunal statistik**")

# Initialisera Kolada
kolada = KoladaConnector()

# === FLIKAR FÖR OLIKA KATEGORIER ===
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
            st.metric("Förvärvsarbetande 20-64 år", f"{sysselsattning['värde']:.1f}%", 
                     help=f"Data från {sysselsattning['år']}")
        else:
            st.metric("Förvärvsarbetande 20-64 år", "N/A")
    
    with col2:
        if arbetslosa:
            st.metric("Arbetslösa eller i åtgärd", f"{arbetslosa['värde']:.1f}%",
                     help=f"Data från {arbetslosa['år']}")
        else:
            st.metric("Arbetslösa eller i åtgärd", "N/A")
    
    with col3:
        if nystartade:
            st.metric("Nystartade arbetsställen", f"{nystartade['värde']:.1f}",
                     help=f"Antal per 1000 inv 16-64 år ({nystartade['år']})")
        else:
            st.metric("Nystartade arbetsställen", "N/A")
    
    with col4:
        if sysselsatta_antal:
            st.metric("Sysselsatta totalt", f"{int(sysselsatta_antal['värde']):,}",
                     help=f"Antal sysselsatta ({sysselsatta_antal['år']})")
        else:
            st.metric("Sysselsatta totalt", "N/A")
    
    # Trender
    st.subheader("📈 Trender över tid")
    tab_syss, tab_arblos = st.tabs(["Sysselsättning", "Arbetslöshet"])
    
    with tab_syss:
        if not syss_trend.empty:
            fig = px.line(syss_trend, x='år', y='värde', 
                         title='Förvärvsarbetande 20-64 år, andel (%)', markers=True)
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
                         title='Arbetslösa eller i åtgärd minst en dag, 16-64 år (%)', markers=True)
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
        
        fig = go.Figure(data=[go.Bar(x=syss_jamfor_sorted['kommun_namn'], y=syss_jamfor_sorted['värde'],
                                     marker_color=colors, text=syss_jamfor_sorted['värde'].round(1),
                                     textposition='outside')])
        fig.update_layout(title=f"Förvärvsarbetande 20-64 år ({syss_jamfor_sorted['år'].iloc[0]})",
                         xaxis_title="Kommun", yaxis_title="Andel (%)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ==================== FLIK 2: UTBILDNING ====================
with tab2:
    st.header("🎓 Utbildning & Skola")
    st.markdown("**Skolresultat, gymnasieexamen och utbildningskvalitet**")
    
    with st.spinner("Hämtar utbildningsdata från Kolada..."):
        meritvarde = kolada.get_latest_value("N15413")
        behoriga_yrke = kolada.get_latest_value("N15446")
        examen_3ar = kolada.get_latest_value("N15533")
        
        merit_trend = kolada.get_skolresultat_ak9(years=10)
        examen_trend = kolada.get_gymnasie_examen(years=10)
        merit_jamfor = kolada.compare_municipalities("N15413")
    
    # Nyckeltal
    st.subheader("📚 Grundskola - Årskurs 9")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if meritvarde:
            st.metric("Genomsnittligt meritvärde", f"{meritvarde['värde']:.1f}",
                     help=f"Data från {meritvarde['år']}")
    
    with col2:
        if behoriga_yrke:
            st.metric("Behöriga till yrkesprogram", f"{behoriga_yrke['värde']:.1f}%",
                     help=f"Data från {behoriga_yrke['år']}")
    
    with col3:
        if examen_3ar:
            st.metric("Gymnasieexamen inom 3 år", f"{examen_3ar['värde']:.1f}%",
                     help=f"Data från {examen_3ar['år']}")
    
    # Trender
    st.subheader("📈 Utveckling över tid")
    if not merit_trend.empty:
        fig = px.line(merit_trend, x='år', y='värde',
                     title='Genomsnittligt meritvärde årskurs 9', markers=True)
        fig.update_layout(xaxis_title="År", yaxis_title="Meritvärde", hovermode='x unified')
        fig.update_traces(line_color='#457B9D', marker=dict(size=8))
        st.plotly_chart(fig, use_container_width=True)
    
    # Jämförelse
    st.subheader("🔄 Jämförelse med andra kommuner")
    if not merit_jamfor.empty:
        merit_jamfor_sorted = merit_jamfor.sort_values('värde', ascending=False)
        colors = ['#457B9D' if x == 'Kungsbacka' else '#A8DADC' for x in merit_jamfor_sorted['kommun_namn']]
        
        fig = go.Figure(data=[go.Bar(x=merit_jamfor_sorted['kommun_namn'], y=merit_jamfor_sorted['värde'],
                                     marker_color=colors, text=merit_jamfor_sorted['värde'].round(1),
                                     textposition='outside')])
        fig.update_layout(title=f"Genomsnittligt meritvärde åk 9 ({merit_jamfor_sorted['år'].iloc[0]})",
                         xaxis_title="Kommun", yaxis_title="Meritvärde", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ==================== FLIK 3: OMSORG & VÄLFÄRD ====================
with tab3:
    st.header("👶👵 Omsorg & Välfärd")
    st.markdown("**Barnomsorg, förskola och äldreomsorg**")
    
    with st.spinner("Hämtar omsorgsdata från Kolada..."):
        barn_forskola = kolada.get_latest_value("N15011")
        aldre_65 = kolada.get_latest_value("N00204")
        hemtjanst_65 = kolada.get_latest_value("N00911")
        sarskilt_65 = kolada.get_latest_value("N00910")
        
        barn_trend = kolada.get_forskola_andel(years=10)
        hemtjanst_trend = kolada.get_aldreomsorg_hemtjanst(years=10)
    
    # Barnomsorg
    st.subheader("👶 Barnomsorg & Förskola")
    col1, col2 = st.columns(2)
    
    with col1:
        if barn_forskola:
            st.metric("Barn 1-5 år i förskola", f"{barn_forskola['värde']:.1f}%",
                     help=f"Data från {barn_forskola['år']}")
    
    # Äldreomsorg
    st.subheader("👵 Äldreomsorg")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        if aldre_65:
            st.metric("Invånare 65+ år", f"{int(aldre_65['värde']):,}",
                     help=f"Data från {aldre_65['år']}")
    
    with col4:
        if hemtjanst_65:
            st.metric("Hemtjänst 65+", f"{hemtjanst_65['värde']:.1f}%",
                     help=f"Data från {hemtjanst_65['år']}")
    
    with col5:
        if sarskilt_65:
            st.metric("Särskilt boende 65+", f"{sarskilt_65['värde']:.1f}%",
                     help=f"Data från {sarskilt_65['år']}")
    
    # Trender
    st.subheader("📈 Utveckling över tid")
    if not barn_trend.empty:
        fig = px.line(barn_trend, x='år', y='värde',
                     title='Barn 1-5 år i förskola, andel (%)', markers=True)
        fig.update_layout(xaxis_title="År", yaxis_title="Andel (%)", hovermode='x unified')
        fig.update_traces(line_color='#F77F00', marker=dict(size=8))
        st.plotly_chart(fig, use_container_width=True)

# ==================== FLIK 4: MILJÖ & HÅLLBARHET ====================
with tab4:
    st.header("🌱 Miljö & Hållbarhet")
    st.markdown("**Utsläpp, återvinning och hållbart resande**")
    
    with st.spinner("Hämtar miljödata från Kolada..."):
        miljoindex = kolada.get_latest_value("N00302")
        hallbart_resande = kolada.get_latest_value("N00974")
        vaxthusgas = kolada.get_latest_value("N00304")
        atervinning = kolada.get_latest_value("N17425")
        
        vaxthusgas_trend = kolada.get_vaxthusgas(years=10)
        atervinning_trend = kolada.get_atervinning(years=10)
    
    # Nyckeltal
    st.subheader("📊 Miljöindikatorer")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if miljoindex:
            st.metric("Miljökvalitet", f"{miljoindex['värde']:.1f}",
                     help=f"Kommunindex ({miljoindex['år']})")
    
    with col2:
        if hallbart_resande:
            st.metric("Hållbart resande", f"{hallbart_resande['värde']:.1f}%",
                     help=f"Data från {hallbart_resande['år']}")
    
    with col3:
        if vaxthusgas:
            st.metric("Växthusgaser", f"{vaxthusgas['värde']:.2f}",
                     help=f"Ton CO₂-ekv/inv ({vaxthusgas['år']})")
    
    with col4:
        if atervinning:
            st.metric("Återvinning", f"{atervinning['värde']:.1f}%",
                     help=f"Data från {atervinning['år']}")
    
    # Trender
    st.subheader("📈 Utveckling över tid")
    if not vaxthusgas_trend.empty:
        fig = px.line(vaxthusgas_trend, x='år', y='värde',
                     title='Utsläpp växthusgaser totalt (ton CO₂-ekv/inv)', markers=True)
        fig.update_layout(xaxis_title="År", yaxis_title="Ton CO₂-ekv per invånare", hovermode='x unified')
        fig.update_traces(line_color='#dc2f02', marker=dict(size=8))
        st.plotly_chart(fig, use_container_width=True)
        
        if len(vaxthusgas_trend) >= 2:
            forsta = vaxthusgas_trend.iloc[0]['värde']
            senaste = vaxthusgas_trend.iloc[-1]['värde']
            forandring = senaste - forsta
            emoji = "🟢" if forandring < 0 else "🔴"
            minskning_procent = ((senaste - forsta) / forsta) * 100 if forsta > 0 else 0
            st.info(f"{emoji} **Förändring:** {forsta:.2f} ({vaxthusgas_trend.iloc[0]['år']}) → {senaste:.2f} ({vaxthusgas_trend.iloc[-1]['år']}) = **{forandring:+.2f}** ({minskning_procent:+.1f}%)")

# ==================== FLIK 5: KULTUR & FRITID ====================
with tab5:
    st.header("🎭 Kultur & Fritid")
    st.markdown("**Bibliotek, kulturaktiviteter och fritidsverksamhet**")
    
    with st.spinner("Hämtar kultur- och fritidsdata från Kolada..."):
        kultur_nojeslivs = kolada.get_latest_value("N00593")
        bibliotek_besok = kolada.get_latest_value("N11801")
        bibliotek_lan = kolada.get_latest_value("N11929")
        
        besok_trend = kolada.get_biblioteksbesok(years=10)
        lan_trend = kolada.get_bibliotekslan(years=10)
    
    # Nyckeltal
    st.subheader("🗣️ Medborgarnas upplevelse")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if kultur_nojeslivs:
            st.metric("Kultur & nöjesliv bra", f"{kultur_nojeslivs['värde']:.1f}%",
                     help=f"Data från {kultur_nojeslivs['år']}")
    
    with col2:
        if bibliotek_besok:
            st.metric("Biblioteksbesök per inv", f"{bibliotek_besok['värde']:.1f}",
                     help=f"Data från {bibliotek_besok['år']}")
    
    with col3:
        if bibliotek_lan:
            st.metric("Bibliotekslån per inv", f"{bibliotek_lan['värde']:.1f}",
                     help=f"Data från {bibliotek_lan['år']}")
    
    # Trender
    st.subheader("📈 Utveckling över tid")
    if not besok_trend.empty:
        fig = px.line(besok_trend, x='år', y='värde',
                     title='Biblioteksbesök per invånare', markers=True)
        fig.update_layout(xaxis_title="År", yaxis_title="Besök per invånare", hovermode='x unified')
        fig.update_traces(line_color='#6a4c93', marker=dict(size=8))
        st.plotly_chart(fig, use_container_width=True)

# === DATAKÄLLA ===
st.markdown("---")
st.caption("📊 **Datakälla:** Kolada - Sveriges största databas för kommunala nyckeltal | Uppdateras automatiskt var 7:e dag")
