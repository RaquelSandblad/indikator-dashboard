# ------------------------------------------------------------
# Tätortskarta - Visar tätorter i Kungsbacka kommun
# Baserat på SCB:s officiella tätortsavgränsning 2023
# ------------------------------------------------------------

import os
import sys
import json
import traceback

import streamlit as st

# OBS! Denna sida är tillfälligt dold från sidomenyn.
st.set_page_config(page_title="Värmekarta (Ej publik)", page_icon="❌", layout="wide", initial_sidebar_state="collapsed")

# Avbryt rendering om någon försöker öppna sidan direkt
st.warning("Denna sida är inte publik ännu.")
st.stop()
import pandas as pd
import plotly.express as px
import requests
import folium
from streamlit_folium import st_folium

# Lägg till projektets rotkatalog i Python-sökvägen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_sources import SCBDataSource

# ---------- Streamlit grundinställningar ----------
st.set_page_config(
    page_title="Tätortskarta - Kungsbacka",
    page_icon="🏘️",
    layout="wide"
)

st.title("🏘️ Tätortskarta - Kungsbacka kommun")
st.caption("Tätortsbegrepp: Max 200 meter mellan husen, minst 200 invånare i sammanhängande bebyggelse.")

# ---------- Hämta befolkningsdata från SCB (kommun 1384) ----------
TOTAL_BEFOLKNING_FALLBACK = 85653
MAN_FALLBACK = 42624
KVINNOR_FALLBACK = 43029

scb = SCBDataSource()

latest_year = None
latest_total = None
men_total = None
women_total = None

try:
    pop_data = scb.fetch_population_data(region_code="1384")
    if isinstance(pop_data, pd.DataFrame) and not pop_data.empty:
        latest_year = int(pop_data["År"].max())
        latest_total = int(pop_data.loc[pop_data["År"] == latest_year, "Antal"].sum())
        men_total = int(pop_data[(pop_data["År"] == latest_year) & (pop_data["Kön"] == "Män")]["Antal"].sum())
        women_total = int(pop_data[(pop_data["År"] == latest_year) & (pop_data["Kön"] == "Kvinnor")]["Antal"].sum())

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total befolkning (SCB)", f"{latest_total:,}", delta=f"År {latest_year}")
        with col2:
            st.metric("Män", f"{men_total:,}", delta=f"{men_total/latest_total*100:.1f}%")
        with col3:
            st.metric("Kvinnor", f"{women_total:,}", delta=f"{women_total/latest_total*100:.1f}%")
    else:
        raise ValueError("Tomt dataobjekt från SCB")
except Exception as e:
    st.warning(f"Kunde inte hämta live befolkningsdata: {e}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total befolkning (SCB)", f"{TOTAL_BEFOLKNING_FALLBACK:,}", delta="2023")
    with col2:
        st.metric("Män", f"{MAN_FALLBACK:,}", delta=f"{MAN_FALLBACK/TOTAL_BEFOLKNING_FALLBACK*100:.1f}%")
    with col3:
        st.metric("Kvinnor", f"{KVINNOR_FALLBACK:,}", delta=f"{KVINNOR_FALLBACK/TOTAL_BEFOLKNING_FALLBACK*100:.1f}%")

total_kommun_bef = latest_total if latest_total else TOTAL_BEFOLKNING_FALLBACK

# ---------- Skapa tätortskarta med SCB:s avgränsningar ----------
st.subheader("📍 Tätorter i Kungsbacka kommun")
st.info("🏘️ **Tätort (SCB):** Max 200 meter mellan husen, minst 200 invånare. Data från 2023.")

data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(data_dir, exist_ok=True)
geojson_path = os.path.join(data_dir, "scb_tatorter_2023_kungsbacka.geojson")

tatorter_geojson = None

try:
    if os.path.exists(geojson_path):
        with open(geojson_path, "r", encoding="utf-8") as f:
            tatorter_geojson = json.load(f)
        st.caption("📊 Data från lokal cache (SCB Tätorter 2023).")
    else:
        with st.spinner("Hämtar tätortsdata från SCB…"):
            url = "https://geodata.scb.se/geoserver/stat/wfs"
            params = {
                "service": "WFS",
                "version": "2.0.0",
                "request": "GetFeature",
                "typeNames": "stat:Tatorter_2023",
                "outputFormat": "application/json",
                "CQL_FILTER": "kommun='1384'",
            }
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            tatorter_geojson = resp.json()

            with open(geojson_path, "w", encoding="utf-8") as f:
                json.dump(tatorter_geojson, f, ensure_ascii=False, indent=2)
        st.caption("📊 Data hämtad från SCB Geodatatjänst (Tätorter 2023).")
except FileNotFoundError as e:
    st.error("❌ Kunde inte ladda tätortsdata.")
    st.info(f"Filen hittades inte: {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ Fel vid hämtning av tätortsdata: {e}")
    with st.expander("Teknisk information"):
        st.code(traceback.format_exc())
    st.stop()

if not tatorter_geojson or "features" not in tatorter_geojson:
    st.error("❌ Ingen tätortsdata tillgänglig.")
    st.stop()

# ---------- Bygg karta ----------
m = folium.Map(location=[57.48, 12.08], zoom_start=10, tiles="OpenStreetMap")

total_tatort_befolkning = 0
total_area = 0.0

