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

# Streamlit config
st.set_page_config(page_title="Uppföljning av ÖP - Kungsbacka", layout="wide")

@st.cache_data(ttl=86400)
def las_in_planbesked_och_op():
    planbesked = gpd.read_file("planbesked.json").to_crs(epsg=4326)
    op = gpd.read_file("op.json").to_crs(epsg=4326)

    planbesked_m = planbesked.to_crs(epsg=3006)
    op_m = op.to_crs(epsg=3006)
    op_union = op_m.unary_union

    def kontrollera_planbesked(row, op_geom, tröskel=0.5):
        geom = row.geometry
        if geom is None or geom.is_empty or not geom.is_valid or geom.area == 0:
            return False
        if not geom.intersects(op_geom):
            return False
        intersektion = geom.intersection(op_geom)
        if intersektion.is_empty or not intersektion.is_valid:
            return False
        andel_inom = intersektion.area / geom.area if geom.area > 0 else 0
        return andel_inom >= tröskel

    planbesked_m["följer_op"] = planbesked_m.apply(
        lambda row: kontrollera_planbesked(row, op_union, tröskel=0.5), axis=1
    )

    planbesked["följer_op"] = planbesked_m["följer_op"]

    return planbesked, op  # 

# Konfigurera API-bas-URL (används när vi kopplar in mikroservices)
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5000/api")

# SIDVAL
val = st.sidebar.radio("Välj sida", [
    "Introduktion",
    "Kommunnivå - Planbesked",
    "Kommunnivå - Förhandsbesked",   # 👈 Ny sida här!
    "Kommunnivå - Befolkning",
    "Kommunnivå - Värmekarta",
    "Kommunnivå - Kollektivtrafik",
    "Kungsbacka stad",
    "Anneberg", "Åsa", "Kullavik", "Särö", "Vallda", "Onsala", "Fjärås", "Frillesås"
])

# Ny funktion: hämta befolkning baserat på kön och ålder

def hamta_filterad_befolkning(region_code="1384", kon=["1", "2"], alder_intervall=["20", "21", "22", "23", "24"], year="2023"):
    query = {
        "query": [
            {
                "code": "Region",
                "selection": { "filter": "item", "values": [region_code] }
            },
            {
                "code": "Kon",
                "selection": { "filter": "item", "values": kon }
            },
            {
                "code": "Alder",
                "selection": { "filter": "item", "values": alder_intervall }
            },
            {
                "code": "Tid",
                "selection": { "filter": "item", "values": [year] }
            }
        ],
        "response": {
            "format": "json"
        }
    }
    print(f"[DEBUG] Genererad query: {query}")  # Debugutskrift
    return scb_service.fetch_data("BE/BE0101/BE0101A/BefolkningNy", query)
    
def hamta_befolkningstrend(region_code="1384", years=None):
    return scb_service.get_population_trend(region_code=region_code, years=years)

def hamta_aldersfordelning():
    # Skapa query för att hämta åldersfördelning
    query = {
        "query": [
            {"code": "Region", "selection": {"filter": "item", "values": ["1384"]}},
            {"code": "Kon", "selection": {"filter": "item", "values": ["1", "2"]}},
            {"code": "Alder", "selection": {"filter": "item", "values": [str(i) for i in range(0, 101)]}},  # Fixad åldersintervall
            {"code": "Tid", "selection": {"filter": "item", "values": ["2023"]}}
        ],
        "response": {"format": "json"}
    }

    # Debug: Visa query
    st.write("Debug: Skickad query till SCB API för åldersfördelning")
    st.json(query)

    try:
        # Skicka query till SCB API
        data = scb_service.fetch_data("BE/BE0101/BE0101A/BefolkningNy", query)
        st.write("Debug: Data returnerad från SCB API:")
        st.write(data)

        # Omvandla till DataFrame om data finns
        if "data" in data:
            return pd.DataFrame(data["data"])
        else:
            st.error("🚨 Inga data returnerades från SCB API.")
            return pd.DataFrame()  # Returnera tom DataFrame
    except requests.exceptions.HTTPError as e:
        st.error(f"🚨 Kunde inte hämta data från SCB API: {e}")
        return pd.DataFrame()  # Returnera tom DataFrame
    except Exception as e:
        st.error(f"🚨 Ett oväntat fel inträffade: {e}")
        return pd.DataFrame()  # Returnera tom DataFrame

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
    ax.get_yaxis().set_major_formatter(
        plt.matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',').replace(',', ' '))
    )
    plt.tight_layout()
    st.pyplot(fig)

