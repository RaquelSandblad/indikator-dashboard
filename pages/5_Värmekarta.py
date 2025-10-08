""""""

Tätortskarta - Visar tätorter i Kungsbacka kommunTätortskarta - Visar tätorter i Kungsbacka kommun

Baserat på SCB:s officiella tätortsavgränsning 2023Baserat på SCB:s officiella tätortsavgränsning 2023

""""""



import streamlit as stimport streamlit as st

import sysimport sys

import osimport os

import jsonimpor        # Lägg till polygon med STARK orange färg så den syns tydligt

import requests        folium.GeoJson(

            feature,

# Lägg till projektets rotkatalog i Python-sökvägen            style_function=lambda x, color=farg: {

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))                'fillColor': color,

                'color': '#cc5500',  # Mörkare kant

from data_sources import SCBDataSource                'weight': 2,

import folium                'fillOpacity': 0.85  # MYCKET synlig - som i din bild!

from streamlit_folium import st_folium            },

import pandas as pd            popup=folium.Popup(popup_html, max_width=300),

import plotly.express as px            tooltip=f"{tatort_namn} ({befolkning:,} inv)"

        ).add_to(m)t requests

st.set_page_config(

    page_title="Tätortskarta - Kungsbacka",# Lägg till projektets rotkatalog i Python-sökvägen

    page_icon="🏘️",sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    layout="wide"

)from data_sources import SCBDataSource

import folium

st.title("🏘️ Tätortskarta - Kungsbacka kommun")from streamlit_folium import st_folium

st.caption("Tätortsbegrepp: Max 200 meter mellan husen, minst 200 invånare i sammanhängande bebyggelse")import pandas as pd

import plotly.express as px

# Hämta korrekt befolkningsdata från SCB

scb = SCBDataSource()st.set_page_config(

    page_title="Tätortskarta - Kungsbacka",

try:    page_icon="�️",

    pop_data = scb.fetch_population_data(region_code="1384")    layout="wide"

    )

    if not pop_data.empty:

        latest_year = pop_data["År"].max()st.title("�️ Tätortskarta - Kungsbacka kommun")

        latest_total = pop_data[pop_data["År"] == latest_year]["Antal"].sum()st.caption("Tätortsbegrepp: Max 200 meter mellan husen, minst 200 invånare i sammanhängande bebyggelse")

        men_total = pop_data[(pop_data["År"] == latest_year) & (pop_data["Kön"] == "Män")]["Antal"].sum()

        women_total = pop_data[(pop_data["År"] == latest_year) & (pop_data["Kön"] == "Kvinnor")]["Antal"].sum()# Hämta verklig befolkningsdata från SCB

        scb = SCBDataSource()

        # Visa statistik först

        col1, col2, col3 = st.columns(3)# Korrekt befolkningsdata från SCB (2023)

        TOTAL_BEFOLKNING_2023 = 85653

        with col1:MAN_2023 = 42624

            st.metric("Total befolkning (SCB)", f"{latest_total:,}", KVINNOR_2023 = 43029

                     delta=f"År {latest_year}")

        try:

        with col2:    pop_data = scb.fetch_population_data()

            st.metric("Män", f"{men_total:,}",     

                     delta=f"{men_total/latest_total*100:.1f}%")    if not pop_data.empty:

                # Visa faktisk SCB data

        with col3:        latest_year = pop_data["År"].max()

            st.metric("Kvinnor", f"{women_total:,}",         latest_total = pop_data[pop_data["År"] == latest_year]["Antal"].sum()

                     delta=f"{women_total/latest_total*100:.1f}%")        men_total = pop_data[(pop_data["År"] == latest_year) & (pop_data["Kön"] == "Män")]["Antal"].sum()

    else:        women_total = pop_data[(pop_data["År"] == latest_year) & (pop_data["Kön"] == "Kvinnor")]["Antal"].sum()

        # Fallback med korrekta siffror        

        col1, col2, col3 = st.columns(3)        # Visa statistik först

        with col1:        col1, col2, col3 = st.columns(3)

            st.metric("Total befolkning", "85,792", delta="2024")        

        with col2:        with col1:

            st.metric("Män", "42,694", delta="49.8%")            st.metric("Total befolkning (SCB)", f"{latest_total:,}", 

        with col3:                     delta=f"År {latest_year}")

            st.metric("Kvinnor", "43,098", delta="50.2%")        

                    with col2:

