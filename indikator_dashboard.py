import streamlit as st
from PIL import Image
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import requests
from requests.exceptions import RequestException
import json

# ---------------- SIDBAR ----------------
st.set_page_config(page_title="Uppföljning av ÖP - Kungsbacka", layout="wide")
st.sidebar.title("Välj sida")
val = st.sidebar.radio("Välj sida", [
    "Introduktion", "Kommunnivå", "Kungsbacka stad",
    "Anneberg", "Åsa", "Kullavik", "Särö", "Vallda", "Onsala", "Fjärås", "Frillesås",
    "Rörelser och transport"
])

# ---------------- FUNKTION: hämta åldersfördelning från SCB ----------------
def hamta_aldersfordelning():
    url = "https://api.scb.se/OV0104/v1/doris/sv/ssd/BE/BE0101/BE0101A/BefolkningNy"
    payload = {
        "query": [
            {"code": "Region", "selection": {"filter": "item", "values": ["1384"]}},
            {"code": "Kon", "selection": {"filter": "item", "values": ["1", "2"]}},
            {"code": "Alder", "selection": {"filter": "item", "values": [str(i) for i in range(101)] + ["100+"]}},
            {"code": "Tid", "selection": {"filter": "item", "values": ["2023"]}}
        ],
        "response": {"format": "json"}
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        rows = data.get("data", [])
        parsed = [
            {"Kön": row["key"][1], "Ålder": row["key"][2], "Antal": int(row["values"][0])}
            for row in rows
        ]
        return pd.DataFrame(parsed)
    except (RequestException, json.JSONDecodeError, KeyError):
        st.warning("Kunde inte hämta åldersfördelning just nu från SCB. Försök igen senare.")
        return pd.DataFrame(columns=["Kön", "Ålder", "Antal"])

# ---------------- FUNKTION: visa ålderspyramid ----------------
def visa_alderspyramid(df, rubrik="Ålderspyramid"):
    if not df.empty:
        df_m = df[df.Kön == "1"]
        df_k = df[df.Kön == "2"]

        df_m = df_m.set_index("Ålder")["Antal"] * -1
        df_k = df_k.set_index("Ålder")["Antal"]

        fig, ax = plt.subplots(figsize=(10, 8))
        df_m.plot(kind="barh", color="skyblue", ax=ax, label="Män")
        df_k.plot(kind="barh", color="lightcoral", ax=ax, label="Kvinnor")
        ax.set_title(rubrik)
        ax.set_xlabel("Antal personer")
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("Ingen data att visa just nu.")

# ---------------- INTRO ----------------
if val == "Introduktion":
    st.title("Uppföljning av Översiktsplanen för Kungsbacka kommun")
    st.write("""
Här kan du följa upp indikatorer för:
- Kommunen som helhet
- Kungsbacka stad
- Utvecklingsorter
- Rörelser och transport
    """)
    st.subheader("Strategi 2040")
    bild = Image.open("image.png")
    st.image(bild, caption="Strategi för Kungsbacka kommun", width=700)

# ---------------- KOMMUN ----------------
elif val == "Kommunnivå":
    st.title("Kommunnivå – befolkning, demografi och näringsliv")

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
    st.markdown("<hr style='margin-top: 15px; margin-bottom: 10px;'>", unsafe_allow_html=True)

    bef_2022 = 85682
    bef_2023 = 85476
    tillvaxt = ((bef_2023 - bef_2022) / bef_2022) * 100
    skillnad = bef_2023 - bef_2022

    st.write("**📈 Befolkningstillväxt**", f"{tillvaxt:.2f} %", delta=f"{skillnad} personer")
    if skillnad >= 0:
        st.markdown(f"⬆️ {skillnad} personer", unsafe_allow_html=True)
    else:
        st.markdown(f"<span style='color:red;'>⬇️ {skillnad} personer</span>", unsafe_allow_html=True)

    st.write("**🥣 Ålderspyramid & åldersfördelning per geografiskt område**")
    df = hamta_aldersfordelning()
    visa_alderspyramid(df, rubrik="Ålderspyramid – Kungsbacka kommun 2023")

# ---------------- ORTER ----------------
def ort_sida(namn):
    st.title(f"{namn} – utveckling och indikatorer")
    st.write("### Befolkning och struktur")
    st.write("- Antal och andel invånare")
    st.write("- Täthet")
    st.write("- Dag/natt-befolkning")
    st.write("### Service och livskvalitet")
    st.write("- Kommunal service")
    st.write("- Kultur/idrottsutbud")
    st.write("### Avstånd till kollektivtrafik")
    st.write("Kartor och statistik kan kopplas in för att visa avstånd till hållplats")
    st.write("### Inflyttning")
    st.write("Här visas statistik om inflyttning")
    st.write("### Demografi")
    df = hamta_aldersfordelning()
    visa_alderspyramid(df, rubrik=f"Ålderspyramid – {namn} (hela kommunen som exempel)")

orter = ["Kungsbacka stad", "Anneberg", "Åsa", "Kullavik", "Särö", "Vallda", "Onsala", "Fjärås", "Frillesås"]
if val in orter:
    ort_sida(val)

# ---------------- TRANSPORT ----------------
elif val == "Rörelser och transport":
    st.title("Rörelser och transport")
    st.write("### Avstånd till kollektivtrafik")
    st.markdown("""
- 90 % av befolkningen bör ha en hållplats inom **1 km**  
- 50 % bör ha en hållplats inom **400 meter**
""")
    st.write("### Turtäthet för kollektivtrafik")
    st.markdown("""
- Minst **1 avgång per timme** i lågtrafik  
- Minst **30-minuterstrafik** i högtrafik
""")
    st.write("### Pendlingsmöjligheter")
    st.markdown("""
Visualisering av:
- Hur många som pendlar in/ut
- Medelrestid
- Andel som åker kollektivt, cyklar, går, etc.
""")

def testdata_kungsbacka():
    url = "https://api.scb.se/OV0104/v1/doris/sv/ssd/BE/BE0101/BE0101A/BefolkningNy"
    payload = {
        "query": [
            {"code": "Region", "selection": {"filter": "item", "values": ["1384"]}},
            {"code": "Kon", "selection": {"filter": "item", "values": ["1", "2"]}},
            {"code": "Alder", "selection": {"filter": "item", "values": ["20", "30", "40"]}},
            {"code": "Tid", "selection": {"filter": "item", "values": ["2023"]}}
        ],
        "response": {"format": "json"}
    }
    response = requests.post(url, json=payload)
    return response.json()
