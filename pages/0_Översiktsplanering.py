"""
Sida för Översiktsplanering - Uppföljning av översiktsplanen med planbesked och Antura-data
"""

import streamlit as st
import json
import os
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go

st.set_page_config(
    page_title="Översiktsplanering - Kungsbacka",
    page_icon="📋",
    layout="wide"
)

# Ladda översiktsplanens kunskapsbas
@st.cache_data
def load_oversiktsplan_knowledge():
    """Läser in kunskapsbasen om översiktsplanen"""
    try:
        knowledge_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'oversiktsplan_kunskap.json')
        with open(knowledge_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Kunde inte läsa översiktsplanens kunskapsbas: {e}")
        return None

def get_ort_info(projektnamn, op_knowledge):
    """Hittar ortinformation baserat på projektnamn"""
    if not op_knowledge:
        return None
    
    projektnamn_lower = projektnamn.lower()
    
    # Sök i prioriterade orter
    for ort_namn, ort_info in op_knowledge.get('prioriterade_orter', {}).items():
        if ort_namn.lower() in projektnamn_lower:
            return {
                'ort': ort_namn,
                'typ': ort_info['typ'],
                'prioritet': ort_info['prioritet'],
                'beskrivning': ort_info['beskrivning'],
                'utvecklingsomraden': ', '.join(ort_info.get('utvecklingsområden', [])),
                'mal': ort_info.get('mål', '')
            }
    
    # Sök i övriga orter
    for ort_namn, ort_info in op_knowledge.get('ovriga_orter', {}).items():
        if ort_namn.lower() in projektnamn_lower:
            return {
                'ort': ort_namn,
                'typ': ort_info['typ'],
                'prioritet': ort_info['prioritet'],
                'beskrivning': ort_info['beskrivning'],
                'utvecklingsomraden': '',
                'mal': ort_info.get('mål', '')
            }
    
    # Om ingen match - returnera grundläggande info
    return {
        'ort': 'Okänd ort',
        'typ': 'Ej klassificerad',
        'prioritet': 'Ej angiven',
        'beskrivning': 'Ingen information tillgänglig',
        'utvecklingsomraden': '',
        'mal': ''
    }

def plot_planbesked_pie(labels, values, colors):
    """Ritar ett cirkeldiagram med anpassade färger och etiketter"""
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors, line=dict(color='#fff', width=2)),
        textinfo='label+percent',
        insidetextorientation='radial',
        pull=[0.05 if v == max(values) else 0 for v in values],
        hole=0.15
    )])
    fig.update_traces(textfont_size=16)
    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        height=320
    )
    st.plotly_chart(fig, use_container_width=True)


