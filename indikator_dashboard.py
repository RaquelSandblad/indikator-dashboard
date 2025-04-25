# app.py
import streamlit as st
from PIL import Image
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import requests
import json
import geopandas as gpd
from shapely.geometry import Point
import os

# Konfigurera API-bas-URL
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5000/api")

# ---------------- SIDBAR ----------------
st.set_page_config(page_title="Uppföljning av ÖP - Kungsbacka", layout="wide")
st.sidebar.title("Välj sida")
val = st.sidebar.radio("Välj sida", [
    "Introduktion",
    "Kommunnivå - Planbesked",
    "Kommunnivå - Befolkning",
    "Kommunnivå - Värmekarta",
    "Kommunnivå - Kollektivtrafik",
    "Kungsbacka stad",
    "Anneberg", "Åsa", "Kullavik", "Särö", "Vallda", "Onsala", "Fjärås", "Frillesås"
])

# ---------------- FUNKTION: hämta data från API ----------------
@st.cache_data(ttl=3600)  # Cache i 1 timme
def hamta_data_fran_api(endpoint, params=None):
    """Hämtar data från API Gateway."""
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Kunde inte hämta data: {e}")
        return []

# ---------------- FUNKTION: hämta åldersfördelning via API ----------------
def hamta_aldersfordelning(region="1384", year="2023"):
    """Hämtar befolkningsdata per ålder och kön."""
    data = hamta_data_fran_api("befolkning/alder-kon", {"region": region, "ar": year})
    if data:
        return pd.DataFrame(data)
    return pd.DataFrame(columns=["Kön", "Ålder", "Antal"])

# ---------------- FUNKTION: hämta befolkningstrender via API ----------------
def hamta_befolkningstrend(region="1384", years=None):
    """Hämtar befolkningsutveckling över tid."""
    params = {"region": region}
    if years:
        params["ar"] = ",".join(years)
    
    data = hamta_data_fran_api("befolkning/trend", params)
    if data:
        return pd.DataFrame(data)
    return pd.DataFrame(columns=["År", "Antal"])

# ---------------- FUNKTION: hämta kollektivtrafikdata via API ----------------
def hamta_kollektivtrafik(lan="13"):
    """Hämtar kollektivtrafikdata (hållplatser)."""
    data = hamta_data_fran_api("kollektivtrafik/hallplatser", {"lan": lan})
    if data:
        return pd.DataFrame(data)
    return pd.DataFrame(columns=["namn", "lan", "kommun", "lat", "lon"])

# ---------------- FUNKTION: hämta invånare per ort (flyttas senare till API) ----------------
def hamta_invanare_ort():
    data = {
        "Kungsbacka stad": 23500,
        "Anneberg": 3800,
        "Åsa": 3400,
        "Kullavik": 4100,
        "Särö": 5200,
        "Vallda": 4600,
        "Onsala": 11900,
        "Fjärås": 3800,
        "Frillesås": 2500
    }
    return data

# ---------------- FUNKTION: visa ålderspyramid ----------------
def visa_alderspyramid(df, rubrik="Ålderspyramid"):
    import matplotlib.ticker as ticker

    if df.empty:
        st.info("Ingen data att visa.")
        return

    df["Ålder"] = pd.to_numeric(df["Ålder"], errors="coerce")
    df = df.dropna(subset=["Ålder"])
    df["Ålder"] = df["Ålder"].astype(int)
    df = df[df["Ålder"] <= 100]

    df_pivot = df.pivot_table(index="Ålder", columns="Kön", values="Antal", aggfunc="sum", fill_value=0)
    df_pivot = df_pivot.sort_index()

    for kol in ["Män", "Kvinnor"]:
        if kol not in df_pivot.columns:
            df_pivot[kol] = 0

    df_pivot["Män"] = -df_pivot["Män"]
    max_val = max(abs(df_pivot["Män"].min()), df_pivot["Kvinnor"].max())

    fig, ax = plt.subplots(figsize=(6, 8))
    ax.barh(df_pivot.index, df_pivot["Män"], color="#69b3a2", label="Män")
    ax.barh(df_pivot.index, df_pivot["Kvinnor"], color="#ff9999", label="Kvinnor")

    ax.set_xlim(-max_val * 1.05, max_val * 1.05)
    ax.set_ylim(0, 100)
    ax.invert_yaxis()
    ax.set_xlabel("Antal personer")
    ax.set_ylabel("Ålder")
    ax.set_title(rubrik, fontsize=14)
    ax.axvline(0, color="gray", linewidth=0.5)

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{abs(int(x)):,}"))
    ax.legend(loc="upper right", frameon=False)

    plt.tight_layout()
    st.pyplot(fig)

