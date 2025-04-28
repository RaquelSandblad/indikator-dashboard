# indikator_dashboard.py

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
from SCB_Dataservice import SCBService
scb_service = SCBService()

# Konfigurera API-bas-URL (används när vi kopplar in mikroservices)
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

# ---------------- FUNKTION: Läs in planbesked och ÖP ----------------
@st.cache_data
def las_in_planbesked_och_op():
    planbesked = gpd.read_file("planbesked.json")
    op = gpd.read_file("op.json")
    planbesked = planbesked.to_crs(epsg=4326)
    op = op.to_crs(epsg=4326)

    # Funktion för spatial kontroll
    def kontrollera_planbesked(row, op_geom, tröskel=0.5):
        if row.geometry.intersects(op_geom):
            intersektion = row.geometry.intersection(op_geom)
            andel_inom = intersektion.area / row.geometry.area
            return andel_inom >= tröskel
        return False

    op_union = op.unary_union  # Effektivisering

    planbesked["följer_op"] = planbesked.apply(
        lambda row: kontrollera_planbesked(row, op_union, tröskel=0.5),
        axis=1
    )

    return planbesked, op

# ---------------- FUNKTION: Visa planbesked på karta ----------------
def visa_planbesked_karta(planbesked, op):
    st.subheader("Planbesked och Översiktsplan (ÖP)")  # Utan emoji!
    karta = folium.Map(location=[57.5, 12.0], zoom_start=11)

    # Lägg till Översiktsplan
    folium.GeoJson(op, name="Översiktsplan", style_function=lambda x: {
        "color": "blue",
        "weight": 1,
        "fillOpacity": 0.1,
    }).add_to(karta)

    # Lägg till varje planbesked
    for idx, row in planbesked.iterrows():
        color = "green" if row["följer_op"] else "red"
        popup_text = row.get("projektnamn", "Planbesked")
        folium.GeoJson(
            row.geometry.__geo_interface__,  # Denna fix!
            style_function=lambda feature, color=color: {
                "fillColor": color,
                "color": color,
                "weight": 2,
                "fillOpacity": 0.4,
            },
            tooltip=popup_text
        ).add_to(karta)

    # Visa kartan en gång, efter loopen!
    st_folium(karta, width=800, height=600)
    
    st.subheader("Tabell över planbesked")
    st.dataframe(planbesked[["projektnamn", "följer_op"]].rename(columns={"projektnamn": "Projektnamn", "följer_op": "Följer ÖP"}))

# ---------------- FUNKTION: hämta åldersfördelning från SCB ----------------
@st.cache_data
def hamta_aldersfordelning():
    return scb_service.get_population_by_age_gender(region_code="1384", year="2023")


# ---------------- FUNKTION: hämta befolkningstrend från SCB ----------------
@st.cache_data
def hamta_befolkningstrend(region_code="1384", years=None):
    return scb_service.get_population_trend(region_code=region_code, years=years)


# ---------------- FUNKTION: hämta invånare per ort (dummyversion) ----------------
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
def visa_kollektivtrafikkarta(kommun="Kungsbacka"):
    st.subheader("🚌 Kollektivtrafik - Hållplatser")
    st.caption("(Simulerad data - ersätt med riktig data från Trafikverket)")
    
    # Simulerad data för hållplatser
    data = pd.DataFrame({
        'namn': ['Kungsbacka station', 'Hede station', 'Åsa station', 'Fjärås centrum', 'Onsala centrum'],
        'lat': [57.497, 57.515, 57.350, 57.460, 57.420],
        'lon': [12.075, 12.060, 12.120, 12.170, 12.010]
    })
    
    # Beräkna centrum för kartan
    center_lat = data["lat"].mean()
    center_lon = data["lon"].mean()
    
    folium_map = folium.Map(location=[center_lat, center_lon], zoom_start=11)
    
    # Lägg till hållplatser på kartan
    for _, row in data.iterrows():
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
    st.write("Här visas planbesked och huruvida de stämmer överens med ÖP:")
    st.markdown("""
    - 🟢 Grön = i linje med ÖP
    - 🔴 Röd = avviker från ÖP:s strategi
    """)

 

    # ---------------- DEBUG av ÖP ----------------
    st.subheader("🔍 Debugg av Översiktsplan (ÖP)")

