import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
import requests
import json

# Lägg till current directory till Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ORTER

st.set_page_config(
    page_title="Karttjänst - Kungsbacka",
    page_icon="🗺️",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .map-header {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    .map-header h1 {
        color: white;
        margin: 0;
    }
    .area-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #11998e;
    }
    .area-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #11998e;
        margin-bottom: 0.5rem;
    }
    .info-badge {
        display: inline-block;
        background: #e8f5e9;
        color: #1b5e20;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.85rem;
        margin: 0.2rem;
        font-weight: 500;
    }
    .planning-info {
        background: #fff3e0;
        border-left: 4px solid #f57c00;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
        color: #333;
    }
    /* Fix light text on light background */
    .js-plotly-plot .plotly text {
        fill: #000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="map-header">
    <h1>🗺️ Karttjänst - Planering och Utveckling</h1>
    <p>Utforska Kungsbackas olika orter och områden med relevant information från översiktsplanen och statistik</p>
</div>
""", unsafe_allow_html=True)

# Information om orter med planeringsdata
ORTER_INFO = {
    "Kungsbacka stad": {
        "typ": "Huvudort (prioriterad)",
        "befolkning_ca": 45000,
        "planering": "Stark urban utveckling med förtätning i centrum. Nytt stationsområde planeras.",
        "utmaningar": "Trafik, parkeringsplatser, balansera tillväxt med grönområden",
        "utvecklingsområden": ["Stationsområdet", "Västra Kungsbacka", "Östra Kungsbacka"],
        "koordinater": [57.487, 12.075],
        "prioriterad": True
    },
    "Åsa": {
        "typ": "Prioriterad ort",
        "befolkning_ca": 3500,
        "planering": "Utveckling av bostäder och service för att stärka ortens roll som prioriterad ort.",
        "utmaningar": "Infrastruktur, kollektivtrafik, stärka ortens centrum",
        "utvecklingsområden": ["Åsa centrum", "Östra Åsa"],
        "koordinater": [57.407, 12.145],
        "prioriterad": True
    },
    "Fjärås": {
        "typ": "Ort",
        "befolkning_ca": 3500,
        "planering": "Varsam utveckling med hänsyn till natur och kulturmiljö.",
        "utmaningar": "Bevara karaktär samtidigt som service stärks",
        "utvecklingsområden": ["Fjärås centrum"],
        "koordinater": [57.417, 12.083],
        "prioriterad": False
    },
    "Onsala": {
        "typ": "Ort",
        "befolkning_ca": 14000,
        "planering": "Utveckling av hållbar kustbebyggelse. Fokus på kollektivtrafik.",
        "utmaningar": "Högt exploateringstryck, värna kustmiljö och grönområden",
        "utvecklingsområden": ["Onsala centrum", "Gottskär"],
        "koordinater": [57.402, 11.973],
        "prioriterad": False
    },
    "Kullavik": {
        "typ": "Ort",
        "befolkning_ca": 4500,
        "planering": "Komplettering av bostäder med hänsyn till kustläge och natur.",
        "utmaningar": "Begränsat utrymme, bevara karaktär",
        "utvecklingsområden": ["Kullavik centrum"],
        "koordinater": [57.420, 11.934],
        "prioriterad": False
    },
    "Särö": {
        "typ": "Ort",
        "befolkning_ca": 3000,
        "planering": "Exklusiv kustort med fokus på att bevara miljö och karaktär.",
        "utmaningar": "Högt exploateringstryck, begränsad mark, bevara kustmiljö",
        "utvecklingsområden": ["Särö centrum"],
        "koordinater": [57.446, 11.941],
        "prioriterad": False
    },
    "Vallda": {
        "typ": "Ort",
        "befolkning_ca": 1500,
        "planering": "Kompletterande bebyggelse i anslutning till befintlig ort.",
        "utmaningar": "Gles bebyggelse, serviceutbud",
        "utvecklingsområden": ["Vallda centrum"],
        "koordinater": [57.460, 12.130],
        "prioriterad": False
    },
    "Frillesås": {
        "typ": "Ort",
        "befolkning_ca": 1200,
        "planering": "Bevara småortskaraktär, komplettering med mindre bostadsområden.",
        "utmaningar": "Kollektivtrafik, service",
        "utvecklingsområden": ["Frillesås centrum"],
        "koordinater": [57.379, 12.111],
        "prioriterad": False
    },
    "Anneberg": {
        "typ": "Prioriterad ort",
        "befolkning_ca": 800,
        "planering": "Prioriterad ort med varsam komplettering av bostäder och service.",
        "utmaningar": "Utveckla service, förbättra kollektivtrafik",
        "utvecklingsområden": ["Anneberg centrum", "Älafors", "Lerberg"],
        "koordinater": [57.320, 12.180],
        "prioriterad": True
    }
}

# Skapa karta med orter
st.subheader("📍 Kungsbacka kommun - Orter och utvecklingsområden")

# Förklaring av ortstruktur
with st.expander("ℹ️ Om Kungsbackas ortstruktur"):
    st.markdown("""
    **Kungsbacka kommun består av:**
    
    - **1 Huvudort (prioriterad):** Kungsbacka stad (ca 45,000 invånare)
    - **2 Prioriterade orter:** Åsa och Anneberg
    - **6 Övriga orter:** Kullavik, Särö, Vallda, Onsala, Frillesås och Fjärås
    
    **Färgkodning på kartan:**
    - 🟤 **Mörk orange** = Prioriterade orter (Kungsbacka stad, Åsa, Anneberg)
    - 🟠 **Orange** = Övriga orter
    
    **Vad betyder "prioriterad ort"?**
    
    Kungsbacka stad, Åsa och Anneberg är utpekade som prioriterade orter i översiktsplanen. Det innebär att dessa orter 
    har särskild betydelse för kommunens utveckling och får prioritet när det gäller:
    - Utbyggnad av service och kommersiell verksamhet
    - Kollektivtrafikförbindelser
    - Utveckling av bostäder och offentlig service
    
    Målet är att stärka dessa orter så att de kan erbjuda god service till både boende i orten 
    och omkringliggande landsbygdsområden.
    """)


# Förbered data för kartan
map_data = []
for ort, info in ORTER_INFO.items():
    map_data.append({
        'Ort': ort,
        'Typ': info['typ'],
        'Befolkning': info['befolkning_ca'],
        'Lat': info['koordinater'][0],
        'Lon': info['koordinater'][1],
        'Info': f"{ort} ({info['typ']})<br>Ca {info['befolkning_ca']:,} invånare"
    })

df_map = pd.DataFrame(map_data)

# Läs in ortgränserna från GeoJSON
try:
    with open('/workspaces/indikator-dashboard/data/orter_avgransningar.geojson', 'r') as f:
        orter_geojson = json.load(f)
except FileNotFoundError:
    orter_geojson = None

# Skapa interaktiv karta med ortgränser
fig = go.Figure()

# Lägg till ortgränser som polygoner
if orter_geojson:
    for feature in orter_geojson['features']:
        ort_namn = feature['properties']['ort']
        ort_info = ORTER_INFO.get(ort_namn, {})
        is_prioriterad = ort_info.get('prioriterad', False)
        
        # Färg baserat på prioritering
        color = '#d84315' if is_prioriterad else '#ff9800'
        
        # Lägg till polygon
        coords = feature['geometry']['coordinates'][0]
        lats = [c[1] for c in coords]
        lons = [c[0] for c in coords]
        
        fig.add_trace(go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode='lines',
            line=dict(width=2, color=color),
            fill='toself',
            fillcolor=color,
            opacity=0.15,
            name=ort_namn,
            hoverinfo='text',
            hovertext=f"{ort_namn}<br>{ort_info.get('typ', 'Ort')}<br>Ca {ort_info.get('befolkning_ca', 0):,} invånare",
            showlegend=False
        ))

# Lägg till punkter för orterna (ovanpå polygonerna)
fig.add_trace(go.Scattermapbox(
    lat=df_map['Lat'],
    lon=df_map['Lon'],
    mode='markers+text',
    marker=dict(
        size=df_map['Befolkning'] / 500,
        color=['#d84315' if 'prioriterad' in typ.lower() else '#ff9800' for typ in df_map['Typ']],
        opacity=0.9
    ),
    text=df_map['Ort'],
    textposition='top center',
    textfont=dict(size=10, color='#000', family='Arial, sans-serif'),
    hoverinfo='text',
    hovertext=[f"{row['Ort']}<br>{row['Typ']}<br>Ca {row['Befolkning']:,} invånare" 
               for _, row in df_map.iterrows()],
    showlegend=False
))

fig.update_layout(
    mapbox=dict(
        style="open-street-map",
        center=dict(lat=57.45, lon=12.05),
        zoom=10
    ),
    height=600,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# Urval av ort
st.markdown("---")
st.subheader("🏘️ Välj ort för detaljerad information")

selected_ort = st.selectbox(
    "Välj ort:",
    list(ORTER_INFO.keys()),
    index=0
)

if selected_ort:
    info = ORTER_INFO[selected_ort]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="area-card">
            <div class="area-title">{selected_ort}</div>
            <span class="info-badge">{info['typ']}</span>
            <span class="info-badge">Ca {info['befolkning_ca']:,} invånare</span>
            {f'<span class="info-badge" style="background: #fff3e0; color: #f57c00; font-weight: 600;">⭐ Prioriterad ort</span>' if info['prioriterad'] else ''}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="planning-info">
            <h4>📋 Planering och utveckling</h4>
            <p>{info['planering']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**⚠️ Utmaningar:**")
        st.write(info['utmaningar'])
        
        st.markdown("**🏗️ Utvecklingsområden:**")
        for område in info['utvecklingsområden']:
            st.write(f"- {område}")
    
    with col2:
        st.markdown("### 🔗 Relaterade dokument")
        
        st.markdown("""
        <div style="background: #f5f5f5; padding: 1rem; border-radius: 8px;">
            <h4 style="margin-top: 0;">Översiktsplanen</h4>
            <p style="font-size: 0.9rem;">Se detaljerad information om utveckling och planering för detta område.</p>
        """, unsafe_allow_html=True)
        
        if st.button(f"📖 Läs mer om {selected_ort} i översiktsplanen", key="op_link"):
            st.info(f"Öppnar översiktsplanen för {selected_ort}...")
            st.markdown("[Gå till översiktsplanen](https://karta.kungsbacka.se/oversiktsplan)", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Visa eventell statistik för området om tillgänglig
        st.markdown("### 📊 Statistik")
        st.info("Statistik på ortnivå kommer från SCB och översiktsplanen")

# Länk till översiktsplanekartan
st.markdown("---")
st.subheader("🗺️ Fullständig översiktsplanekarta")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Interaktiv översiktsplanekarta
    
    För mer detaljerad kartinformation och planeringsdokument, besök kommunens officiella översiktsplanekarta.
    
    Här kan du:
    - Se detaljerade planer för olika områden
    - Läsa om markanvändning och restriktioner
    - Hitta information om framtida utvecklingsområden
    - Ta del av underlagskartor
    """)
    
    st.markdown("""
    <a href="https://karta.kungsbacka.se/oversiktsplan" target="_blank" 
       style="display: inline-block; background: #11998e; color: white; padding: 0.8rem 1.5rem; 
              border-radius: 6px; text-decoration: none; font-weight: 500;">
        🗺️ Öppna översiktsplanekartan
    </a>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    ### Tillgängliga kartlager
    
    I översiktsplanekartan hittar du bland annat:
    
    - **Markanvändning** - Hur mark planeras användas
    - **Utvecklingsområden** - Framtida utbyggnadsområden
    - **Grönstruktur** - Parker, naturområden
    - **Infrastruktur** - Vägar, kollektivtrafik
    - **Riksintressen** - Skyddade områden
    - **Kulturmiljö** - Bevarandevärda miljöer
    """)

