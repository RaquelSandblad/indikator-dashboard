"""
Sida för ortspecifik analys
Visar data och utvecklingspotential för olika orter i Kungsbacka kommun
"""

import streamlit as st
import sys
import os

# Lägg till projektets rotkatalog i Python-sökvägen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Ortanalys - Kungsbacka",
    page_icon="📍",
    layout="wide"
)

st.title("📍 Analys per ort")

# ALLA 9 ORTER från översiktsplanen
ORTER = {
    "Kungsbacka stad": {
        "befolkning": 45000, 
        "lat": 57.4879, 
        "lon": 12.0756,
        "typ": "Huvudort (prioriterad)",
        "beskrivning": "Kommunens huvudort och största tätort med bred service och goda kommunikationer."
    },
    "Åsa": {
        "befolkning": 8900, 
        "lat": 57.3667, 
        "lon": 12.1333,
        "typ": "Prioriterad ort",
        "beskrivning": "Kustsamhälle med egen stadskärna, skolor och tågstation."
    },
    "Fjärås": {
        "befolkning": 3500, 
        "lat": 57.4167, 
        "lon": 12.0833,
        "typ": "Prioriterad ort",
        "beskrivning": "Tätort med tågstation längs Västkustbanan, bra pendlingsmöjligheter."
    },
    "Onsala": {
        "befolkning": 14000, 
        "lat": 57.4833, 
        "lon": 11.9167,
        "typ": "Ort",
        "beskrivning": "Stor kustort med skärgårdsmiljö, populärt bostadsområde."
    },
    "Kullavik": {
        "befolkning": 4500, 
        "lat": 57.4667, 
        "lon": 11.9500,
        "typ": "Ort",
        "beskrivning": "Kustort med närhet till Onsala och Särö, växande bostadsområde."
    },
    "Särö": {
        "befolkning": 3000, 
        "lat": 57.5167, 
        "lon": 11.9333,
        "typ": "Ort",
        "beskrivning": "Kustort med badstränder och rekreationsmöjligheter, attraktivt läge."
    },
    "Vallda": {
        "befolkning": 1500, 
        "lat": 57.3800, 
        "lon": 12.2800,
        "typ": "Ort",
        "beskrivning": "Mindre tätort i kommunens östra delar, lantlig karaktär."
    },
    "Frillesås": {
        "befolkning": 1200, 
        "lat": 57.3500, 
        "lon": 12.2333,
        "typ": "Ort",
        "beskrivning": "Landsbygdsort med grundskola och lokal service."
    },
    "Anneberg": {
        "befolkning": 800, 
        "lat": 57.3200, 
        "lon": 12.1800,
        "typ": "Ort",
        "beskrivning": "Mindre ort i södra delen av kommunen, nära Åsa."
    }
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
            "Orttyp",
            locality_data['typ'],
            help="Enligt översiktsplanen"
        )
    
    with col3:
        # Beräkna andel av kommunens befolkning
        total_kommun = 85792  # Kungsbacka totalt (2024)
        andel = (locality_data["befolkning"] / total_kommun) * 100
        st.metric(
            "Andel av kommunen",
            f"{andel:.1f}%",
            help=f"Av totalt {total_kommun:,} invånare"
        )
    
    # Beskrivning
    st.info(f"📝 **Om {selected_locality}:** {locality_data['beskrivning']}")
    
    # Karta för orten
    st.subheader("Kartvy")
    try:
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
