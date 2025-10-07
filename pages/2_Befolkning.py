"""
Befolkningsanalys - SCB Data med befolkningsförändringar
"""

import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.scb_connector import SCBConnector

st.set_page_config(page_title="Befolkning - Kungsbacka", page_icon="�", layout="wide")

st.title("� Befolkningsförändringar")
st.markdown("*Analys av befolkningsutveckling och dess komponenter*")

scb = SCBConnector()

# Testa API
pop_change = pd.DataFrame()
api_works = False

try:
    with st.spinner("Hämtar befolkningsförändringar..."):
        pop_change = scb.get_population_change()
    
    if not pop_change.empty:
        st.success("✅ SCB Befolkningsförändringar ansluten")
        api_works = True
    else:
        st.warning("⚠️ Befolkningsförändringsdata inte tillgänglig för närvarande")
except Exception as e:
    st.warning(f"⚠️ Kunde inte hämta befolkningsförändringar: {e}")

st.markdown("---")

if not api_works or pop_change.empty:
    st.info("""
    ### 📊 Befolkningsförändringsdata
    
    Denna sida är förberedd för att visa:
    
    **Naturlig befolkningsförändring:**
    - 👶 **Levande födda** per år
    - ⚰️ **Döda** per år
    - 📊 **Naturlig folkökning** (födda - döda)
    
    **Flyttningar:**
    - ➡️ **Inflyttade** (från andra kommuner/länder)
    - ⬅️ **Utflyttade** (till andra kommuner/länder)  
    - 🔄 **Flyttnetto** (inflyttade - utflyttade)
    
    **Total folkökning:**
    - 📈 **Folkökning totalt** = Naturlig folkökning + Flyttnetto
    
    ---
    
    **Varför visas ingen data?**
    
    SCB's API för befolkningsförändringar kunde inte nås just nu. 
    Denna data kan finnas tillgänglig via:
    - SCB's statistikdatabas (manuell nedladdning)
    - Kolada API (har vissa flyttningsstatistik)
    - Direkt från kommunens befolkningsregister
    
    **Alternativ datakälla:**
    
    Vi kan istället beräkna **uppskattad folkökning** från befolkningsdata vi redan har:
    """)
    
    st.markdown("---")
    
    # Visa uppskattad folkökning från befolkningsdata
    st.subheader("📈 Beräknad befolkningsutveckling")
    
    with st.spinner("Beräknar från tillgänglig data..."):
        pop_total = scb.get_population_total()
    
    if not pop_total.empty:
        yearly = pop_total.groupby('År')['Antal'].sum().reset_index()
        yearly['Förändring'] = yearly['Antal'].diff()
        yearly['Förändring %'] = yearly['Antal'].pct_change() * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            latest = yearly.iloc[-1]
            st.metric("📊 Befolkning " + str(int(latest['År'])), 
                     f"{int(latest['Antal']):,}".replace(",", " "))
        
        with col2:
            if pd.notna(latest['Förändring']):
                st.metric("📈 Förändring från föregående år", 
                         f"{int(latest['Förändring']):+,}".replace(",", " "),
                         f"{latest['Förändring %']:+.1f}%")
        
        with col3:
            avg_change = yearly['Förändring'].dropna().mean()
            st.metric("📊 Genomsnittlig tillväxt/år", 
                     f"{int(avg_change):+,}".replace(",", " "))
        
        # Diagram
        fig = px.bar(yearly[yearly['Förändring'].notna()], 
                    x='År', y='Förändring',
                    title='Årlig befolkningsförändring (beräknad från folkmängd)',
                    labels={'Förändring': 'Förändring antal personer', 'År': 'År'},
                    color='Förändring',
                    color_continuous_scale=['red', 'yellow', 'green'])
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **💡 Notera:** Denna graf visar total befolkningsförändring men kan inte visa uppdelning på:
        - Födda vs Döda (naturlig förändring)
        - Inflyttade vs Utflyttade (flyttnetto)
        
        För mer detaljerad statistik, kontakta Kungsbacka kommun direkt eller använd Kolada för vissa flyttningsdata.
        """)
        
    st.markdown("---")
    
    # Länk till alternativa källor
    st.subheader("🔗 Alternativa datakällor")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **SCB Statistikdatabasen:**
        - [Befolkningsstatistik](https://www.statistikdatabasen.scb.se/pxweb/sv/ssd/)
        - Sök på tabell "BE0101"
        - Manuell nedladdning möjlig
        """)
    
    with col2:
        st.markdown("""
        **Kolada - Öppna Jämförelser:**
        - [Kolada.se](https://www.kolada.se)
        - KPI N00975: Inrikes flyttningsnetto
        - KPI N00976: Utrikes flyttningsnetto
        """)
    
    st.stop()  # Stoppa här om ingen data

# === DATA FINNS - VISA FULLSTÄNDIG ANALYS ===