# Läs ÖP igen om behövs (du har säkert redan gjort detta i las_in_planbesked_och_op)
    op_debug = gpd.read_file("op.json")

# Visa antal geometrier
    st.write(f"Antal ytor i ÖP: {len(op_debug)}")

# Visa exempel på första ytorna
    st.write(op_debug.head())

# Plot snabbt för att SE kartan
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
op_debug.plot(ax=ax, color="blue", alpha=0.5)
    plt.title("ÖP Geometrier")
    st.pyplot(fig)

    planbesked, op = las_in_planbesked_och_op()
    visa_planbesked_karta(planbesked, op)


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
        
        st.write(f"**📈 Befolkningstillväxt:** {tillvaxt:.2f} %")
        if skillnad >= 0:
            st.markdown(f"⬆️ {skillnad} personer", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:red;'>⬇️ {skillnad} personer</span>", unsafe_allow_html=True)
        
        # Visa befolkningsutveckling över tid
        st.write("**📊 Befolkningsutveckling över tid**")
        visa_befolkningsutveckling(trend_df, rubrik=f"Befolkningsutveckling i Kungsbacka kommun {trend_df['År'].min()}-{trend_df['År'].max()}")
    else:
        st.error("Kunde inte hämta befolkningsutveckling från SCB.")
        bef_2022 = 85682
        bef_2023 = 85476
        tillvaxt = ((bef_2023 - bef_2022) / bef_2022) * 100
        skillnad = bef_2023 - bef_2022

        st.write(f"**📈 Befolkningstillväxt:** {tillvaxt:.2f} %")
        if skillnad >= 0:
            st.markdown(f"⬆️ {skillnad} personer", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:red;'>⬇️ {skillnad} personer</span>", unsafe_allow_html=True)

    st.write("**🥣 Ålderspyramid & åldersfördelning per geografiskt område**")
    df = hamta_aldersfordelning()
    visa_alderspyramid(df, rubrik="Ålderspyramid – Kungsbacka kommun 2023")

elif val == "Kommunnivå - Värmekarta":
    st.title("Kommunnivå – Värmekarta för befolkningstäthet")
    visa_varmekarta()

elif val == "Kommunnivå - Kollektivtrafik":
    st.title("Kommunnivå – Kollektivtrafik")
    visa_kollektivtrafikkarta()

# ---------------- ORTER ----------------
def ort_sida(namn):
    st.title(f"{namn} – utveckling och indikatorer")
    st.write("### Befolkning och struktur")
    inv_data = hamta_invanare_ort()
    if namn in inv_data:
        st.write(f"- Antal invånare: **{inv_data[namn]:,}**")
    else:
        st.write("- Antal invånare: saknas")
    st.write("- Dag/natt-befolkning")

    st.write("### Service och livskvalitet")
    st.write("- Kommunal service")
    st.write("- Kultur/idrottsutbud")

    st.write("### Avstånd till kollektivtrafik (lokalt)")
    st.write("Här kommer lokal analys och karta för hållplatser i orten.")

    st.write("### Inflyttning")
    st.write("Här visas statistik om inflyttning per år och ort")

    st.write("### Demografi")
    df = hamta_aldersfordelning()
    visa_alderspyramid(df, rubrik=f"Ålderspyramid – {namn} (hela kommunen som exempel)")

orter = ["Kungsbacka stad", "Anneberg", "Åsa", "Kullavik", "Särö", "Vallda", "Onsala", "Fjärås", "Frillesås"]
if val in orter:
    ort_sida(val)
