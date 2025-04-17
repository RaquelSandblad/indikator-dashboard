import streamlit as st
from PIL import Image
import pandas as pd
import folium
from streamlit_folium import st_folium

# ---------------- SIDBAR ----------------
st.set_page_config(page_title="Uppföljning av ÖP - Kungsbacka", layout="wide")
st.sidebar.title("Välj sida")
val = st.sidebar.radio("Välj sida", ["Introduktion", "Kommunnivå", "Kungsbacka stad", "Anneberg & Åsa", "Övriga orter", "Rörelser och transport"])

# ---------------- INTRO ----------------
if val == "Introduktion":
    st.title("Uppföljning av Översiktsplan för Kungsbacka kommun")
    st.write("""
Här kan du följa upp indikatorer för:

- Kommunen som helhet
- Kungsbacka stad
- Anneberg och Åsa
- Övriga orter
- Rörelser och transport
    """)

    st.subheader("Strategi 2040")
    bild = Image.open("image.png")  # Se till att du laddar upp 'image.png' också!
    st.image(bild, caption="Strategi för Kungsbacka kommun", width=700)

# ---------------- KOMMUN ----------------
elif val == "Kommunnivå":
    st.title("Kommunnivå – befolkning, demografi och näringsliv")

    st.write("### Planbesked – följer de ÖP?")
    st.markdown("""
Här kan du se var i kommunen nya planbesked lämnats in, och om de stämmer överens med ÖP:s riktlinjer.
- 🟢 Grön = i linje med ÖP
- 🔴 Röd = avviker från ÖP:s strategi
""")

    # Exempeldata (ersätt med riktig data sen)
    planbesked = [
        {"namn": "Tölö Ängar", "koordinat": [57.500, 12.078], "status": "i linje"},
        {"namn": "Idala by", "koordinat": [57.420, 12.280], "status": "avviker"},
    ]

    # Skapa karta
    plan_karta = folium.Map(location=[57.47, 12.1], zoom_start=10)

    for pb in planbesked:
        färg = "green" if pb["status"] == "i linje" else "red"
        folium.Marker(
            location=pb["koordinat"],
            popup=f"{pb['namn']} – {pb['status']}",
            icon=folium.Icon(color=färg)
        ).add_to(plan_karta)

    st_folium(plan_karta, width=700, height=500)

    bef_2022 = 85682
    bef_2023 = 85476
    tillväxt = ((bef_2023 - bef_2022) / bef_2022) * 100
    skillnad = bef_2023 - bef_2022

    st.write("**📈 Befolkningstillväxt**", f"{tillväxt:.2f} %", delta=f"{skillnad} personer")

    if skillnad >= 0:
        st.markdown(f"⬆️ {skillnad} personer", unsafe_allow_html=True)
    else:
        st.markdown(f"<span style='color:red;'>⬇️ {skillnad} personer</span>", unsafe_allow_html=True)

    st.write("**🧓 Ålderspyramid & åldersfördelning per geografiskt område** *(Ej inlagd ännu – men förberedd)*")
    st.write("**🏭 Näringslivstrender**: arbetstillfällen, detaljplanerad mark – [här kan du koppla in data från SCB eller kommunen]")

# ---------------- STAD ----------------
elif val == "Kungsbacka stad":
    st.title("Kungsbacka stad – måluppfyllelse och trender")

    st.write("### Måluppfyllelse")
    st.write("**Andel nybyggnation i stad**")
    faktiskt = 52
    mål = 50
    if faktiskt >= mål:
        st.success(f"✅ Uppfyllt: {faktiskt}% ≥ {mål}%")
    else:
        st.error(f"❌ Ej uppfyllt: {faktiskt}% < {mål}%")

    st.write("**Flerfamiljshus i staden**")
    andel = 78
    mål_ff = 75
    if andel >= mål_ff:
        st.success(f"✅ Uppfyllt: {andel}% ≥ {mål_ff}%")
    else:
        st.error(f"❌ Ej uppfyllt: {andel}% < {mål_ff}%")

    st.write("### Trender och analys – exempel på indikatorer")
    st.markdown("""
- Antal och andel invånare i staden
- Täthet
- Dag/natt-befolkning
- Boendeformer
- Kommunal service
- Kultur/idrottsutbud
    """)

# ---------------- ORTER ----------------
elif val == "Anneberg & Åsa":
    st.title("Utvecklingsorter – Anneberg & Åsa")

    orter = {
        "Anneberg": {"koordinat": [57.5345, 12.1167], "flerfamiljshus": 36, "mål": 35},
        "Åsa": {"koordinat": [57.353, 12.073], "flerfamiljshus": 30, "mål": 35},
    }

    st.write("### Måluppfyllelse – Andel flerfamiljshus")
    for ort, data in orter.items():
        if data["flerfamiljshus"] >= data["mål"]:
            st.success(f"{ort}: ✅ {data['flerfamiljshus']} % ≥ {data['mål']} %")
        else:
            st.error(f"{ort}: ❌ {data['flerfamiljshus']} % < {data['mål']} %")

    st.write("### 🗺️ Karta")
    karta = folium.Map(location=[57.43, 12.1], zoom_start=10)

    for ort, data in orter.items():
        färg = "green" if data["flerfamiljshus"] >= data["mål"] else "red"
        folium.CircleMarker(
            location=data["koordinat"],
            radius=10,
            popup=f"{ort}: {data['flerfamiljshus']} %",
            color=färg,
            fill=True,
            fill_color=färg,
            fill_opacity=0.7
        ).add_to(karta)

    st_folium(karta, width=700, height=500)

# ---------------- TRANSPORT ----------------
elif val == "Rörelser och transport":
    st.title("Rörelser och transport")

    st.write("### Avstånd till kollektivtrafik")
    st.markdown("""
- 90 % av befolkningen bör ha en hållplats inom **1 km**  
- 50 % bör ha en hållplats inom **400 meter**  
- *(Nuläge: skrivs in manuellt eller hämtas från GIS/SCB senare)*
    """)

    st.write("### Turtäthet för kollektivtrafik")
    st.markdown("""
- Minst **1 avgång per timme** i lågtrafik  
- Minst **30-minuterstrafik** i högtrafik  
- *(Data kan kopplas från Västtrafik eller Trafikverket)*
    """)

    st.write("### Pendlingsmöjligheter")
    st.markdown("""
Här kan ni visa kartor eller statistik för:
- Hur många pendlar ut/in varje dag
- Medelrestid
- Andel som åker kollektivt, cyklar, går, etc.
- *(Exempel: SCB, Trafikverket, kommunens data)*
    """)
