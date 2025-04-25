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

# ---------------- SIDBAR ----------------
st.set_page_config(page_title="Uppföljning av ÖP - Kungsbacka", layout="wide")
st.sidebar.title("Välj sida")
val = st.sidebar.radio("Välj sida", [
    "Introduktion",
    "Kommunnivå - Planbesked",
    "Kommunnivå - Befolkning",
    "Kommunnivå - Värmekarta",
    "Kungsbacka stad",
    "Anneberg", "Åsa", "Kullavik", "Särö", "Vallda", "Onsala", "Fjärås", "Frillesås"
])

# ---------------- FUNKTION: hämta åldersfördelning från SCB ----------------
@st.cache_data
def hamta_aldersfordelning():
    url = "https://api.scb.se/OV0104/v1/doris/sv/ssd/BE/BE0101/BE0101A/BefolkningNy"
    payload = {
        "query": [
            {"code": "Region", "selection": {"filter": "item", "values": ["1384"]}},
            {"code": "Kon", "selection": {"filter": "item", "values": ["1", "2"]}},
            {"code": "Alder", "selection": {"filter": "item", "values": [str(i) for i in range(0, 100)] + ["100+"]}},
            {"code": "Tid", "selection": {"filter": "item", "values": ["2023"]}}
        ],
        "response": {"format": "json"}
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        rows = data.get("data", [])
        parsed = []
        for row in rows:
            kön = "Män" if row["key"][1] == "1" else "Kvinnor"
            ålder = row["key"][2]
            antal = int(row["values"][0])
            parsed.append({"Kön": kön, "Ålder": ålder, "Antal": antal})

        df = pd.DataFrame(parsed)
        df["Ålder"] = df["Ålder"].replace("100+", 100).astype(int)
        return df.sort_values(by="Ålder")

    except Exception as e:
        st.error(f"Kunde inte hämta data från SCB: {e}")
        return pd.DataFrame(columns=["Kön", "Ålder", "Antal"])

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
    bild = Image.open("image.png")
    st.image(bild, caption="Strategi för Kungsbacka kommun", width=700)

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
