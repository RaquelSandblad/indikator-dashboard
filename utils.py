# utils.py - Hjälpfunktioner för databehandling och visualisering

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from typing import Dict, List, Optional, Union
import geopandas as gpd
from datetime import datetime, timedelta
import requests
import time

def load_geospatial_data() -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Laddar och bearbetar geospatial data (planbesked och ÖP)"""
    
    try:
        # Läs planbesked
        if os.path.exists("planbesked.json"):
            planbesked = gpd.read_file("planbesked.json").to_crs(epsg=4326)
        else:
            planbesked = gpd.GeoDataFrame()
            st.warning("Filen 'planbesked.json' saknas")
        
        # Läs översiktsplan
        if os.path.exists("op.json"):
            op = gpd.read_file("op.json").to_crs(epsg=4326)
        elif os.path.exists("op.geojson"):
            op = gpd.read_file("op.geojson").to_crs(epsg=4326)
        else:
            op = gpd.GeoDataFrame()
            st.warning("Ingen ÖP-fil hittades (op.json eller op.geojson)")
        
        # Beräkna ÖP-följsamhet om båda finns
        if not planbesked.empty and not op.empty:
            planbesked = calculate_op_compliance(planbesked, op)
        
        return planbesked, op
        
    except Exception as e:
        st.error(f"Fel vid laddning av geodata: {e}")
        return gpd.GeoDataFrame(), gpd.GeoDataFrame()

def calculate_op_compliance(planbesked_gdf: gpd.GeoDataFrame, op_gdf: gpd.GeoDataFrame, 
                          threshold: float = 0.5) -> gpd.GeoDataFrame:
    """Beräknar om planbesked följer översiktsplanen"""
    
    try:
        # Konvertera till metersystem för arealberäkningar
        planbesked_m = planbesked_gdf.to_crs(epsg=3006)  # SWEREF99 TM
        op_m = op_gdf.to_crs(epsg=3006)
        
        # Skapa union av alla ÖP-områden
        op_union = op_m.unary_union
        
        def check_compliance(row):
            """Kontrollerar om en geometri följer ÖP"""
            geom = row.geometry
            
            # Grundläggande validering
            if geom is None or geom.is_empty or not geom.is_valid or geom.area == 0:
                return False
            
            # Kontrollera överlapp med ÖP
            if not geom.intersects(op_union):
                return False
            
            # Beräkna andel som ligger inom ÖP
            intersection = geom.intersection(op_union)
            if intersection.is_empty or not intersection.is_valid:
                return False
            
            overlap_ratio = intersection.area / geom.area if geom.area > 0 else 0
            return overlap_ratio >= threshold
        
        # Applicera kontroll på alla planbesked
        planbesked_m["följer_op"] = planbesked_m.apply(check_compliance, axis=1)
        
        # Kopiera tillbaka till ursprunglig GeoDataFrame
        planbesked_gdf["följer_op"] = planbesked_m["följer_op"]
        
        return planbesked_gdf
        
    except Exception as e:
        st.error(f"Fel vid beräkning av ÖP-följsamhet: {e}")
        planbesked_gdf["följer_op"] = False
        return planbesked_gdf

def create_population_pyramid(df: pd.DataFrame, title: str = "Ålderspyramid") -> go.Figure:
    """Skapar en interaktiv ålderspyramid med Plotly"""
    
    if df.empty:
        return go.Figure().add_annotation(text="Ingen data tillgänglig", 
                                        xref="paper", yref="paper",
                                        x=0.5, y=0.5, showarrow=False)
    
    # Förbered data
    df_pivot = df.pivot_table(index="Ålder", columns="Kön", values="Antal", 
                             aggfunc="sum", fill_value=0)
    
    # Hantera om bara en könstillhörighet finns
    men_data = -df_pivot.get("Män", pd.Series(0, index=df_pivot.index))
    women_data = df_pivot.get("Kvinnor", pd.Series(0, index=df_pivot.index))
    
    fig = go.Figure()
    
    # Lägg till män (negativa värden)
    fig.add_trace(go.Bar(
        y=df_pivot.index,
        x=men_data,
        name="Män",
        orientation="h",
        marker_color="#69b3a2",
        hovertemplate="Ålder: %{y}<br>Män: %{customdata}<extra></extra>",
        customdata=-men_data
    ))
    
    # Lägg till kvinnor (positiva värden)
    fig.add_trace(go.Bar(
        y=df_pivot.index,
        x=women_data,
        name="Kvinnor", 
        orientation="h",
        marker_color="#ff9999",
        hovertemplate="Ålder: %{y}<br>Kvinnor: %{x}<extra></extra>"
    ))
    
    # Uppdatera layout
    max_val = max(abs(men_data.min()), women_data.max()) if not df_pivot.empty else 100
    
    fig.update_layout(
        title=title,
        xaxis_title="Antal personer",
        yaxis_title="Ålder",
        barmode="overlay",
        height=600,
        xaxis=dict(range=[-max_val*1.1, max_val*1.1]),
        legend=dict(x=0.85, y=0.95),
        hovermode="y unified"
    )
    
    return fig

def create_trend_chart(df: pd.DataFrame, x_col: str, y_col: str, 
                      title: str = "Trend över tid") -> go.Figure:
    """Skapar en trendgraf med Plotly"""
    
    if df.empty:
        return go.Figure().add_annotation(text="Ingen data tillgänglig",
                                        xref="paper", yref="paper", 
                                        x=0.5, y=0.5, showarrow=False)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col], 
        mode="lines+markers",
        name=y_col,
        line=dict(color="#1f77b4", width=3),
        marker=dict(size=8),
        hovertemplate=f"{x_col}: %{{x}}<br>{y_col}: %{{y:,.0f}}<extra></extra>"
    ))
    
    # Lägg till trendlinje
    if len(df) > 1:
        z = np.polyfit(range(len(df)), df[y_col], 1)
        p = np.poly1d(z)
        
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=p(range(len(df))),
            mode="lines",
            name="Trend",
            line=dict(color="red", width=2, dash="dash"),
            hoverinfo="skip"
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_col,
        yaxis_title=y_col,
        height=400,
        showlegend=True
    )
    
    return fig

def create_pie_chart(data: Dict[str, int], title: str = "Fördelning") -> go.Figure:
    """Skapar ett interaktivt pajdiagram"""
    
    if not data:
        return go.Figure().add_annotation(text="Ingen data tillgänglig",
                                        xref="paper", yref="paper",
                                        x=0.5, y=0.5, showarrow=False)
    
    labels = list(data.keys())
    values = list(data.values())
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
        hovertemplate="<b>%{label}</b><br>Antal: %{value}<br>Andel: %{percent}<extra></extra>"
    )])
    
    fig.update_layout(
        title=title,
        height=400,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1)
    )
    
    return fig

def format_number(number: Union[int, float], unit: str = "") -> str:
    """Formaterar nummer med tusentalsavgränsare"""
    if isinstance(number, (int, float)):
        if number >= 1000000:
            return f"{number/1000000:.1f}M {unit}".strip()
        elif number >= 1000:
            return f"{number/1000:.1f}k {unit}".strip()
        else:
            return f"{number:,.0f} {unit}".strip()
    return str(number)

def calculate_change(current: float, previous: float) -> tuple[float, str]:
    """Beräknar förändring och trend"""
    if previous == 0:
        return 0, "stable"
    
    change = ((current - previous) / previous) * 100
    
    if change > 0.5:
        return change, "up"
    elif change < -0.5:
        return change, "down"
    else:
        return change, "stable"

def safe_api_request(url: str, params: Optional[Dict] = None, 
                    timeout: int = 30, retries: int = 3) -> Optional[Dict]:
    """Säker API-förfrågan med retry-logik"""
    
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            st.warning(f"Timeout för API-anrop (försök {attempt + 1}/{retries})")
            
        except requests.exceptions.RequestException as e:
            st.warning(f"API-fel: {e} (försök {attempt + 1}/{retries})")
            
        if attempt < retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
    
    return None

def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """Validerar att DataFrame har nödvändiga kolumner"""
    if df.empty:
        return False
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.warning(f"Saknade kolumner i data: {missing_columns}")
        return False
    
    return True

def export_data(data: Union[pd.DataFrame, Dict], filename: str, format: str = "csv"):
    """Exporterar data till fil"""
    try:
        if format.lower() == "csv" and isinstance(data, pd.DataFrame):
            return data.to_csv(index=False).encode('utf-8')
        elif format.lower() == "json":
            if isinstance(data, pd.DataFrame):
                return data.to_json(orient="records", force_ascii=False).encode('utf-8')
            else:
                return json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
        else:
            raise ValueError(f"Ostödd filformat: {format}")
            
    except Exception as e:
        st.error(f"Fel vid export: {e}")
        return None

def create_status_indicator(value: float, target: float, title: str) -> Dict:
    """Skapar en statusindikator för KPI"""
    
    if target == 0:
        ratio = 0
    else:
        ratio = value / target
    
    if ratio >= 1.0:
        status = "success"
        color = "#28a745"
    elif ratio >= 0.8:
        status = "warning"
        color = "#ffc107"
    else:
        status = "danger"
        color = "#dc3545"
    
    return {
        "value": value,
        "target": target,
        "ratio": ratio,
        "status": status,
        "color": color,
        "title": title
    }

import os
import json

def create_population_heatmap(orter_data: Dict) -> go.Figure:
    """Skapar en värmekarta som visar befolkningstäthet per ort"""
    
    if not orter_data:
        return go.Figure().add_annotation(text="Ingen data tillgänglig",
                                        xref="paper", yref="paper",
                                        x=0.5, y=0.5, showarrow=False)
    
    # Förbred data för värmekarta
    lats = [data["lat"] for data in orter_data.values()]
    lons = [data["lon"] for data in orter_data.values()]
    populations = [data["befolkning"] for data in orter_data.values()]
    ort_names = list(orter_data.keys())
    
    # Skapa värmekarta
    fig = go.Figure()
    
    # Lägg till värmekarta-punkter
    fig.add_trace(go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode='markers',
        marker=dict(
            size=[max(8, pop/500) for pop in populations],  # Storlek baserat på befolkning
            color=populations,
            colorscale='Viridis',
            colorbar=dict(title="Befolkning"),
            sizemode='diameter',
            sizemin=8,
            sizemax=40
        ),
        text=ort_names,
        hovertemplate="<b>%{text}</b><br>Befolkning: %{marker.color:,}<extra></extra>",
        showlegend=False
    ))
    
    # Beräkna centrum och zoom
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=9
        ),
        height=500,
        margin=dict(l=0, r=0, t=30, b=0),
        title="Befolkningsvärmekarta - Kungsbacka kommun"
    )
    
    return fig

def create_streamlit_map(planbesked_gdf: gpd.GeoDataFrame, op_gdf: gpd.GeoDataFrame):
    """Skapar en interaktiv karta med Folium för Streamlit"""
    import folium
    from streamlit_folium import st_folium
    
    # Kungsbacka kommun centrum
    center_lat, center_lon = 57.4878, 12.0726
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
    
    # Lägg till planbesked med färgkodning för ÖP-följsamhet
    if not planbesked_gdf.empty:
        for idx, row in planbesked_gdf.iterrows():
            if row.geometry is not None:
                # Använd centroiden för punktmarkering
                if row.geometry.geom_type == 'Point':
                    coords = [row.geometry.y, row.geometry.x]
                else:
                    centroid = row.geometry.centroid
                    coords = [centroid.y, centroid.x]
                
                # Bestäm färg baserat på ÖP-följsamhet
                if 'följer_op' in row and row['följer_op']:
                    icon_color = 'green'
                    icon_name = 'ok-sign'
                    status_text = "✅ Följer ÖP"
                else:
                    icon_color = 'red' 
                    icon_name = 'remove-sign'
                    status_text = "❌ Följer inte ÖP"
                
                # Skapa popup med namn om det finns
                popup_text = f"<b>Planbesked {idx + 1}</b><br>{status_text}"
                
                # Lägg till namn om det finns i data
                if 'namn' in row and pd.notna(row['namn']):
                    popup_text = f"<b>{row['namn']}</b><br>{status_text}"
                elif 'title' in row and pd.notna(row['title']):
                    popup_text = f"<b>{row['title']}</b><br>{status_text}"
                elif 'typ' in row and pd.notna(row['typ']):
                    popup_text = f"<b>{row['typ']}</b><br>Planbesked {idx + 1}<br>{status_text}"
                
                folium.Marker(
                    coords,
                    popup=popup_text,
                    icon=folium.Icon(color=icon_color, icon=icon_name)
                ).add_to(m)
    
    # Lägg till legend
    legend_html = '''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 150px; height: 90px; 
                background-color: white; z-index:9999; font-size:14px;
                border:2px solid grey; padding: 10px">
    <p><b>Planbesked status</b></p>
    <p><i class="fa fa-circle" style="color:green"></i> Följer ÖP</p>
    <p><i class="fa fa-circle" style="color:red"></i> Följer inte ÖP</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return st_folium(m, height=500, width=700)
