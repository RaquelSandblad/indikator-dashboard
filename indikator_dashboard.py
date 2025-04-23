import streamlit as st
from PIL import Image
import pandas as pd
import folium
from streamlit_folium import st_folium

# ---------------- SIDBAR ----------------
st.set_page_config(page_title="Uppföljning av ÖP - Kungsbacka", layout="wide")
st.sidebar.title("Välj sida")
val = st.sidebar.radio("", [
    "Introduktion", "Kommunnivå", "Kungsbacka stad", 
    "Anneberg", "Åsa", "Kullavik", "Särö", "Vallda", "Onsala", "Fjärås", "Frillesås",
    "Övriga orter", "Rörelser och transport"
])

# ---------------- INTRO ----------------
if val == "Introduktion":
    st.title("Uppföljning av Översiktsplanen för Kungsbacka kommun")
    st.write("""
Här kan du följa upp indikatorer för:

- Kommunen som helhet
- Kungsbacka stad
- Prioriterade utvecklingsorter (Åsa, Anneberg, m.fl.)
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
Här kan du se var i kommunen nya planbesked lämnats in.
- 🟢 Grön = i linje med ÖP
- 🔴 Röd = avviker från ÖP:s strategi
""")

    planbesked = [
        {"namn": "Tölö Ängar", "koordinat": [57.500, 12.078], "status": "i linje"},
        {"namn": "Idala by", "koordinat": [57.420, 12.280], "status": "avviker"},
    ]
    plan_karta = folium.Map(location=[57.47, 12.1], zoom_start=10)
    for pb in planbesked:
        färg = "green" if pb["status"] == "i linje" else "red"
        folium.Marker(
            location=pb["koordinat"],
            popup=pb["namn"],
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

# ---------------- GEMENSAM ORTFUNKTION ----------------
def ort_sida(namn):
    st.title(f"{namn} – utveckling och indikatorer")
    st.write("### Demografi")
    st.write("- Antal och andel invånare")
    st.write("- Ålderspyramid")
    st.write("- Boendeformer")

    st.write("### Täthet och bebyggelse")
    st.write("- Täthet")
    st.write("- Dag/natt-befolkning")

    st.write("### Service och livskvalitet")
    st.write("- Kommunal service")
    st.write("- Kultur/idrottsutbud")

    st.write("### Avstånd till kollektivtrafik")
    st.write("(Här kan du visa kartor eller statistik som visar hur många som har tillgång till hållplats inom 400 m och 1 km.)")

# ---------------- ORTER ----------------
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
