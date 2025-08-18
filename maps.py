# maps.py - Förbättrade kartfunktioner med riktiga datakällor

import folium
from folium import plugins
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import geopandas as gpd
import requests
from typing import Dict, List, Optional, Tuple
import numpy as np
from config import ORTER, COLORS, GIS_SOURCES

class InteractiveMap:
    """Klass för att skapa interaktiva kartor med olika lager"""
    
    def __init__(self, center_lat: float = 57.49, center_lon: float = 12.08, zoom: int = 11):
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.zoom = zoom
        
    def create_base_map(self) -> folium.Map:
        """Skapar en baskarta"""
        m = folium.Map(
            location=[self.center_lat, self.center_lon],
            zoom_start=self.zoom,
            tiles=None
        )
        
        # Lägg till olika baskartor
        folium.TileLayer(
            tiles='OpenStreetMap',
            name='OpenStreetMap',
            overlay=False,
            control=True
        ).add_to(m)
        
        folium.TileLayer(
            tiles='CartoDB positron',
            name='CartoDB Positron',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Lantmäteriets topografiska karta (WMS)
        try:
            folium.raster_layers.WmsTileLayer(
                url='https://minkarta.lantmateriet.se/map/topowebbcache/',
                layers='topowebbcache',
                name='Lantmäteriet Topo',
                fmt='image/png',
                transparent=True,
                overlay=False,
                control=True,
                version='1.1.1'
            ).add_to(m)
        except:
            pass  # Om WMS inte fungerar, fortsätt utan
        
        return m
    
    def add_planbesked_layer(self, m: folium.Map, planbesked_gdf: gpd.GeoDataFrame) -> folium.Map:
        """Lägger till planbesked som lager"""
        if planbesked_gdf.empty:
            return m
            
        # Skapa färgkodning baserat på ÖP-följsamhet
        def get_color(follows_op):
            return COLORS["op_green"] if follows_op else COLORS["op_red"]
        
        for idx, row in planbesked_gdf.iterrows():
            color = get_color(row.get("följer_op", False))
            
            # Popup-information
            popup_html = f"""
            <div style="width: 200px;">
                <h4>{row.get('projektnamn', 'Planbesked')}</h4>
                <p><strong>Följer ÖP:</strong> {'Ja' if row.get('följer_op', False) else 'Nej'}</p>
                <p><strong>Typ:</strong> {row.get('typ', 'Okänt')}</p>
                <p><strong>Status:</strong> {row.get('status', 'Okänt')}</p>
            </div>
            """
            
            folium.GeoJson(
                row.geometry.__geo_interface__,
                style_function=lambda feature, color=color: {
                    "fillColor": color,
                    "color": color,
                    "weight": 2,
                    "fillOpacity": 0.6,
                    "opacity": 0.8
                },
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=row.get('projektnamn', 'Planbesked')
            ).add_to(m)
        
        return m
    
    def add_op_layer(self, m: folium.Map, op_gdf: gpd.GeoDataFrame, visible: bool = True) -> folium.Map:
        """Lägger till översiktsplan som lager"""
        if op_gdf.empty:
            return m
            
        style = {
            "color": COLORS["theme_blue"],
            "weight": 2,
            "fillOpacity": 0.1 if visible else 0,
            "opacity": 0.8 if visible else 0
        }
        
        folium.GeoJson(
            op_gdf.to_json(),
            style_function=lambda feature: style,
            name="Översiktsplan",
            show=visible
        ).add_to(m)
        
        return m
    
    def add_nature_reserves(self, m: folium.Map) -> folium.Map:
        """Lägger till naturreservat från Naturvårdsverket"""
        try:
            # Hämta naturreservat via WFS
            wfs_url = "https://geodata.naturvardsverket.se/geoserver/naturreservat/wfs"
            params = {
                "service": "WFS",
                "version": "2.0.0",
                "request": "GetFeature", 
                "typeName": "naturreservat:naturreservat",
                "outputFormat": "application/json",
                "bbox": "11.5,57.0,12.5,58.0,EPSG:4326"  # Kungsbacka-området
            }
            
            # Läs direkt med geopandas
            gdf = gpd.read_file(wfs_url, bbox=(11.5, 57.0, 12.5, 58.0))
            
            if not gdf.empty:
                folium.GeoJson(
                    gdf.to_json(),
                    style_function=lambda feature: {
                        "fillColor": "green",
                        "color": "darkgreen",
                        "weight": 1,
                        "fillOpacity": 0.3
                    },
                    popup=folium.GeoJsonPopup(fields=["namn"], aliases=["Namn:"]),
                    name="Naturreservat",
                    show=False
                ).add_to(m)
                
        except Exception as e:
            st.warning(f"Kunde inte ladda naturreservat: {e}")
        
        return m
    
    def add_traffic_data(self, m: folium.Map) -> folium.Map:
        """Lägger till trafikdata (demo med Trafikverkets öppna data)"""
        # Demo-data för trafikmätpunkter
        traffic_data = [
            {"name": "E6 Kungsbacka", "lat": 57.50, "lon": 12.07, "flow": 25000, "speed": 78},
            {"name": "E20 Kungsbacka", "lat": 57.48, "lon": 12.08, "flow": 18000, "speed": 72},
            {"name": "Väg 158 Särö", "lat": 57.42, "lon": 11.93, "flow": 8000, "speed": 65},
            {"name": "Väg 168 Onsala", "lat": 57.41, "lon": 12.01, "flow": 12000, "speed": 68}
        ]
        
        feature_group = folium.FeatureGroup(name="Trafikflöden", show=False)
        
        for station in traffic_data:
            # Färgkodning baserat på trafikflöde
            if station["flow"] > 20000:
                color = "red"
                radius = 15
            elif station["flow"] > 10000:
                color = "orange" 
                radius = 10
            else:
                color = "green"
                radius = 7
            
            popup_html = f"""
            <div style="width: 200px;">
                <h4>{station['name']}</h4>
                <p><strong>Trafikflöde:</strong> {station['flow']:,} fordon/dygn</p>
                <p><strong>Medelhastighet:</strong> {station['speed']} km/h</p>
            </div>
            """
            
            folium.CircleMarker(
                location=[station["lat"], station["lon"]],
                radius=radius,
                popup=folium.Popup(popup_html, max_width=300),
                color=color,
                fillColor=color,
                fillOpacity=0.7,
                tooltip=f"{station['name']}: {station['flow']:,} fordon/dygn"
            ).add_to(feature_group)
        
        feature_group.add_to(m)
        return m
    
    def add_public_transport(self, m: folium.Map) -> folium.Map:
        """Lägger till kollektivtrafikstationer"""
        # Stationer i Kungsbacka (demo-data)
        stations = [
            {"name": "Kungsbacka station", "lat": 57.4878, "lon": 12.0765, "type": "tåg"},
            {"name": "Åsa station", "lat": 57.3500, "lon": 12.1167, "type": "tåg"},
            {"name": "Särö station", "lat": 57.4167, "lon": 11.9333, "type": "tåg"},
            {"name": "Kungsbacka centrum", "lat": 57.4885, "lon": 12.0755, "type": "buss"},
            {"name": "Onsala centrum", "lat": 57.4056, "lon": 12.0119, "type": "buss"}
        ]
        
        feature_group = folium.FeatureGroup(name="Kollektivtrafik", show=False)
        
        for station in stations:
            icon_color = "blue" if station["type"] == "tåg" else "green"
            icon_symbol = "train" if station["type"] == "tåg" else "bus"
            
            folium.Marker(
                location=[station["lat"], station["lon"]],
                popup=f"<b>{station['name']}</b><br>Typ: {station['type'].title()}",
                icon=folium.Icon(color=icon_color, icon=icon_symbol, prefix="fa"),
                tooltip=station["name"]
            ).add_to(feature_group)
        
        feature_group.add_to(m)
        return m
    
    def add_population_heatmap(self, m: folium.Map) -> folium.Map:
        """Lägger till befolkningstäthet som värmekarta"""
        # Demo-data för befolkningstäthet per ruta
        heat_data = []
        
        # Generera slumpmässiga befolkningspunkter runt Kungsbacka
        np.random.seed(42)  # För reproducerbarhet
        
        for _ in range(200):
            lat = np.random.normal(57.49, 0.05)  # Runt Kungsbacka
            lon = np.random.normal(12.08, 0.08)
            intensity = np.random.exponential(0.5)  # Exponentialfördelning för realistisk spridning
            heat_data.append([lat, lon, intensity])
        
        # Lägg till extra punkter för orterna
        for ort, coords in ORTER.items():
            population_density = coords.get("befolkning", 1000) / 10000  # Normaliserad densitet
            heat_data.append([coords["lat"], coords["lon"], population_density])
        
        # Skapa värmekarta
        heat_map = plugins.HeatMap(
            heat_data,
            name="Befolkningstäthet",
            min_opacity=0.2,
            max_zoom=15,
            radius=25,
            blur=15,
            show=False
        )
        
        m.add_child(heat_map)
        return m
    
    def create_planning_map(self, planbesked_gdf: gpd.GeoDataFrame, op_gdf: gpd.GeoDataFrame) -> folium.Map:
        """Skapar en komplett planeringskarta"""
        m = self.create_base_map()
        
        # Lägg till alla lager
        m = self.add_op_layer(m, op_gdf, visible=False)
        m = self.add_planbesked_layer(m, planbesked_gdf)
        m = self.add_nature_reserves(m)
        m = self.add_traffic_data(m)
        m = self.add_public_transport(m)
        m = self.add_population_heatmap(m)
        
        # Lägg till lagerhantering
        folium.LayerControl(collapsed=False).add_to(m)
        
        # Lägg till målverktyg
        draw = plugins.Draw(
            export=True,
            filename='export.geojson',
            position='topleft',
            draw_options={
                'polyline': True,
                'polygon': True,
                'circle': True,
                'rectangle': True,
                'marker': True,
                'circlemarker': False,
            }
        )
        draw.add_to(m)
        
        # Lägg till fullskärmsknapp
        plugins.Fullscreen().add_to(m)
        
        # Lägg till miniaturkarta
        minimap = plugins.MiniMap()
        m.add_child(minimap)
        
        return m

def create_streamlit_map(planbesked_gdf: gpd.GeoDataFrame, op_gdf: gpd.GeoDataFrame):
    """Skapar och visar karta i Streamlit"""
    
    st.subheader("🗺️ Interaktiv planeringskarta")
    
    # Kontroller för lager
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        show_op = st.checkbox("Visa Översiktsplan", value=False)
    with col2:
        show_nature = st.checkbox("Visa Naturreservat", value=False)
    with col3:
        show_traffic = st.checkbox("Visa Trafikdata", value=False)
    with col4:
        show_transit = st.checkbox("Visa Kollektivtrafik", value=False)
    
    # Skapa kartan
    map_creator = InteractiveMap()
    m = map_creator.create_base_map()
    
    # Lägg till lager baserat på användarval
    if show_op:
        m = map_creator.add_op_layer(m, op_gdf, visible=True)
    
    if not planbesked_gdf.empty:
        m = map_creator.add_planbesked_layer(m, planbesked_gdf)
    
    if show_nature:
        m = map_creator.add_nature_reserves(m)
    
    if show_traffic:
        m = map_creator.add_traffic_data(m)
    
    if show_transit:
        m = map_creator.add_public_transport(m)
    
    # Lägg till lagerhantering
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Visa kartan
    map_data = st_folium(m, width=1200, height=600, returned_objects=["last_object_clicked"])
    
    # Visa information om klickade objekt
    if map_data["last_object_clicked"]:
        st.write("**Senast klickade objekt:**")
        st.json(map_data["last_object_clicked"])
    
    return map_data