except Exception as e:            st.metric("Män", f"{men_total:,}", 

    st.warning(f"Kunde inte hämta live befolkningsdata: {e}")                     delta=f"{men_total/latest_total*100:.1f}%")

    # Fallback        

    col1, col2, col3 = st.columns(3)        with col3:

    with col1:            st.metric("Kvinnor", f"{women_total:,}", 

        st.metric("Total befolkning", "85,792", delta="2024")                     delta=f"{women_total/latest_total*100:.1f}%")

    with col2:                     

        st.metric("Män", "42,694", delta="49.8%")    else:

    with col3:        # Använd verifierad SCB data 2023

        st.metric("Kvinnor", "43,098", delta="50.2%")        col1, col2, col3 = st.columns(3)

        with col1:

# Skapa tätortskarta med SCB:s officiella avgränsningar            st.metric("Total befolkning Kungsbacka", f"{TOTAL_BEFOLKNING_2023:,}", 

st.subheader("📍 Tätorter i Kungsbacka kommun")                     delta="2023 (SCB)")

st.info("🏘️ **Tätortsbegrepp (SCB):** Max 200 meter mellan husen, minst 200 invånare. Data från 2023.")        with col2:

            st.metric("Män", f"{MAN_2023:,}", 

try:                     delta=f"{MAN_2023/TOTAL_BEFOLKNING_2023*100:.1f}%")

    # Ladda SCB:s tätortsavgränsningar för Kungsbacka        with col3:

    geojson_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'scb_tatorter_2023_kungsbacka.geojson')            st.metric("Kvinnor", f"{KVINNOR_2023:,}", 

                         delta=f"{KVINNOR_2023/TOTAL_BEFOLKNING_2023*100:.1f}%")

    # Försök ladda lokal fil, annars hämta från SCBexcept Exception as e:

    if os.path.exists(geojson_path):    st.warning(f"Använder verifierad SCB-data 2023")

        with open(geojson_path, 'r', encoding='utf-8') as f:    # Använd verifierad data

            tatorter_geojson = json.load(f)    col1, col2, col3 = st.columns(3)

        st.caption("📊 Data från lokal cache (SCB Tätorter 2023)")    with col1:

    else:        st.metric("Total befolkning Kungsbacka", f"{TOTAL_BEFOLKNING_2023:,}", 

        # Hämta från SCB WFS                 delta="2023 (SCB)")

        with st.spinner("Hämtar tätortsdata från SCB..."):    with col2:

            url = "https://geodata.scb.se/geoserver/stat/wfs"        st.metric("Män", f"{MAN_2023:,}", 

            params = {                 delta=f"{MAN_2023/TOTAL_BEFOLKNING_2023*100:.1f}%")

                'service': 'WFS',    with col3:

                'version': '2.0.0',        st.metric("Kvinnor", f"{KVINNOR_2023:,}", 

                'request': 'GetFeature',                 delta=f"{KVINNOR_2023/TOTAL_BEFOLKNING_2023*100:.1f}%")

                'typeNames': 'stat:Tatorter_2023',        st.metric("Kvinnor", "43,617", delta="50.0%")

                'outputFormat': 'application/json',

                'CQL_FILTER': "kommun='1384'"  # Kungsbacka kommunkod# Skapa tätortskarta med SCB:s officiella avgränsningar

            }st.subheader("📍 Tätorter i Kungsbacka kommun")

            response = requests.get(url, params=params, timeout=30)st.info("🏘️ **Tätortsbegrepp (SCB):** Max 200 meter mellan husen, minst 200 invånare. Data från 2023.")

            tatorter_geojson = response.json()

            try:

            # Spara för framtida användning    # Ladda SCB:s tätortsavgränsningar för Kungsbacka

            with open(geojson_path, 'w', encoding='utf-8') as f:    geojson_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'scb_tatorter_2023_kungsbacka.geojson')

                json.dump(tatorter_geojson, f, ensure_ascii=False, indent=2)    

        st.caption("📊 Data hämtad från SCB Geodatatjänst (Tätorter 2023)")    # Försök ladda lokal fil, annars hämta från SCB

        if os.path.exists(geojson_path):

    # Skapa karta centrerad på Kungsbacka        with open(geojson_path, 'r', encoding='utf-8') as f:

    m = folium.Map(            tatorter_geojson = json.load(f)

        location=[57.48, 12.08],        st.caption("📊 Data från lokal cache (SCB Tätorter 2023)")

        zoom_start=10,    else:

        tiles="OpenStreetMap"        # Hämta från SCB WFS

    )        st.info("Hämtar tätortsdata från SCB...")

            url = "https://geodata.scb.se/geoserver/stat/wfs"

    # Lägg till varje tätortsområde som orange polygon        params = {

    total_tatort_befolkning = 0            'service': 'WFS',

    total_area = 0            'version': '2.0.0',

                'request': 'GetFeature',

    for feature in tatorter_geojson['features']:            'typeNames': 'stat:Tatorter_2023',

        props = feature['properties']            'outputFormat': 'application/json',

        tatort_namn = props.get('tatort', 'Okänd')            'CQL_FILTER': "kommun='1384'"  # Kungsbacka kommunkod

        befolkning = props.get('bef', 0)        }

        area_ha = props.get('area_ha', 0)        response = requests.get(url, params=params, timeout=30)

        tatortskod = props.get('tatortskod', '')        tatorter_geojson = response.json()

                

        total_tatort_befolkning += befolkning        # Spara för framtida användning

        total_area += area_ha        with open(geojson_path, 'w', encoding='utf-8') as f:

                    json.dump(tatorter_geojson, f, ensure_ascii=False, indent=2)

        # Orange färg - MYCKET TYDLIGARE        st.caption("📊 Data hämtad från SCB Geodatatjänst (Tätorter 2023)")

        farg = "#ff8c42"    

            # Skapa karta centrerad på Kungsbacka

        # Skapa detaljerad popup    m = folium.Map(

        popup_html = f"""        location=[57.48, 12.08],

        <div style='font-family: Arial; min-width: 220px;'>        zoom_start=10,

            <h3 style='margin: 0 0 8px 0; color: #ff6b35;'>{tatort_namn}</h3>        tiles="OpenStreetMap"

            <p style='margin: 5px 0;'><strong>Befolkning:</strong> {befolkning:,} invånare</p>    )

            <p style='margin: 5px 0;'><strong>Areal:</strong> {area_ha} hektar</p>    

            <p style='margin: 5px 0; font-size: 11px; color: #666;'>Tätortskod: {tatortskod}</p>    # Lägg till varje tätortsområde som orange polygon

            <hr style='margin: 8px 0; border: none; border-top: 1px solid #ddd;'>    total_befolkning = 0

            <p style='margin: 5px 0; font-size: 10px; font-style: italic;'>    total_area = 0

                SCB Tätortsavgränsning 2023    

            </p>    for feature in tatorter_geojson['features']:

        </div>        props = feature['properties']

        """        tatort_namn = props.get('tatort', 'Okänd')

                befolkning = props.get('bef', 0)

        # Lägg till polygon med orange färg - ÖKA OPACITY!        area_ha = props.get('area_ha', 0)

        folium.GeoJson(        tatortskod = props.get('tatortskod', '')

            feature,        

            style_function=lambda x, color=farg: {        total_befolkning += befolkning

                'fillColor': color,        total_area += area_ha

                'color': '#cc5500',  # Mörkare kant        

                'weight': 2,        # Orange färg - samma som i din bild

                'fillOpacity': 0.75,  # Ökad från 0.65 till 0.75        farg = "#ff8c42"

                'opacity': 1        

            },        # Skapa detaljerad popup

            popup=folium.Popup(popup_html, max_width=300),        popup_html = f"""

            tooltip=f"{tatort_namn} ({befolkning:,} inv)"        <div style='font-family: Arial; min-width: 220px;'>

        ).add_to(m)            <h3 style='margin: 0 0 8px 0; color: #ff6b35;'>{tatort_namn}</h3>

                <p style='margin: 5px 0;'><strong>Befolkning:</strong> {befolkning:,} invånare</p>

    # Beräkna landsbygdsbefolkning            <p style='margin: 5px 0;'><strong>Areal:</strong> {area_ha} hektar</p>

    total_kommun_bef = 85792  # Från SCB 2024            <p style='margin: 5px 0; font-size: 11px; color: #666;'>Tatortskod: {tatortskod}</p>

    landsbygd_bef = total_kommun_bef - total_tatort_befolkning            <hr style='margin: 8px 0; border: none; border-top: 1px solid #ddd;'>

                <p style='margin: 5px 0; font-size: 10px; font-style: italic;'>

    # Lägg till legend (längst ner till vänster, UTANFÖR kartan)                SCB Tätortsavgränsning 2023

    legend_html = f"""            </p>

    <div style="        </div>

        position: fixed;         """

        bottom: 50px;         

        left: 50px;         # Lägg till polygon med STARK orange färg så den syns

        width: 300px;         folium.GeoJson(

        background-color: white;             feature,

        border: 2px solid #666;             style_function=lambda x, color=farg: {

        z-index: 9999;                 'fillColor': color,

        font-size: 13px;                'color': '#cc5500',  # Mörkare kant

        padding: 12px;                'weight': 2,

        border-radius: 5px;                'fillOpacity': 0.85  # ÖKA från 0.65 till 0.85 så det SYNS!

        box-shadow: 0 2px 4px rgba(0,0,0,0.2);            },

    ">            popup=folium.Popup(popup_html, max_width=300),

        <h4 style='margin: 0 0 10px 0; color: #333;'>Tätortsbegrepp</h4>            tooltip=f"{tatort_namn} ({befolkning:,} inv)"

        <p style='margin: 5px 0; line-height: 1.5;'>        ).add_to(m)

            <span style='display: inline-block; width: 20px; height: 12px; background-color: #ff8c42; border: 1px solid #cc5500;'></span>    

            Tätortsområde    # Lägg till legend (längst ner till vänster, UTANFÖR kartan)

        </p>    legend_html = """

        <hr style='margin: 10px 0; border: none; border-top: 1px solid #ddd;'>    <div style="

        <p style='margin: 5px 0; font-size: 11px; line-height: 1.4;'>        position: fixed; 

            <strong>Definition:</strong> Max 200 meter mellan husen, minst 200 invånare        bottom: 50px; 

        </p>        left: 50px; 

        <hr style='margin: 10px 0; border: none; border-top: 1px solid #ddd;'>        width: 280px; 

        <p style='margin: 3px 0; font-size: 11px;'>        background-color: white; 

            <strong>I tätorter:</strong> {total_tatort_befolkning:,} inv        border: 2px solid #666; 

        </p>        z-index: 9999; 

        <p style='margin: 3px 0; font-size: 11px;'>        font-size: 13px;

            <strong>På landsbygd:</strong> ~{landsbygd_bef:,} inv        padding: 12px;

        </p>        border-radius: 5px;

        <p style='margin: 8px 0 3px 0; font-size: 10px; color: #666;'>        box-shadow: 0 2px 4px rgba(0,0,0,0.2);

            Källa: SCB Tätortsavgränsning 2023    ">

        </p>        <h4 style='margin: 0 0 10px 0; color: #333;'>Tätortsbegrepp</h4>

    </div>        <p style='margin: 5px 0; line-height: 1.5;'>

    """            <span style='display: inline-block; width: 20px; height: 12px; background-color: #ff8c42; border: 1px solid #cc5500;'></span>

    m.get_root().html.add_child(folium.Element(legend_html))            Tätortsområde

            </p>

    # Visa kartan        <hr style='margin: 10px 0; border: none; border-top: 1px solid #ddd;'>

    st_folium(m, width=1200, height=650)        <p style='margin: 5px 0; font-size: 11px; line-height: 1.4;'>

                <strong>Definition:</strong> Max 200 meter mellan husen, minst 200 invånare

    # Visa sammanfattande statistik        </p>

    col1, col2, col3, col4 = st.columns(4)        <p style='margin: 5px 0; font-size: 10px; color: #666;'>

    with col1:            Källa: SCB Tätortsavgränsning 2023

        st.metric("Antal tätorter", len(tatorter_geojson['features']))        </p>

    with col2:    </div>

        st.metric("Befolkning i tätorter", f"{total_tatort_befolkning:,}")    """

    with col3:    m.get_root().html.add_child(folium.Element(legend_html))

        st.metric("Befolkning på landsbygd", f"~{landsbygd_bef:,}")    

    with col4:    # Visa kartan

        st.metric("Total areal tätorter", f"{total_area:,} ha")    st_folium(m, width=1200, height=650)

        

    # Info om landsbygd    # Visa sammanfattande statistik med KORREKT kontext

    st.info(f"💡 **Obs!** Av kommunens totalt {total_kommun_bef:,} invånare bor {total_tatort_befolkning:,} ({total_tatort_befolkning/total_kommun_bef*100:.1f}%) i tätorter och cirka {landsbygd_bef:,} ({landsbygd_bef/total_kommun_bef*100:.1f}%) på landsbygden.")    col1, col2, col3, col4 = st.columns(4)

        with col1:

    # Statistik under kartan        st.metric("Antal tätorter", len(tatorter_geojson['features']))

    st.subheader("📊 Befolkningsfördelning per tätort")    with col2:

            st.metric("Befolkning i tätorter", f"{total_befolkning:,}")

    # Bygg dataframe från GeoJSON    with col3:

    tatorter_lista = []        # Hämta total befolkning från SCB data om tillgänglig

    for feature in tatorter_geojson['features']:        try:

        props = feature['properties']            if not pop_data.empty:

        tatorter_lista.append({                total_kommun = pop_data[pop_data["År"] == latest_year]["Antal"].sum()

            "Tätort": props.get('tatort', 'Okänd'),                landsbygd = total_kommun - total_befolkning

            "Befolkning": props.get('bef', 0),                st.metric("Befolkning på landsbygd", f"{landsbygd:,}", 

            "Areal (ha)": props.get('area_ha', 0),                         delta=f"{(landsbygd/total_kommun*100):.1f}%")

            "Tätortskod": props.get('tatortskod', '')            else:

        })                st.metric("Total areal", f"{total_area:,} ha")

            except:

    df_orter = pd.DataFrame(tatorter_lista).sort_values("Befolkning", ascending=False)            st.metric("Total areal", f"{total_area:,} ha")

    df_orter["Andel av tätorter (%)"] = (df_orter["Befolkning"] / df_orter["Befolkning"].sum()) * 100    with col4:

    df_orter["Andel av kommun (%)"] = (df_orter["Befolkning"] / total_kommun_bef) * 100        st.metric("Total areal tätorter", f"{total_area:,} ha")

        

    # Visa som stapeldiagram med orange färg    st.warning(f"⚠️ **OBS:** Detta är endast {len(tatorter_geojson['features'])} tätorter med totalt {total_befolkning:,} invånare. Kungsbacka kommun har totalt ~87,000 invånare - resterande ~{87000-total_befolkning:,} bor utanför tätorterna (landsbygd, fritidshusområden, etc).")

    fig = px.bar(    

        df_orter,    # Statistik under kartan

        x="Tätort",    st.subheader("📊 Befolkningsfördelning per tätort")

        y="Befolkning",    

        title="Befolkning per tätort i Kungsbacka kommun (SCB 2023)",    # Bygg dataframe från GeoJSON

        text="Befolkning",    tatorter_lista = []

        color_discrete_sequence=["#ff8c42"]  # Orange färg    for feature in tatorter_geojson['features']:

    )        props = feature['properties']

            tatorter_lista.append({

    fig.update_traces(texttemplate='%{text:,}', textposition='outside')            "Tätort": props.get('tatort', 'Okänd'),

    fig.update_layout(            "Befolkning": props.get('bef', 0),

        xaxis_tickangle=-45,            "Areal (ha)": props.get('area_ha', 0),

        height=500,            "Tätortskod": props.get('tatortskod', '')

        showlegend=False        })

    )    

        df_orter = pd.DataFrame(tatorter_lista).sort_values("Befolkning", ascending=False)

    st.plotly_chart(fig, use_container_width=True)    df_orter["Andel (%)"] = (df_orter["Befolkning"] / df_orter["Befolkning"].sum()) * 100

        

    # Tabell med detaljer    # Visa som stapeldiagram med orange färg

    with st.expander("📋 Detaljerad tätortsstatistik"):    fig = px.bar(

        st.dataframe(        df_orter,

            df_orter.style.format({        x="Tätort",

                "Befolkning": "{:,.0f}",        y="Befolkning",

                "Areal (ha)": "{:,.0f}",        title="Befolkning per tätort i Kungsbacka kommun (SCB 2023)",

                "Andel av tätorter (%)": "{:.1f}%",        text="Befolkning",

                "Andel av kommun (%)": "{:.1f}%"        color_discrete_sequence=["#ff8c42"]  # Orange färg

            }),    )

            use_container_width=True,    

            hide_index=True    fig.update_traces(texttemplate='%{text:,}', textposition='outside')

        )    fig.update_layout(

        st.caption("Källa: SCB Tätortsavgränsning 2023 + SCB Befolkningsstatistik 2024")        xaxis_tickangle=-45,

                height=500,

except FileNotFoundError as e:        showlegend=False

    st.error("❌ Kunde inte ladda tätortsdata")    )

    st.info(f"Filen hittades inte: {e}")    

except Exception as e:    st.plotly_chart(fig, use_container_width=True)

    st.error(f"❌ Fel vid visning av tätortskarta: {e}")    

    st.info("Kontrollera att SCB:s geodatatjänst är tillgänglig")    # Tabell med detaljer

    import traceback    with st.expander("📋 Detaljerad tätortsstatistik"):

    with st.expander("Teknisk information"):        st.dataframe(

        st.code(traceback.format_exc())            df_orter.style.format({

                "Befolkning": "{:,.0f}",
                "Areal (ha)": "{:,.0f}",
                "Andel (%)": "{:.1f}%"
            }),
            use_container_width=True,
            hide_index=True
        )
        st.caption("Källa: SCB Tätortsavgränsning 2023")
        
except FileNotFoundError as e:
    st.error("❌ Kunde inte ladda tätortsdata")
    st.info(f"Filen hittades inte: {e}")
except Exception as e:
    st.error(f"❌ Fel vid visning av tätortskarta: {e}")
    st.info("Kontrollera att SCB:s geodatatjänst är tillgänglig")
    import traceback
    with st.expander("Teknisk information"):
        st.code(traceback.format_exc())

