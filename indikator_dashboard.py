import streamlit as st
from PIL import Image
import pandas as pd
import folium
from streamlit_folium import st_folium

# ---------------- SIDBAR ----------------
st.set_page_config(page_title="Uppföljning av ÖP – Kungsbacka", layout="wide")
st.sidebar.title("🗂️ Välj sida")
val = st.sidebar.radio("Gå till:", ["🧭 Introduktion", "🏛️ Kommunnivå", "🏙️ Kungsbacka stad", "🏘️ Anneberg & Åsa"])

# ---------------- INTRO ----------------
if val == "🧭 Introduktion":
    st.title("📊 Uppföljning av Översiktsplan – Kungsbacka")
    st.write("""
Här kan du följa upp indikatorer för:

- Kommunen som helhet
- Staden (Kungsbacka)
- Utvalda orter (Anneberg, Åsa)
    """)

    st.subheader("🗺️ Strategibild (ÖP)")
    bild = Image.open("image.png")  # Se till att du laddar upp 'image.png' också!
    st.image(bild, caption="Strategi för Kungsbacka kommun", use_column_width=True)

# ---------------- KOMMUN ----------------
elif val == "🏛️ Kommunnivå":
    st.title("🏛️ Kommunnivå – befolkning, demografi och näringsliv")

    bef_2022 = 85682
    bef_2023 = 85476
    tillväxt = ((bef_2023 - bef_2022) / bef_2022) * 100

    st.metric("📈 Befolkningstillväxt", f"{tillväxt:.2f} %", delta=f"{bef_2023 - bef_2022} personer")

    st.write("**🧓 Ålderspyramid & åldersfördelning per geografiskt område** *(Ej inlagd ännu – men förberedd)*")
    st.write("**🏭 Näringslivstrender**: arbetstillfällen, detaljplanerad mark – [här kan du koppla in data från SCB eller kommunen]")

# ---------------- STAD ----------------
elif val == "🏙️ Kungsbacka stad":
    st.title("🏙️ Kungsbacka stad – måluppfyllelse och trender")

    st.write("### 🎯 Måluppfyllelse")
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

    st.write("### 📊 Trender och analys – exempel på indikatorer")
    st.markdown("""
- Antal och andel invånare i staden
- Täthet
- Dag/natt-befolkning
- Boendeformer
- Kommunal service
- Kultur/idrottsutbud
    """)

# ---------------- ORTER ----------------
elif val == "🏘️ Anneberg & Åsa":
    st.title("🏘️ Utvecklingsorter – Anneberg & Åsa")

    orter = {
        "Anneberg": {"koordinat": [57.507, 12.191], "flerfamiljshus": 36, "mål": 35},
        "Åsa": {"koordinat": [57.353, 12.073], "flerfamiljshus": 30, "mål": 35},
    }

    st.write("### 🎯 Måluppfyllelse – Andel flerfamiljshus")
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