# Visa i befolkningssidan
if val == "Kommunnivå - Befolkning":
    st.title("Kommunnivå – Befolkningsstatistik")

    kön_val = st.selectbox("Välj kön", {"Totalt": ["1", "2"], "Kvinnor": ["2"], "Män": ["1"]})
    ålder_val = st.selectbox("Välj åldersintervall", [f"{i}-{i+4}" for i in range(0, 100, 5)])
    
    # Kontrollera att ålder_val är korrekt
    st.write(f"Debug: Åldersintervall som valts: {ålder_val}")
    if ålder_val is None or "-" not in ålder_val:
        st.error("🚨 Vänligen välj ett giltigt åldersintervall.")
    else:
        start, end = map(int, ålder_val.split("-"))
        alder_values = [str(i) for i in range(start, end + 1)]
    # Skapa query för debugvisning
    query = {
        "query": [
            {"code": "Region", "selection": {"filter": "item", "values": ["1384"]}},
            {"code": "Kon", "selection": {"filter": "item", "values": kön_val}},
            {"code": "Alder", "selection": {"filter": "item", "values": alder_values}},
            {"code": "Tid", "selection": {"filter": "item", "values": ["2023"]}}
        ],
        "response": {"format": "json"}
    }

    # Visa debug (valfritt)
    with st.expander("📦 Visa skickad SCB-query"):
        st.json(query)

# Försök hämta antal – med skydd
    try:
        antal = scb_service.fetch_data("BE/BE0101/BE0101A/BefolkningNy", query)
        total = sum(int(d["values"][0].replace("..", "0")) for d in antal.get("data", []))
        st.metric("Totalt antal i valt urval", f"{total:,}")
    except Exception as e:
        st.error("🚨 Kunde inte hämta data från SCB – kontrollera att urvalet är giltigt.")


        trend_df = hamta_befolkningstrend()
        if not trend_df.empty and len(trend_df) >= 2:
            visa_befolkningsutveckling(trend_df)

        df = hamta_aldersfordelning()
        st.write("Debug: Dataframe innehåll från hamta_aldersfordelning:")
        st.write(df)
        visa_alderspyramid(df)

# ---------------- ANVÄNDNING ----------------
# ---------------- FUNKTION: Visa planbesked på karta ----------------
def visa_planbesked_karta(planbesked, op):
    st.subheader("Planbesked och Översiktsplan (ÖP)") 
    karta = folium.Map(location=[57.5, 12.0], zoom_start=11)

    # Visa eller göm ÖP-lagret
    visa_op = st.checkbox("Visa Översiktsplan (ÖP)", value=False)

    if visa_op:
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
    if df.empty:
        st.error("🚨 Ålderspyramiden kunde inte visas eftersom det saknas data.")
        return
    
    # Kontrollera att nödvändiga kolumner finns
    required_columns = {"Ålder", "Kön", "Antal"}
    if not required_columns.issubset(df.columns):
        st.error("🚨 Data saknar nödvändiga kolumner för att skapa ålderspyramiden.")
        st.write(f"Debug: Tillgängliga kolumner: {df.columns}")
        return

    # Kontrollera åldersvärden
    df["Ålder"] = pd.to_numeric(df["Ålder"], errors="coerce")
    if df["Ålder"].isnull().all():
        st.error("🚨 Data innehåller inga giltiga åldersvärden.")
        return

    # Fortsätt med att skapa ålderspyramidgrafen
    import matplotlib.ticker as ticker
    df_pivot = df.pivot_table(index="Ålder", columns="Kön", values="Antal", aggfunc="sum", fill_value=0)
    df_pivot["Män"] = -df_pivot.get("Män", 0)  # Negativa värden för män
    max_val = max(abs(df_pivot["Män"].min()), df_pivot["Kvinnor"].max())

    fig, ax = plt.subplots(figsize=(6, 8))
    ax.barh(df_pivot.index, df_pivot["Män"], color="#69b3a2", label="Män")
    ax.barh(df_pivot.index, df_pivot["Kvinnor"], color="#ff9999", label="Kvinnor")
    ax.set_xlim(-max_val * 1.05, max_val * 1.05)
    ax.set_xlabel("Antal personer")
    ax.set_ylabel("Ålder")
    ax.set_title(rubrik, fontsize=14)
    ax.axvline(0, color="gray", linewidth=0.5)
    ax.legend(loc="upper right", frameon=False)

    plt.tight_layout()
    st.pyplot(fig)