# Extra funktioner
st.markdown("---")
st.subheader("📈 Jämför orter")

col1, col2 = st.columns(2)

with col1:
    ort1 = st.selectbox("Välj första ort:", list(ORTER_INFO.keys()), key="ort1")

with col2:
    ort2 = st.selectbox("Välj andra ort:", list(ORTER_INFO.keys()), index=1, key="ort2")

if ort1 and ort2:
    st.markdown("### Jämförelse")
    
    comp_col1, comp_col2, comp_col3 = st.columns(3)
    
    with comp_col1:
        st.metric("Befolkning", 
                 f"{ORTER_INFO[ort1]['befolkning_ca']:,}",
                 delta=f"{ORTER_INFO[ort1]['befolkning_ca'] - ORTER_INFO[ort2]['befolkning_ca']:,} vs {ort2}")
    
    with comp_col2:
        st.metric(ort1, ORTER_INFO[ort1]['typ'])
    
    with comp_col3:
        st.metric(ort2, ORTER_INFO[ort2]['typ'])
    
    # Jämförelse i tabell
    comp_df = pd.DataFrame({
        'Aspekt': ['Typ', 'Befolkning (ca)', 'Antal utvecklingsområden'],
        ort1: [
            ORTER_INFO[ort1]['typ'],
            f"{ORTER_INFO[ort1]['befolkning_ca']:,}",
            len(ORTER_INFO[ort1]['utvecklingsområden'])
        ],
        ort2: [
            ORTER_INFO[ort2]['typ'],
            f"{ORTER_INFO[ort2]['befolkning_ca']:,}",
            len(ORTER_INFO[ort2]['utvecklingsområden'])
        ]
    })
    
    st.dataframe(comp_df, use_container_width=True, hide_index=True)