def show_antura_section():
    """Visar Antura planbesked-sektionen med båda tabellerna"""
    
    st.markdown("""
    <div style='font-size:1em; color:#888; margin-bottom:1em;'>
    (Denna sektion kommer att uppdateras automatiskt när Antura-integration är på plats. Rubrikerna nedan är statiska, data kommer från Antura.)
    </div>
    <div style='display:flex; gap:32px;'>
        <div style='flex:1;'>
            <table style='width:100%; border-collapse:collapse; border:1px solid #ccc;'>
                <tr>
                    <td rowspan='3' style='background:#c19a9a; color:black; font-weight:bold; padding:10px; font-size:0.9em; writing-mode:vertical-rl; text-orientation:mixed; width:15%; text-align:center;'>BOSTÄDER</td>
                    <td rowspan='1' style='background:#c19a9a; color:black; font-weight:bold; padding:8px; font-size:0.85em; writing-mode:vertical-rl; text-orientation:mixed; width:15%; text-align:center;'>Kungsbacka stad</td>
                    <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.75em; width:50%;'>
                            Gåsevadholm S:1<br>
                            <u>Bäratorr</u> 2:1 och 1:12 samt Kungsbacka 5:1<br>
                            Hammerö 7:3<br>
                            Hammerö 13:7 m.fl.<br>
                            Lärkan 14<br>
                            Ysby 3:4 m.fl.<br>
                            Fors 1:387<br>
                            Aranäs 10 och 15<br>
                            Store Lyckor 1 och 2
                    </td>
                    <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center; width:10%;'></td>
                    <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center; width:10%;'><strong>Xx st</strong></td>
                </tr>
                <tr>
                    <td rowspan='1' style='background:#c19a9a; color:black; font-weight:bold; padding:8px; font-size:0.85em; writing-mode:vertical-rl; text-orientation:mixed; text-align:center;'>Åsa</td>
                    <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.75em;'>
                            Åsa 5:197 och 5:70<br>
                            Åsa 5:161 och Åsa 5:101<br>
                            Åsa 5:96<br>
                            <u>Kläppa</u> 1:4 daterat 2023-10-28<br>
                            Åsa 4:146 och Åsa 4:152<br>
                            Åsa 5:153 och 5:89<br>
                            Åsa 3:14 och Åsa 5:219
                    </td>
                    <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                    <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                </tr>
                <tr>
                    <td rowspan='1' style='background:#c19a9a; color:black; font-weight:bold; padding:8px; font-size:0.85em; writing-mode:vertical-rl; text-orientation:mixed; text-align:center;'>Anneberg</td>
                    <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.75em;'>
                            Älafors 4:12<br>
                            Lerberg 16:40, 3:9 och 3:11<br>
                            Älafors 4:12 (Skifte 23)
                    </td>
                    <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                    <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                </tr>
            </table>
        </div>
        <div style='flex:1;'>
            <table style='width:100%; border-collapse:collapse; border:1px solid #ccc;'>
                <tr>
                    <td rowspan='2' style='background:#c19a9a; color:black; font-weight:bold; padding:10px; font-size:0.9em; writing-mode:vertical-rl; text-orientation:mixed; width:15%; text-align:center;'>BOSTÄDER</td>
                    <td rowspan='1' style='background:#c19a9a; color:black; font-weight:bold; padding:8px; font-size:0.85em; writing-mode:vertical-rl; text-orientation:mixed; width:15%; text-align:center;'>Övriga orter</td>
                    <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.75em; width:50%;'>
                            del av <u>Bångsbå</u> 4:1<br>
                            Lyngås 3:3<br>
                            Bäcken 1:31 m.fl.<br>
                            Vallda 5:11<br>
                            Frillesås-Rya 2:11<br>
                            Må 2:210<br>
                            Frillesås-rya 2:3 och <u>Lurendal</u> 1:3<br>
                            Kyvík 5:380
                    </td>
                    <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center; width:10%;'>Väg 158, C<br>Väg 158, utvidgad<br>ort</td>
                    <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center; width:10%;'><strong>Xx st</strong></td>
                </tr>
                <tr>
                    <td rowspan='1' style='background:#c19a9a; color:black; font-weight:bold; padding:8px; font-size:0.85em; writing-mode:vertical-rl; text-orientation:mixed; text-align:center;'>Utanför ort</td>
                    <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.75em;'>
                            Vallda 20:3, <u>Bröndom</u> 1:2 och del av Vallda 20:59*<br>
                            Bukärr 1:5*<br>
                            Gräppås 2:13<br>
                            Hede 1:53,
                    </td>
                    <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                    <td style='background:#f5f5f5; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                </tr>
                <tr>
                    <td rowspan='4' style='background:#e6b3ff; color:black; font-weight:bold; padding:10px; font-size:0.75em; writing-mode:vertical-rl; text-orientation:mixed; text-align:center;'>MARK FÖR NÄRINGSLIV</td>
                    <td rowspan='1' style='background:#e6b3ff; color:black; font-weight:bold; padding:8px; font-size:0.75em; writing-mode:vertical-rl; text-orientation:mixed; text-align:center;'>Åsa stad</td>
                    <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.75em;'>
                            Åskatorp 21:1 mfl<br>
                            Varla 2:423<br>
                            Varla 2:412<br>
                            Hede 3:12 skifte 1<br>
                            Vallda 23:2<br>
                            Vallda 5:11*
                    </td>
                    <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                    <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.8em; text-align:center;'><strong>Xx ha</strong></td>
                </tr>
                <tr>
                    <td rowspan='1' style='background:#d9b3ff; color:black; font-weight:bold; padding:8px; font-size:0.75em; writing-mode:vertical-rl; text-orientation:mixed; text-align:center;'>Fjärås stn</td>
                    <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.75em;'>Väg 158,<br>trafikintensivt</td>
                    <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                    <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                </tr>
                <tr>
                    <td rowspan='1' style='background:#d9b3ff; color:black; font-weight:bold; padding:8px; font-size:0.75em; writing-mode:vertical-rl; text-orientation:mixed; text-align:center;'>KBA stad</td>
                    <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.75em;'></td>
                    <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                    <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                </tr>
                <tr>
                    <td rowspan='1' style='background:#d9b3ff; color:black; font-weight:bold; padding:8px; font-size:0.75em; writing-mode:vertical-rl; text-orientation:mixed; text-align:center;'>Vallda</td>
                    <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.75em;'></td>
                    <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                    <td style='background:#f0e6ff; color:black; padding:8px; font-size:0.8em; text-align:center;'></td>
                </tr>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Avdelare före "Ej startade planer och program" tabellen ---
    st.markdown("---")
    
    # --- ANDRA TABELLEN - "Ej startade planer och program" ---
    st.markdown("""
    <div style='font-size:1.2em; font-weight:bold; margin-bottom:0.5em;'>Ej startade planer och program</div>
    <div style='font-size:1em; color:#888; margin-bottom:1em;'>
    (Tabellen förberedd för automatisk data från Antura. Ikoner och struktur enligt original.)
    </div>
    """, unsafe_allow_html=True)
    
    # Tabell med kolumner för olika orter
    st.markdown("""
    <table style='width:100%; border-collapse:collapse; border:1px solid #ccc;'>
        <tr style='background:#f5f5f5; font-weight:bold; font-size:0.85em;'>
            <td style='border:1px solid #ddd; padding:8px; width:20%; text-align:center; background:#e8e8e8; color:#333;'>KUNGSBACKA STAD</td>
            <td style='border:1px solid #ddd; padding:8px; width:20%; text-align:center; background:#e8e8e8; color:#333;'>ÅSA</td>
            <td style='border:1px solid #ddd; padding:8px; width:20%; text-align:center; background:#e8e8e8; color:#333;'>ANNEBERG</td>
            <td style='border:1px solid #ddd; padding:8px; width:20%; text-align:center; background:#e8e8e8; color:#333;'>ÖVRIGA ORTER</td>
            <td style='border:1px solid #ddd; padding:8px; width:20%; text-align:center; background:#e8e8e8; color:#333;'>UTANFÖR ORT</td>
        </tr>
        <tr>
            <td style='border:1px solid #ddd; padding:12px; vertical-align:top; font-size:0.75em; background:#ffffff; color:#333;'>
                <div style='margin-bottom:10px;'>
                    <span style='font-size:1.2em;'>🏠</span> <strong>Bostäder</strong><br>
                    2021 - DP Tölö ängar syd, del 2<br>
                    2021 - DP Tölö ängar 3, del 2<br>
                    2021 - DP Voxlöv Sydöst<br>
                    2021 - DP Voxlöv Sydväst<br>
                    2021 - DP Sydöstra Centrum etapp 4<br>
                    2021 - DP Sydöstra Centrum etapp 3<br>
                    2020 - DP Södra Porten<br>
                    2021 - DP Kv. Kronan 5<br>
                    2017 - DP Aranäs 15<br>
                    2016 - DP Gertrud<br>
                    2014 - PR Kungsgärde
                </div>
                <div style='margin-bottom:10px;'>
                    <span style='font-size:1.2em;'>🏭</span> <strong>Mark för näringsliv</strong><br>
                    2021 - DP Hede Station –<br>
                    2014 - DP Kungsmässan, etapp 2
                </div>
                <div>
                    <span style='font-size:1.2em;'>🛣️</span> <strong>Infrastruktur</strong><br>
                    DP fyra körfält Kungsgatan
                </div>
            </td>
            <td style='border:1px solid #ddd; padding:12px; vertical-align:top; font-size:0.75em; background:#ffffff; color:#333;'>
                <div style='margin-bottom:10px;'>
                    <span style='font-size:1.2em;'>🏠</span> <strong>Bostäder</strong><br>
                    2014 - DP Ölmanäs 31:1 och 7:10<br>
                    2019 - DP Åsa 2:6, 3:11 Boviera<br>
                    2020 - DP Åsa 4:118 m.fl.
                </div>
                <div style='margin-bottom:10px;'>
                    <span style='font-size:1.2em;'>🏭</span> <strong>Mark för näringsliv</strong><br>
                    2019 - PR verksamheter södra<br>
                    Anneberg
                </div>
            </td>
            <td style='border:1px solid #ddd; padding:12px; vertical-align:top; font-size:0.75em; background:#ffffff; color:#333;'>
                <div style='margin-bottom:10px;'>
                    <span style='font-size:1.2em;'>🏠</span> <strong>Bostäder</strong><br>
                    2019 - PR bostäder Skärby 2:4 mfl
                </div>
                <div style='margin-bottom:10px;'>
                    <span style='font-size:1.2em;'>🏭</span> <strong>Mark för näringsliv</strong><br>
                    2017 - DP Duvehed 2:11, Fjärås<br>
                    lantmanna
                </div>
                <div>
                    <span style='font-size:1.2em;'>🏖️</span> <strong>Besöksnäring</strong><br>
                    2018 - PR Hamnplan, Gottskär
                </div>
            </td>
            <td style='border:1px solid #ddd; padding:12px; vertical-align:top; font-size:0.75em; background:#ffffff; color:#333;'>
                <div style='margin-bottom:10px;'>
                    <span style='font-size:1.2em;'>🏠</span> <strong>Bostäder</strong><br>
                    2020 - DP Spårhaga 1:9<br>
                    2019 - DP Särö 1:493<br>
                    2019 - PR Vallda-Backa 1:6<br>
                    2018 - DP Skörvallla 1:49-1:51 och 1:61<br>
                    2017 - DP Särö 1:526<br>
                    2015 - DP Spårhaga 2:139<br>
                    2014 - DP Särö centrum östra delen
                </div>
            </td>
            <td style='border:1px solid #ddd; padding:12px; vertical-align:top; font-size:0.75em; background:#ffffff; color:#333;'>
                <div>
                    <span style='font-size:1.2em;'>🏠</span> <strong>Bostäder</strong><br>
                    2019 - PR bostäder Ölmanäs 6:80<br>
                    2018 - PR Rosendal 1:2 och 1:3<br>
                    2015 - DP Hjälmared 1:11 och 25:3
                </div>
            </td>
        </tr>
    </table>
    """, unsafe_allow_html=True)


# === HUVUDSIDA ===
st.title("📋 Översiktsplanering")
st.markdown("""
Denna sida visar uppföljning av översiktsplanens genomförande med planbesked, prognoser och utfall.
Data från Antura kommer att integreras automatiskt när systemet är klart.
""")

# Tabs för olika vyer
tabs = st.tabs(["Inledning", "Uppskattning", "Prognos", "Utfall", "Tematisk överblick"])

with tabs[0]:
    # INLEDNING - Översikt från gamla Översikt-sidan
    st.markdown("Huvudnyckeltal och översiktlig information om kommunens utveckling")

    # Snabba nyckeltal
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total befolkning",
            "106,084",
            delta="+288 från föregående år",
            help="Senaste data från SCB 2024"
        )

    with col2:
        st.metric(
            "Planbesked (2022-2025)",
            "49 st",
            delta="35 positiva, 14 negativa",
            help="Följsamhet till översiktsplan"
        )

    with col3:
        st.metric(
            "ÖP-följsamhet",
            "71%",
            delta="Positiva planbesked",
            help="Andel planbesked i enlighet med översiktsplanen"
        )

    with col4:
        st.metric(
            "Bostadsproduktion",
            "847 st/år",
            delta="Målsättning: 1000 st/år",
            help="Nyproducerade bostäder per år"
        )

    st.markdown("---")

    # Översiktlig information
    st.subheader("Översiktlig kommuninformation")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 📈 Befolkningsutveckling
        - Kungsbacka växer stadigt med ca 1% per år
        - Stark inflyttning till kommunen
        - Attraktiv för barnfamiljer och unga vuxna
        
        **Se detaljerad befolkningsanalys under "Befolkning"**
        """)
        
        st.markdown("""
        ### 🏘️ Bostadsutveckling
        - Fokus på förtätning i tätorter
        - Kungsbacka stad prioriterad utvecklingsort
        - Åsa och Anneberg viktiga tillväxtcentra
        """)

    with col2:
        st.markdown("""
        ### 📋 Översiktsplanering
        - Uppföljning av ÖP-följsamhet pågår
        - 71% av planbesked följer översiktsplanen
        - Kontinuerlig dialog med byggherrar
        
        **Se detaljerad uppföljning under "Uppskattning", "Prognos", "Utfall" och "Tematisk överblick"**
        """)
        
        st.markdown("""
        ### 🗺️ Geografisk spridning
        - Kungsbacka stad: ~32,500 invånare
        - Åsa: ~8,900 invånare
        - Särö: ~4,200 invånare
        - Övriga orter och landsbygd
        """)

    st.markdown("---")

    # Senaste uppdateringar
    st.subheader("Senaste aktiviteter")

    from datetime import datetime
    today = datetime.now()

    activities = [
        {"date": today.strftime("%Y-%m-%d"), "activity": "Befolkningsdata uppdaterad från SCB", "type": "data"},
        {"date": today.strftime("%Y-%m-%d"), "activity": "Planbesked registrerade i systemet", "type": "planering"},
    ]

    for activity in activities:
        if activity["type"] == "data":
            st.info(f"**{activity['date']}** - {activity['activity']}")
        else:
            st.success(f"**{activity['date']}** - {activity['activity']}")