# ---------------- FUNKTION: Visa temarubrik med färgkod ----------------
def temarubrik(titel, färg="#f1c40f"):  # Standardfärg: gul
    st.markdown(f"""
    <div style='background-color:{färg};padding:0.5em 1em;border-radius:8px;margin-top:1em;margin-bottom:1em'>
        <h4 style='color:white;margin:0'>{titel}</h4>
    </div>
    """, unsafe_allow_html=True)

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
def visa_befolkningstatet_heatmap():
    # Konfigurera API-slutpunkt och query för SCB
    BASE_URL = "https://api.scb.se/OV0104/v1/doris/sv/ssd/"
    query = {
        "query": [
            {
                "code": "Region",
                "selection": {
                    "filter": "item",
                    "values": ["1384"]  # Kommunens kod (Kungsbacka)
                }
            },
            {
                "code": "Tid",
                "selection": {
                    "filter": "item",
                    "values": ["2024"]  # Årtal för data
                }
            }
        ],
        "response": {
            "format": "json"
        }
    }

    try:
        # Hämta data från SCB:s API
        response = requests.post(BASE_URL + "BE/BE0101/BE0101A/BefolkningNy", json=query)
        response.raise_for_status()
        data = response.json()

        # Kontrollera att data returneras
        if "data" not in data:
            st.error("Inga data returnerades från SCB API.")
            return

        # Konvertera data till en DataFrame
        import pandas as pd
        df = pd.DataFrame(data["data"])
        df["value"] = df["values"].apply(lambda x: int(x[0].replace("..", "0")))  # Hantera ".." som 0
        df["id"] = df["key"].apply(lambda x: x[0])  # Extrahera region-ID
        st.write("Debug: Data hämtad från SCB API:")
        st.write(df.head())

        # Läs in geometridata (testa med op.geojson eller op.json)
        try:
            geo_path = "op.geojson"  # Första valet
            geo_df = gpd.read_file(geo_path)
        except FileNotFoundError:
            geo_path = "op.json"  # Andra valet
            geo_df = gpd.read_file(geo_path)

        # Kombinera SCB-data med geometridata
        geo_df = geo_df.merge(df, left_on="id", right_on="id")

        # Säkerställ att geometrin har rätt koordinatsystem
        geo_df = geo_df.to_crs(epsg=4326)

        # Skapa karta med Folium
        karta = folium.Map(location=[57.5, 12.0], zoom_start=10)  # Justera till Kungsbackas koordinater
        folium.Choropleth(
            geo_data=geo_df,
            data=geo_df,
            columns=["id", "value"],  # ID och befolkningstäthet
            key_on="feature.properties.id",
            fill_color="YlOrRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Befolkning per km²"
        ).add_to(karta)

        # Visa kartan i Streamlit
        st_folium(karta, height=600, width=900)

    except requests.exceptions.RequestException as e:
        st.error(f"Fel vid anrop till SCB:s API: {e}")
    except FileNotFoundError:
        st.error("Filen 'op.geojson' eller 'op.json' kunde inte hittas. Kontrollera att filerna finns i projektmappen.")
    except Exception as e:
        st.error(f"Ett oväntat fel inträffade: {e}")
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

# ---------------- FUNKTION: Visa cirkeldiagram för planbesked ----------------
def visa_planbesked_paj(planbesked_df):
    följer = planbesked_df["följer_op"].sum()
    avviker = len(planbesked_df) - följer
    labels = ["Följer ÖP", "Avviker från ÖP"]
    values = [följer, avviker]
    colors = ["#6ab7a8", "#ff6f69"]

    fig, ax = plt.subplots(figsize=(6, 4))
    wedges, texts = ax.pie(values, colors=colors, startangle=90, radius=1)

    total = sum(values)
    text_props = {"fontsize": 12}

    # Lägg etiketter till höger om varje wedge, justerat manuellt
    for i, wedge in enumerate(wedges):
        label = f"{labels[i]} ({values[i]} st, {values[i]/total:.1%})"
        x = 1.2
        y = 0.5 - i * 0.3
        ax.text(x, y, label, ha="left", va="center", **text_props)

    ax.set_aspect("equal")
    st.pyplot(fig)

# ---------------- INTRO ----------------
if val == "Introduktion":
    st.title("Uppföljning av översiktsplanering för Kungsbacka kommun")
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

    planbesked, op = las_in_planbesked_och_op()

    # Kartan i en placeholder så layouten blir stabil
    with st.container():
        visa_planbesked_karta(planbesked, op)
    with st.container():
        visa_planbesked_paj(planbesked)