# HUVUDMETRICS
st.subheader("📊 Senaste året")

latest_year = pop_change['År'].max()
latest_data = pop_change[pop_change['År'] == latest_year]

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    fodda = latest_data[latest_data['Typ'] == 'Födda']['Antal'].sum()
    st.metric("👶 Födda", f"{fodda}")

with col2:
    doda = latest_data[latest_data['Typ'] == 'Döda']['Antal'].sum()
    st.metric("⚰️ Döda", f"{doda}")

with col3:
    inflytt = latest_data[latest_data['Typ'] == 'Inflyttade']['Antal'].sum()
    st.metric("➡️ Inflyttade", f"{inflytt}")

with col4:
    utflytt = latest_data[latest_data['Typ'] == 'Utflyttade']['Antal'].sum()
    st.metric("⬅️ Utflyttade", f"{utflytt}")

with col5:
    folkokning = latest_data[latest_data['Typ'] == 'Folkökning']['Antal'].sum()
    color = "normal" if folkokning >= 0 else "inverse"
    st.metric("📈 Folkökning", f"{folkokning:+d}")

st.markdown("---")

# UTVECKLING ÖVER TID
st.subheader("📈 Utveckling över tid (5 år)")

fig = px.line(pop_change, x='År', y='Antal', color='Typ',
              markers=True,
              title='Befolkningsförändringar per år',
              labels={'Antal': 'Antal personer', 'År': 'År'})
fig.update_layout(hovermode='x unified', height=500)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# FLYTTNETTO
st.subheader("🔄 Flyttnetto (Inflyttade - Utflyttade)")

# Beräkna flyttnetto per år
flyttnetto_data = []
for year in sorted(pop_change['År'].unique()):
    year_data = pop_change[pop_change['År'] == year]
    inflytt = year_data[year_data['Typ'] == 'Inflyttade']['Antal'].sum()
    utflytt = year_data[year_data['Typ'] == 'Utflyttade']['Antal'].sum()
    netto = inflytt - utflytt
    flyttnetto_data.append({'År': year, 'Flyttnetto': netto})

flyttnetto_df = pd.DataFrame(flyttnetto_data)

if not flyttnetto_df.empty:
    fig = px.bar(flyttnetto_df, x='År', y='Flyttnetto',
                 title='Flyttnetto per år (Positiv = fler inflyttade)',
                 labels={'Flyttnetto': 'Antal personer (netto)', 'År': 'År'},
                 color='Flyttnetto',
                 color_continuous_scale=['red', 'yellow', 'green'])
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# NATURLIG FOLKÖKNING
st.subheader("� Naturlig folkökning (Födda - Döda)")

# Beräkna naturlig folkökning per år
naturlig_data = []
for year in sorted(pop_change['År'].unique()):
    year_data = pop_change[pop_change['År'] == year]
    fodda = year_data[year_data['Typ'] == 'Födda']['Antal'].sum()
    doda = year_data[year_data['Typ'] == 'Döda']['Antal'].sum()
    naturlig = fodda - doda
    naturlig_data.append({'År': year, 'Naturlig folkökning': naturlig})

naturlig_df = pd.DataFrame(naturlig_data)

if not naturlig_df.empty:
    fig = px.bar(naturlig_df, x='År', y='Naturlig folkökning',
                 title='Naturlig folkökning per år',
                 labels={'Naturlig folkökning': 'Antal personer', 'År': 'År'},
                 color='Naturlig folkökning',
                 color_continuous_scale=['red', 'yellow', 'green'])
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# KOMPONENTER I FOLKÖKNING
st.subheader("📊 Komponenter i folkökningen")

if not flyttnetto_df.empty and not naturlig_df.empty:
    combined = flyttnetto_df.merge(naturlig_df, on='År')
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=combined['År'], y=combined['Flyttnetto'], 
                         name='Flyttnetto', marker_color='lightblue'))
    fig.add_trace(go.Bar(x=combined['År'], y=combined['Naturlig folkökning'], 
                         name='Naturlig folkökning', marker_color='lightgreen'))
    
    fig.update_layout(
        title='Komponenter i folkökningen',
        xaxis_title='År',
        yaxis_title='Antal personer',
        barmode='stack',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Analys
    col1, col2 = st.columns(2)
    
    with col1:
        avg_flyttnetto = flyttnetto_df['Flyttnetto'].mean()
        st.metric("📍 Snitt flyttnetto", f"{avg_flyttnetto:+.0f}/år")
    
    with col2:
        avg_naturlig = naturlig_df['Naturlig folkökning'].mean()
        st.metric("👶 Snitt naturlig folkökning", f"{avg_naturlig:+.0f}/år")

# RÅDATA
with st.expander("📋 Rådata"):
    st.dataframe(pop_change, use_container_width=True)
    st.caption(f"Källa: SCB, hämtad {datetime.now().strftime('%Y-%m-%d %H:%M')}")

