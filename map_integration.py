# map_integration.py - Förbättrad kartintegration för Kungsbacka kommun

import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import geopandas as gpd
import pandas as pd
from typing import Dict, List, Optional, Tuple
import json

class KungsbackaMapIntegration:
    """
    Förbättrad kartintegration för Kungsbacka kommun
    Inkluderar WMS, WFS och andra geospatial datakällor
    """
    
    def __init__(self):
        self.center_lat = 57.4878
        self.center_lon = 12.0765
        self.default_zoom = 11
        
        # Kungsbacka kommun WMS/WFS endpoints (dessa behöver verifieras)
        self.wms_base = "https://kartor.kungsbacka.se/geoserver/wms"
        self.wfs_base = "https://kartor.kungsbacka.se/geoserver/wfs"
        
        # Nationella WMS-tjänster som fungerar
        self.lantmateriet_wms = "https://minkarta.lantmateriet.se/map/topowebbcache?"
        self.nvr_wms = "https://geodata.naturvardsverket.se/arcgis/services/Naturvardsregistret_Publikt/Naturreservat/MapServer/WMSServer"
        
    def create_base_map(self, center: Tuple[float, float] = None, zoom: int = None) -> folium.Map:
        """Skapar en baskarta för Kungsbacka"""
        
        if center is None:
            center = (self.center_lat, self.center_lon)
        if zoom is None:
            zoom = self.default_zoom
            
        # Skapa karta med olika bakgrundskartor
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles=None  # Vi lägger till custom tiles
        )
        
        # Lägg till olika bakgrundskartor
        folium.TileLayer(
            'OpenStreetMap',
            name='OpenStreetMap',
            overlay=False,
            control=True
        ).add_to(m)
        
        folium.TileLayer(
            'CartoDB Positron',
            name='CartoDB Light',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Lantmäteriet topografisk karta (kräver ingen API-nyckel för visning)
        folium.TileLayer(
            tiles='https://api.lantmateriet.se/open/topoweb-ccby/v1/wmts/1.0.0/topoweb_ccby/default/3857/{z}/{y}/{x}.png',
            attr='© Lantmäteriet',
            name='Lantmäteriet Topo',
            overlay=False,
            control=True
        ).add_to(m)
        
        return m
    
    def add_kommun_boundary(self, map_obj: folium.Map) -> folium.Map:
        """Lägger till Kungsbacka kommungräns"""
        try:
            # Försök hämta kommungränser från SCB
            scb_kommun_url = "https://geodata.scb.se/arcgis/rest/services/StatisticalUnits/AdministrativeUnits_2022/MapServer/2/query"
            
            params = {
                'where': "KOMMUNNAMN='Kungsbacka'",
                'outFields': '*',
                'f': 'geojson',
                'returnGeometry': 'true'
            }
            
            response = requests.get(scb_kommun_url, params=params, timeout=30)
            
            if response.status_code == 200:
                geojson_data = response.json()
                
                if geojson_data.get('features'):
                    folium.GeoJson(
                        geojson_data,
                        style_function=lambda x: {
                            'color': '#ff6b6b',
                            'weight': 3,
                            'fillOpacity': 0.1,
                            'fillColor': '#ff6b6b'
                        },
                        popup='Kungsbacka kommun',
                        tooltip='Kungsbacka kommungräns'
                    ).add_to(map_obj)
                    
                    return map_obj
            
            # Fallback: rita ungefärlig kommungräns
            self._add_approximate_boundary(map_obj)
            
        except Exception as e:
            st.warning(f"Kunde inte ladda kommungräns: {e}")
            self._add_approximate_boundary(map_obj)
        
        return map_obj
    
    def _add_approximate_boundary(self, map_obj: folium.Map):
        """Lägger till ungefärlig kommungräns"""
        # Ungefärliga koordinater för Kungsbacka kommun
        boundary_coords = [
            [57.3, 11.9],
            [57.3, 12.3],
            [57.6, 12.3],
            [57.6, 11.9],
            [57.3, 11.9]
        ]
        
        folium.Polygon(
            locations=boundary_coords,
            color='#ff6b6b',
            weight=2,
            fillOpacity=0.1,
            popup='Kungsbacka kommun (ungefärlig gräns)'
        ).add_to(map_obj)
    
    def add_nature_reserves(self, map_obj: folium.Map) -> folium.Map:
        """Lägger till naturreservat i Kungsbacka"""
        try:
            # Naturvårdsverkets WFS för naturreservat
            wfs_url = "https://geodata.naturvardsverket.se/arcgis/rest/services/Naturvardsregistret_Publikt/Naturreservat/MapServer/0/query"
            
            params = {
                'where': "KOMMUN LIKE '%Kungsbacka%'",
                'outFields': '*',
                'f': 'geojson',
                'returnGeometry': 'true'
            }
            
            response = requests.get(wfs_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                for feature in data.get('features', []):
                    properties = feature.get('properties', {})
                    geometry = feature.get('geometry', {})
                    
                    if geometry and geometry.get('type') == 'Polygon':
                        name = properties.get('NAMN', 'Naturreservat')
                        area = properties.get('AREAL_HA', 'Okänd storlek')
                        
                        coords = []
                        for ring in geometry['coordinates']:
                            ring_coords = [[coord[1], coord[0]] for coord in ring]  # Växla lat/lon
                            coords.extend(ring_coords)
                        
                        if coords:
                            folium.Polygon(
                                locations=coords,
                                color='green',
                                weight=2,
                                fillOpacity=0.3,
                                fillColor='green',
                                popup=f"<b>{name}</b><br>Areal: {area} ha",
                                tooltip=name
                            ).add_to(map_obj)
            
        except Exception as e:
            st.warning(f"Kunde inte ladda naturreservat: {e}")
        
        return map_obj
    
    def add_planbesked_data(self, map_obj: folium.Map, planbesked_gdf: gpd.GeoDataFrame) -> folium.Map:
        """Lägger till planbesked på kartan"""
        try:
            if planbesked_gdf.empty:
                return map_obj
            
            for idx, row in planbesked_gdf.iterrows():
                # Skapa popup-innehåll
                popup_html = f"""
                <div style="width: 200px;">
                    <h4>{row.get('namn', 'Planbesked')}</h4>
                    <p><b>Typ:</b> {row.get('typ', 'Okänt')}</p>
                    <p><b>Status:</b> {row.get('status', 'Okänd')}</p>
                    <p><b>Datum:</b> {row.get('datum', 'Okänt')}</p>
                </div>
                """
                
                # Bestäm färg baserat på status eller typ
                color = 'blue'
                if 'följer_op' in row and row['följer_op']:
                    color = 'green'
                elif 'följer_op' in row and not row['följer_op']:
                    color = 'red'
                
                # Lägg till markör eller polygon beroende på geometri
                geometry = row.get('geometry')
                if geometry:
                    if geometry.geom_type == 'Point':
                        folium.Marker(
                            location=[geometry.y, geometry.x],
                            popup=popup_html,
                            tooltip=row.get('namn', 'Planbesked'),
                            icon=folium.Icon(color=color, icon='info-sign')
                        ).add_to(map_obj)
                    elif geometry.geom_type in ['Polygon', 'MultiPolygon']:
                        # Konvertera till GeoJSON
                        geojson = gpd.GeoSeries([geometry]).__geo_interface__
                        
                        folium.GeoJson(
                            geojson,
                            style_function=lambda x, color=color: {
                                'color': color,
                                'weight': 2,
                                'fillOpacity': 0.3
                            },
                            popup=popup_html,
                            tooltip=row.get('namn', 'Planbesked')
                        ).add_to(map_obj)
                
        except Exception as e:
            st.warning(f"Kunde inte ladda planbesked: {e}")
        
        return map_obj
    
    def add_demographic_heatmap(self, map_obj: folium.Map, orter_data: Dict) -> folium.Map:
        """Lägger till befolkningsvärmekarta"""
        try:
            from folium.plugins import HeatMap
            
            heat_data = []
            for ort, data in orter_data.items():
                lat = data.get('lat')
                lon = data.get('lon') 
                befolkning = data.get('befolkning', 0)
                
                if lat and lon and befolkning > 0:
                    # Normalisera befolkningsdata för värmekarta
                    intensity = befolkning / 1000  # Skala ned för bättre visualisering
                    heat_data.append([lat, lon, intensity])
            
            if heat_data:
                HeatMap(
                    heat_data,
                    name='Befolkningstäthet',
                    radius=15,
                    blur=10,
                    max_zoom=1,
                    overlay=True,
                    control=True
                ).add_to(map_obj)
                
        except Exception as e:
            st.warning(f"Kunde inte skapa värmekarta: {e}")
        
        return map_obj
    
    def create_interactive_dashboard_map(self, 
                                       planbesked_gdf: gpd.GeoDataFrame = None,
                                       orter_data: Dict = None,
                                       include_layers: List[str] = None) -> folium.Map:
        """Skapar en komplett interaktiv karta för dashboarden"""
        
        if include_layers is None:
            include_layers = ['kommun_boundary', 'nature_reserves', 'planbesked', 'heatmap']
        
        # Skapa baskarta
        map_obj = self.create_base_map()
        
        # Lägg till lager baserat på vad som efterfrågas
        if 'kommun_boundary' in include_layers:
            map_obj = self.add_kommun_boundary(map_obj)
        
        if 'nature_reserves' in include_layers:
            map_obj = self.add_nature_reserves(map_obj)
        
        if 'planbesked' in include_layers and planbesked_gdf is not None:
            map_obj = self.add_planbesked_data(map_obj, planbesked_gdf)
        
        if 'heatmap' in include_layers and orter_data is not None:
            map_obj = self.add_demographic_heatmap(map_obj, orter_data)
        
        # Lägg till lagerkontroll
        folium.LayerControl().add_to(map_obj)
        
        return map_obj

# Global instans för användning i dashboard
kungsbacka_map = KungsbackaMapIntegration()

def create_enhanced_map(planbesked_gdf=None, op_gdf=None, orter_data=None):
    """Wrapper-funktion för enkel användning i dashboard"""
    
    # Bestäm vilka lager som ska inkluderas
    layers = ['kommun_boundary']
    
    if planbesked_gdf is not None and not planbesked_gdf.empty:
        layers.append('planbesked')
    
    if orter_data:
        layers.append('heatmap')
    
    # Lägg alltid till naturreservat
    layers.append('nature_reserves')
    
    return kungsbacka_map.create_interactive_dashboard_map(
        planbesked_gdf=planbesked_gdf,
        orter_data=orter_data,
        include_layers=layers
    )

def get_kommun_wfs_data(layer_name: str) -> Optional[gpd.GeoDataFrame]:
    """
    Försöker hämta WFS-data från Kungsbacka kommun
    OBS: URL:er behöver verifieras med kommunen
    """
    try:
        wfs_base = "https://kartor.kungsbacka.se/geoserver/wfs"
        
        params = {
            'service': 'WFS',
            'version': '2.0.0',
            'request': 'GetFeature',
            'typeName': layer_name,
            'outputFormat': 'application/json',
            'srsName': 'EPSG:4326'
        }
        
        response = requests.get(wfs_base, params=params, timeout=30)
        
        if response.status_code == 200:
            return gpd.read_file(response.text)
        else:
            st.warning(f"WFS-anrop misslyckades för {layer_name}: {response.status_code}")
            return None
            
    except Exception as e:
        st.warning(f"Fel vid WFS-anrop för {layer_name}: {e}")
        return None

def create_simple_map_with_points(points_data: List[Dict]) -> folium.Map:
    """Skapar en enkel karta med punkter"""
    
    # Beräkna center baserat på punkter
    if points_data:
        avg_lat = sum(p['lat'] for p in points_data) / len(points_data)
        avg_lon = sum(p['lon'] for p in points_data) / len(points_data)
        center = (avg_lat, avg_lon)
    else:
        center = (57.4878, 12.0765)  # Kungsbacka centrum
    
    m = folium.Map(location=center, zoom_start=12)
    
    # Lägg till punkter
    for point in points_data:
        folium.Marker(
            location=[point['lat'], point['lon']],
            popup=point.get('popup', ''),
            tooltip=point.get('tooltip', ''),
            icon=folium.Icon(
                color=point.get('color', 'blue'),
                icon=point.get('icon', 'info-sign')
            )
        ).add_to(m)
    
    return m