elif val == "Kommunnivå - Förhandsbesked":
    st.title("Kommunnivå – Förhandsbesked")
    st.write("Här kan du analysera inkomna förhandsbesked och deras relation till ÖP.")
    
    # Exempel på innehåll
    st.markdown("📌 *Här kan ni t.ex. visa statistik, karta eller lista över förhandsbesked.*")

    # TODO: Ersätt detta med din riktiga data eller funktion
    st.info("🔧 Denna sida är under uppbyggnad. Vill du visa karta, tabell eller analys här?")


# ---------------- KOMMUNNIVÅ – BEFOLKNINGSSTATISTIK ----------------
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

        st.write("**📊 Befolkningsutveckling över tid**")
        visa_befolkningsutveckling(trend_df)

        st.write("**🥣 Ålderspyramid & åldersfördelning per geografiskt område**")

    # Hämta åldersdata och visa ålderspyramid
    df = hamta_aldersfordelning()
    if df.empty:
        st.error("🚨 Ingen data kunde hämtas. Försök igen senare.")
    else:
        if st.button("Visa ålderspyramid"):
            visa_alderspyramid(df, rubrik="Ålderspyramid – Kungsbacka kommun 2023")

    # Välj kön och åldersintervall
    kön_val = st.selectbox("Välj kön", {"Totalt": ["1", "2"], "Kvinnor": ["2"], "Män": ["1"]})
    ålder_val = st.selectbox("Välj åldersintervall", [f"{i}-{i+4}" for i in range(0, 100, 5)])
    
    # Hämta filtrerad befolkningsdata
    antal = hamta_filterad_befolkning(kon=kön_val, alder_intervall=ålder_val)
    st.metric("Totalt antal i valt urval", f"{antal:,}")
    
    # Visa trenddata om den finns
    trend_df = hamta_befolkningstrend()
    if not trend_df.empty and len(trend_df) >= 2:
        visa_befolkningsutveckling(trend_df)

        st.write("**Näringslivstrender**: arbetstillfällen, detaljplanerad mark – data kan kopplas från SCB eller kommunen")
elif val == "Kommunnivå - Värmekarta":
    st.title("Kommunnivå – Befolkningstäthet (1 km-rutor)")
    visa_befolkningstatet_heatmap()

elif val == "Kommunnivå - Kollektivtrafik":
    st.title("Kommunnivå – Kollektivtrafik")
    visa_kollektivtrafikkarta()

# ---------------- ORTER ----------------
def ort_sida(namn):
    st.title(f"{namn} – utveckling och indikatorer")

    inv_data = hamta_invanare_ort()

    # Planbesked
    temarubrik("Planbesked och förhandsbesked", färg="#f1c40f")
    st.write("- Hur förhåller det sig till ÖP?")
    st.write("- Byggs det mer i prioriterade orter?")
    # ➕ Här kan du lägga in karta eller analysdata om du har ortspecifik planbesked-info

    # Befolkning
    temarubrik("Befolkning", färg="#c40000")
    if namn in inv_data:
        st.write(f"- Antal invånare: **{inv_data[namn]:,}**")
    else:
        st.write("- Antal invånare: saknas")
    st.write("- Dag/natt-befolkning")
    df = hamta_aldersfordelning()
    visa_alderspyramid(df, rubrik=f"Ålderspyramid – {namn} (hela kommunen som exempel)")

    # Bebyggelse
    temarubrik("Bebyggelsen", färg="#f5a081")
    st.write("- Fördelning mellan bostadstyper (flerbostadshus, villor, etc)")
    st.write("- Täthetskarta (när det finns data)")

    # Naturresurser
    temarubrik("Naturresurser", färg="#4ba3a4")
    st.write("- Påverkan på jordbruksmark vid planbesked / byggande")

    # Trafik
    temarubrik("Trafik", färg="#8b6f4a")
    st.write("- Avstånd till kollektivtrafik")
    st.write("- Andel som bor inom 400 m eller 1 km")
    visa_kollektivtrafikkarta(namn)  # Simulerad just nu

    # Kommunal service
    temarubrik("Kommunal service", färg="#f248b9")
    st.write("- Hur väl fungerar servicen?")
    st.write("- Upplevs som för lite eller för mycket")

    # Kultur och fritid
    temarubrik("Kultur och fritid", färg="#5e2ca5")
    st.write("- Finns det i orten?")
    st.write("- Har det ökat eller minskat?")


orter = ["Kungsbacka stad", "Anneberg", "Åsa", "Kullavik", "Särö", "Vallda", "Onsala", "Fjärås", "Frillesås"]
if val in orter:
    ort_sida(val)