# ---------------- FUNKTION: visa befolkningsutveckling ----------------
def visa_befolkningsutveckling(df, rubrik="Befolkningsutveckling"):
    if df.empty:
        st.info("Ingen data att visa.")
        return
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["År"], df["Antal"], marker='o', linestyle='-', color="#1f77b4")
    
    ax.set_title(rubrik, fontsize=14)
    ax.set_xlabel("År")
    ax.set_ylabel("Antal invånare")
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Formatera y-axeln med tusentalsavgränsare
    ax.get_yaxis().set_major_formatter(
        plt.matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',').replace(',', ' '))
    )
    
    plt.tight_layout()
    st.pyplot(fig)

# ---------------- FUNKTION: visa värmekarta ----------------
def visa_varmekarta():
    st.subheader("🏘️ Befolkningstäthet i kommunen")
    st.caption("(Simulerad värmekarta – ersätt med riktig statistik och geometri)")
    data = pd.DataFrame({
        'lat': [57.5, 57.48, 57.52, 57.51],
        'lon': [12.1, 12.11, 12.09, 12.13],
        'antal': [5000, 1500, 7000, 3000]
    })
    folium_map = folium.Map(location=[57.5, 12.1], zoom_start=11)
    for _, row in data.iterrows():
        folium.Circle(
            location=[row['lat'], row['lon']],
            radius=row['antal'] * 0.5,
            color="crimson",
            fill=True,
            fill_opacity=0.4
        ).add_to(folium_map)
    st_folium(folium_map, height=500)

# ---------------- FUNKTION: visa kollektivtrafikkarta ----------------
def visa_kollektivtrafikkarta(df=None, kommun=None):
    st.subheader("🚌 Kollektivtrafik - Hållplatser")
    
    if df is None or df.empty:
        df = hamta_kollektivtrafik()
    
    if kommun:
        df = df[df["kommun"] == kommun]
    
    if df.empty:
        st.info("Ingen hållplatsdata tillgänglig.")
        return
    
    # Filtrera ut rader utan koordinater
    df = df.dropna(subset=["lat", "lon"])
    
    if df.empty:
        st.info("Inga koordinater för hållplatser tillgängliga.")
        return
    
    # Beräkna centrum för kartan
    center_lat = df["lat"].mean()
    center_lon = df["lon"].mean()
    
    folium_map = folium.Map(location=[center_lat, center_lon], zoom_start=11)
    
    # Lägg till hållplatser på kartan
    for _, row in df.iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=row["namn"],
            icon=folium.Icon(color="blue", icon="bus", prefix="fa")
        ).add_to(folium_map)
    
    st_folium(folium_map, height=500)

# ---------------- INTRO ----------------
if val == "Introduktion":
    st.title("Uppföljning av Översiktsplanen för Kungsbacka kommun")
    st.write("""
Här kan du följa upp indikatorer för:
- Kommunen som helhet
- Kungsbacka stad
- Utvecklingsorter
    """)
    st.subheader("Strategi 2040")
    
    try:
        bild = Image.open("image.png")
        st.image(bild, caption="Strategi för Kungsbacka kommun", width=700)
    except:
        st.warning("Bilden 'image.png' kunde inte laddas. Kontrollera att den finns i samma mapp som skriptet.")

# ---------------- KOMMUNNIVÅ ----------------
elif val == "Kommunnivå - Planbesked":
    st.title("Kommunnivå – Planbesked")
    st.write("### Planbesked – följer de ÖP?")
    st.markdown("""
Här visas planbesked och huruvida de stämmer överens med ÖP:
- 🟢 Grön = i linje med ÖP
- 🔴 Röd = avviker från ÖP:s strategi
""")

    planbesked = [
        {"namn": "Tölö Ängar", "koordinat": [57.500, 12.078], "status": "i linje"},
        {"namn": "Idala by", "koordinat": [57.420, 12.280], "status": "avviker"},
    ]

    plan_karta = folium.Map(location=[57.47, 12.1], zoom_start=10)
    for pb in planbesked:
        farg = "green" if pb["status"] == "i linje" else "red"
        folium.Marker(
            location=pb["koordinat"],
            popup=pb["namn"],
            icon=folium.Icon(color=farg)
        ).add_to(plan_karta)
    st_folium(plan_karta, width=700, height=500)

elif val == "Kommunnivå - Befolkning":
    st.title("Kommunnivå – Befolkningsstatistik")
    
    # Hämta data för befolkningsutveckling
    trend_df = hamta_befolkningstrend()
    
    if not trend_df.empty and len(trend_df) >= 2:
        senaste_ar = trend_df["År"].max()
        nast_senaste_ar = trend_df["År"].unique()[-2]
        
        bef_senaste = trend_df[trend_df["År"] == senaste_ar]["Antal"].values[0]
        bef_nast_senaste = trend_df[trend_df["År"] == nast_senaste_ar]["Antal"].values[0]
        
        tillvaxt = ((bef_senaste - bef_nast_senaste) / bef_nast_senaste) * 100
        skillnad = bef_senaste - bef_nast_senaste
        
        st.write(f"**📈 Befolkningst