with tabs[1]:
    # UPPSKATTNING - Planbesked
    # Rubrik över kartan
    # Hämta datumintervall dynamiskt i framtiden, nu hårdkodat
    start_date = "2022"
    end_date = "april 2025"
    st.markdown(f"""
    <div style='font-size:1.3em; font-weight:bold; margin-bottom:0.5em;'>
        Planbesked<br>
        <span style='font-size:0.9em; font-weight:normal;'>
            {start_date} – {end_date} <br>
            <span style='font-size:0.85em; color:#888;'>
            (Den här datan kommer att ändras automatiskt när vi får in ny data)
            </span>
        </span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # Ladda planbesked-data (geojson)
    # Läs in planbesked.json (GeoJSON)
    planbesked_path = os.path.join(os.path.dirname(__file__), "..", "planbesked.json")
    
    if os.path.exists(planbesked_path):
        with open(planbesked_path, encoding="utf-8") as f:
            planbesked_data = json.load(f)

        # Ladda översiktsplan-kunskapen
        op_knowledge = load_oversiktsplan_knowledge()

        # Skapa karta över Kungsbacka
        m = folium.Map(location=[57.492, 12.073], zoom_start=10, tiles="cartodbpositron")

        # Lägg till planbesked-punkter/polygoner
        for feature in planbesked_data["features"]:
            geom_type = feature["geometry"]["type"]
            props = feature["properties"]
            projektnamn = props.get("projektnamn", "Planbesked")
            
            # Hämta ortinformation från kunskapsbasen
            ort_info = get_ort_info(projektnamn, op_knowledge)
            
            # Skapa rik popup med all information
            popup_html = f"""
            <div style='width: 300px; font-family: Arial, sans-serif;'>
                <h4 style='margin:0 0 10px 0; color:#2c3e50;'>{projektnamn}</h4>
                <hr style='margin:10px 0; border:1px solid #ddd;'>
                <p style='margin:5px 0;'><b>📍 Ort:</b> {ort_info['ort']}</p>
                <p style='margin:5px 0;'><b>🏷️ Typ:</b> {ort_info['typ']}</p>
                <p style='margin:5px 0;'><b>⭐ Prioritet:</b> {ort_info['prioritet']}</p>
                <p style='margin:8px 0;'><b>📝 Beskrivning:</b><br>{ort_info['beskrivning']}</p>
            """
            
            if ort_info['utvecklingsomraden']:
                popup_html += f"<p style='margin:8px 0;'><b>🏗️ Utvecklingsområden:</b><br>{ort_info['utvecklingsomraden']}</p>"
            
            if ort_info['mal']:
                popup_html += f"<p style='margin:8px 0;'><b>🎯 Mål:</b><br>{ort_info['mal']}</p>"
            
            popup_html += "</div>"
            
            if geom_type == "Point":
                coords = feature["geometry"]["coordinates"][::-1]  # lat, lon
                folium.CircleMarker(
                    location=coords,
                    radius=7,
                    color="#3388ff",
                    fill=True,
                    fill_color="#3388ff",
                    fill_opacity=0.7,
                    popup=folium.Popup(popup_html, max_width=320)
                ).add_to(m)
            elif geom_type == "Polygon":
                folium.GeoJson(
                    feature, 
                    name=projektnamn,
                    popup=folium.Popup(popup_html, max_width=320)
                ).add_to(m)

        # --- Kartan och sammanställningsrutor i samma rad ---
        col_map, col_sum1, col_sum2 = st.columns([2,1,1])
        with col_map:
            st_folium(m, width=700, height=500)
        with col_sum1:
            st.markdown("""
            <div style='background-color:#fff; border:2px solid #228B22; border-radius:10px; padding:1em; color:#222; margin-bottom:0.5em;'>
            <b>Sammanställning – <span style='color:#228B22;'>35 st ja</span></b><br>
            71% prioriterade orter/<br>verksamhetsområde varav<br>
            40% i staden<br>
            9% utanför utvecklingsort
            </div>
            """, unsafe_allow_html=True)
        with col_sum2:
            st.markdown("""
            <div style='background-color:#fff; border:2px solid #B22222; border-radius:10px; padding:1em; color:#222; margin-bottom:0.5em;'>
            <b>Sammanställning – <span style='color:#B22222;'>14 st nej</span></b><br>
            29% i prioriterade orter<br>
            57% i övriga orter<br>
            14% utanför utvecklingsort
            </div>
            """, unsafe_allow_html=True)

        # POSITIVA/NEGATIVA planbesked-rutor direkt under kartan och sammanställning
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style='background-color:#eafaf1; border:2px solid #b7e4c7; border-radius:10px; padding:1em; color:#222;'>
            <b>Positiva - <span style='color:#228B22;'>XX</span></b><br>
            <u>Bostäder:</u><br>
            • Kungsbacka stad – ...<br>
            • Åsa – ...<br>
            • Anneberg – ...<br>
            • Övriga orter – ...<br>
            <br>
            <u>Mark för näringsliv</u> – ...<br>
            <u>Offentlig service</u> – ...<br>
            <u>Utanför utvecklingsort</u> – ...<br>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div style='background-color:#fff0f0; border:2px solid #f5c2c7; border-radius:10px; padding:1em; color:#222;'>
            <b>Negativa - <span style='color:#B22222;'>XX</span></b><br>
            Kungsbacka stad – ...<br>
            Åsa – ...<br>
            Övriga orter – ...<br>
            Utanför utvecklingsort – ...<br>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ planbesked.json hittades inte. Kartan kan inte visas.")

    # --- Avdelare före cirkeldiagrammen ---
    st.markdown("---")

    # --- Två cirkeldiagram i rad ---
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style='margin-top:2em; margin-bottom:0.5em;'>
        <span style='font-size:1.2em; font-weight:bold;'>Andel positiva planbesked för bostäder 2022–2025</span>
        </div>
        """, unsafe_allow_html=True)
        plot_planbesked_pie(
            labels=["Kungsbacka stad", "Åsa och Anneberg", "Övriga orter"],
            values=[47, 30, 23],
            colors=["#a63d1c", "#f7b08a", "#fbe7de"]
        )
    with col2:
        st.markdown("""
        <div style='margin-top:2em; margin-bottom:0.5em;'>
        <span style='font-size:1.2em; font-weight:bold;'>Bostadsförsörjningsplan, andel bostäder 2025–2029</span>
        </div>
        """, unsafe_allow_html=True)
        plot_planbesked_pie(
            labels=["Kungsbacka stad", "Åsa och Anneberg", "Övriga orter"],
            values=[60, 15, 25],
            colors=["#a63d1c", "#f7b08a", "#fbe7de"]
        )

    # --- Avdelare före Antura-tabellen ---
    st.markdown("---")

    # --- Antura-tabell i expander (rullgardin) ---
    with st.expander("Planbesked i Antura – vad vi vill kunna få ut", expanded=False):
        show_antura_section()

with tabs[2]:
    st.subheader("Prognos")
    st.info("Här kan du visa prognoser och framtidsscenarier.")

with tabs[3]:
    st.subheader("Utfall")
    st.info("Här kan du visa utfall och faktisk utveckling.")

with tabs[4]:
    st.subheader("Tematisk överblick")
    st.info("Här kan du visa kartor, teman eller annan översiktlig information.")
