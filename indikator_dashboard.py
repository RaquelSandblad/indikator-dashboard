import streamlit as st
from PIL import Image
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import requests

# ---------------- SIDBAR ----------------
st.set_page_config(page_title="Uppföljning av ÖP - Kungsbacka", layout="wide")
st.sidebar.title("Välj sida")
val = st.sidebar.radio("", [
    "Introduktion", "Kommunnivå", "Kungsbacka stad",
    "Anneberg", "Åsa", "Kullavik", "Särö", "Vallda", "Onsala", "Fjärås", "Frillesås",
    "Rörelser och transport"
])

# ---------------- FUNKTION: hämta åldersfördelning från SCB ----------------
def hamta_aldersfordelning():
    url = "https://api.scb.se/OV0104/v1/doris/sv/ssd/BE/BE0101/BE0101A/BefolkningNy"
    payload = {
        "query": [
            {
                "code": "Region",
                "selection": {
                    "filter": "item",
                    "values": ["1384"]
                }
            },
            {
                "code": "Kon",
                "selection": {
                    "filter": "item",
                    "values": ["1", "2"]
                }
            },
            {
                "code": "Alder",
                "selection": {
                    "filter": "item",
                    "values": [str(i) for i in range(101)] + ["100+"]
                }
            },
            {
                "code": "Tid",
                "selection": {
                    "filter": "item",
                    "values": ["2023"]
                }
            }
        ],
        "response": {"format": "json"}
    }
    response = requests.post(url, json=payload)
    data = response.json()
    rows = data["data"]
    parsed = [
        {
            "Kön": row["key"][1],
            "Ålder": row["key"][2],
            "Antal": int(row["values"][0])
        }
        for row in rows
    ]
    return pd.DataFrame(parsed)

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

# Lägg till extra luft och separator
    st.markdown("###")  # luft
    st.markdown("---")  # visuell linje

    bef_2022 = 85682
    bef_2023 = 85476
    tillvaxt = ((bef_2023 - bef_2022) / bef_2022) * 100
    skillnad = bef_2023 - bef_2022

    st.write("**📈 Befolkningstillväxt**", f"{tillvaxt:.2f} %", delta=f"{skillnad} personer")
    if skillnad >= 0:
        st.markdown(f"⬆️ {skillnad} personer", unsafe_allow_html=True)
    else:
        st.markdown(f"<span style='color:red;'>⬇️ {skillnad} personer</span>", unsafe_allow_html=True)

    st.write("**🧃 Ålderspyramid & åldersfördelning per geografiskt område**")
    if st.button("Visa ålderspyramid"):
        df = hamta_aldersfordelning()
        df_m = df[df.Kön == "1"]
        df_k = df[df.Kön == "2"]

        df_m = df_m.set_index("Ålder")["Antal"] * -1
        df_k = df_k.set_index("Ålder")["Antal"]

        fig, ax = plt.subplots(figsize=(10, 8))
        df_m.plot(kind="barh", color="skyblue", ax=ax, label="Män")
        df_k.plot(kind="barh", color="lightcoral", ax=ax, label="Kvinnor")
        ax.set_title("Ålderspyramid – Kungsbacka kommun 2023")
        ax.set_xlabel("Antal personer")
        ax.legend()
        st.pyplot(fig)

    st.write("**🏢 Näringslivstrender**: arbetstillfällen, detaljplanerad mark – data kan kopplas från SCB eller kommunen")

# ---------------- KUNGSBACKA STAD ----------------
elif val == "Kungsbacka stad":
    st.title("Kungsbacka stad – måluppfyllelse och trender")

    st.write("### Måluppfyllelse")
    faktiskt = 52
    mål = 50
    if faktiskt >= mål:
        st.success(f"✅ Uppfyllt: {faktiskt}% ≥ {mål}%")
    else:
        st.error(f"❌ Ej uppfyllt: {faktiskt}% < {mål}%")

    andel = 78
    mål_ff = 75
    if andel >= mål_ff:
        st.success(f"✅ Uppfyllt: {andel}% ≥ {mål_ff}%")
    else:
        st.error(f"❌ Ej uppfyllt: {andel}% < {mål_ff}%")

    st.write("### Trender och analys")
    st.write("#### Befolkning och struktur")
    st.write("- Antal och andel invånare")
    st.write("- Täthet")
    st.write("- Dag/natt-befolkning")
    st.write("#### Service och livskvalitet")
    st.write("- Kommunal service")
    st.write("- Kultur/idrottsutbud")
    st.write("### Avstånd till kollektivtrafik")
    st.write("Här kan kartor eller statistik visas som visar hur många som har tillgång till kollektivtrafik")

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
    st.write("Visualisering av åldersfördelning, t.ex. ålderspyramid")

if val == "Anneberg":
    ort_sida("Anneberg")
elif val == "Åsa":
    ort_sida("Åsa")
elif val == "Kullavik":
    ort_sida("Kullavik")
elif val == "Särö":
    ort_sida("Särö")
elif val == "Vallda":
    ort_sida("Vallda")
elif val == "Onsala":
    ort_sida("Onsala")
elif val == "Fjärås":
    ort_sida("Fjärås")
elif val == "Frillesås":
    ort_sida("Frillesås")

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