for feature in tatorter_geojson["features"]:
    props = feature.get("properties", {})
    tatort_namn = props.get("tatort", "Okänd")
    befolkning = int(props.get("bef", 0) or 0)
    area_ha = float(props.get("area_ha", 0) or 0.0)
    tatortskod = props.get("tatortskod", "")

    total_tatort_befolkning += befolkning
    total_area += area_ha

    farg = "#ff8c42"

    popup_html = f"""
    <div style='font-family: Arial; min-width: 220px;'>
        <h3 style='margin: 0 0 8px 0; color: #ff6b35;'>{tatort_namn}</h3>
        <p style='margin: 5px 0;'><strong>Befolkning:</strong> {befolkning:,} invånare</p>
        <p style='margin: 5px 0;'><strong>Areal:</strong> {area_ha:,.0f} hektar</p>
        <p style='margin: 5px 0; font-size: 11px; color: #666;'>Tätortskod: {tatortskod}</p>
        <hr style='margin: 8px 0; border: none; border-top: 1px solid #ddd;'>
        <p style='margin: 5px 0; font-size: 10px; font-style: italic;'>SCB Tätortsavgränsning 2023</p>
    </div>
    """

    folium.GeoJson(
        feature,
        style_function=lambda _, color=farg: {
            "fillColor": color,
            "color": "#cc5500",
            "weight": 2,
            "fillOpacity": 0.85,
            "opacity": 1
        },
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"{tatort_namn} ({befolkning:,} inv)"
    ).add_to(m)

landsbygd_bef = max(int(total_kommun_bef - total_tatort_befolkning), 0)

legend_html = f"""
<div style="
    position: fixed;
    bottom: 50px;
    left: 50px;
    width: 300px;
    background-color: white;
    border: 2px solid #666;
    z-index: 9999;
    font-size: 13px;
    padding: 12px;
    border-radius: 5px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
">
  <h4 style='margin: 0 0 10px 0; color: #333;'>Tätortsbegrepp</h4>
  <p style='margin: 5px 0; line-height: 1.5;'>
    <span style='display: inline-block; width: 20px; height: 12px; background-color: #ff8c42; border: 1px solid #cc5500;'></span>
    Tätortsområde
  </p>
  <hr style='margin: 10px 0; border: none; border-top: 1px solid #ddd;'>
  <p style='margin: 5px 0; font-size: 11px; line-height: 1.4;'>
    <strong>Definition:</strong> Max 200 meter mellan husen, minst 200 invånare
  </p>
  <hr style='margin: 10px 0; border: none; border-top: 1px solid #ddd;'>
  <p style='margin: 3px 0; font-size: 11px;'>
    <strong>I tätorter:</strong> {total_tatort_befolkning:,} inv
  </p>
  <p style='margin: 3px 0; font-size: 11px;'>
    <strong>På landsbygd:</strong> ~{landsbygd_bef:,} inv
  </p>
  <p style='margin: 8px 0 3px 0; font-size: 10px; color: #666;'>
    Källa: SCB Tätortsavgränsning 2023
  </p>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

st_folium(m, width=1200, height=650)

# ---------- Sammanfattande statistik ----------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Antal tätorter", len(tatorter_geojson["features"]))
with col2:
    st.metric("Befolkning i tätorter", f"{total_tatort_befolkning:,}")
with col3:
    st.metric("Befolkning på landsbygd", f"~{landsbygd_bef:,}")
with col4:
    st.metric("Total areal tätorter", f"{total_area:,.0f} ha")

andel_tatort = (total_tatort_befolkning / total_kommun_bef * 100) if total_kommun_bef > 0 else 0
andel_landsbygd = (landsbygd_bef / total_kommun_bef * 100) if total_kommun_bef > 0 else 0

st.info(
    f"💡 **Obs!** Av kommunens totalt {total_kommun_bef:,} invånare bor "
    f"{total_tatort_befolkning:,} ({andel_tatort:.1f}%) i tätorter och "
    f"cirka {landsbygd_bef:,} ({andel_landsbygd:.1f}%) på landsbygden."
)

# ---------- Statistik under kartan ----------
st.subheader("📊 Befolkningsfördelning per tätort")

tatorter_lista = []
for feature in tatorter_geojson["features"]:
    props = feature.get("properties", {})
    tatorter_lista.append({
        "Tätort": props.get("tatort", "Okänd"),
        "Befolkning": int(props.get("bef", 0) or 0),
        "Areal (ha)": float(props.get("area_ha", 0) or 0.0),
        "Tätortskod": props.get("tatortskod", "")
    })

df_orter = pd.DataFrame(tatorter_lista).sort_values("Befolkning", ascending=False)
df_orter["Andel av tätorter (%)"] = (df_orter["Befolkning"] / df_orter["Befolkning"].sum()) * 100
df_orter["Andel av kommun (%)"] = (df_orter["Befolkning"] / total_kommun_bef) * 100

fig = px.bar(
    df_orter,
    x="Tätort",
    y="Befolkning",
    title="Befolkning per tätort i Kungsbacka kommun (SCB 2023)",
    text="Befolkning",
    color_discrete_sequence=["#ff8c42"]
)

fig.update_traces(texttemplate='%{text:,}', textposition='outside')
fig.update_layout(
    xaxis_tickangle=-45,
    height=500,
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

with st.expander("📋 Detaljerad tätortsstatistik"):
    st.dataframe(
        df_orter.style.format({
            "Befolkning": "{:,.0f}",
            "Areal (ha)": "{:,.0f}",
            "Andel av tätorter (%)": "{:.1f}%",
            "Andel av kommun (%)": "{:.1f}%"
        }),
        use_container_width=True,
        hide_index=True
    )
    st.caption("Källa: SCB Tätortsavgränsning 2023 + SCB Befolkningsstatistik 2024")
