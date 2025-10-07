# 🏙️ Kungsbacka Planeringsdashboard

Ett omfattande Streamlit-baserat verktyg för uppföljning av översiktsplanering och strategisk utveckling i Kungsbacka kommun.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📋 Innehållsförteckning

- [Om Projektet](#-om-projektet)
- [Funktioner](#-funktioner)
- [Teknisk Stack](#-teknisk-stack)
- [Installation](#-installation)
- [Användning](#-användning)
- [Projektstruktur](#-projektstruktur)
- [API-integration](#-api-integration)
- [Deployment](#-deployment)
- [Bidra](#-bidra)
- [Licens](#-licens)

## 🎯 Om Projektet

Kungsbacka Planeringsdashboard är ett webbaserat analysverktyg som hjälper kommunala planerare och beslutsfattare att:

- **Följa upp** översiktsplanens genomförande och måluppfyllelse
- **Analysera** befolkningsutveckling, demografi och prognoser
- **Visualisera** planbesked, byggprojekt och utvecklingsområden på interaktiva kartor
- **Jämföra** kommunala nyckeltal med andra kommuner via Kolada
- **Hämta** aktuell statistik från SCB, Kolada och andra öppna datakällor
- **Utvärdera** bostadsproduktion, infrastruktur och samhällsservice

## ✨ Funktioner

### 🏠 Huvudfunktioner

#### 1. **Startsida (Start.py)**
- Översikt över dashboardens funktionalitet
- Snabbnavigation till olika vyer
- Senaste datauppdateringar

#### 2. **Styrdokument (0_Styrdokument.py)**
- Samling av kommunala styrdokument
- Direktlänkar till översiktsplaner, strategier och policy-dokument
- Strukturerad presentation av planeringsdokument

#### 3. **Översiktsplanering (0_Översiktsplanering.py)**
- Uppföljning av översiktsplanens genomförande
- ÖP-följsamhet för planbesked
- Geografisk visualisering av utvecklingsområden

#### 4. **Nyckeltal (1_Nyckeltal.py)**
- Övergripande KPI:er och indikatorer
- Måluppfyllelse med progress bars
- Bostadsproduktion, återvinning och miljömål
- Visuella trendanalyser

#### 5. **Befolkning (2_Befolkning.py)**
- Detaljerad befolkningsanalys från SCB
- Befolkningsförändringar (födda, döda, in/utvandring)
- Demografiska prognoser
- Ålderspyramider och könsfördelning

#### 6. **Kolada-integration (3_Kolada.py)**
- Live-data från Kommun- och Landstingsdatabasen
- Jämförelser med andra kommuner
- Över 50+ kommunala nyckeltal:
  - Folkmängd och demografi
  - Bygglov och detaljplaner
  - Ekonomi och verksamhet
  - Utbildning och barnomsorg
  - Äldreomsorg och social service
  - Miljö och hållbarhet

#### 7. **Boendebarometer (4_Boendebarometer.py)**
- Analys av bostadsmarknad
- Bostadstyper och fördelning
- Nyproduktion och bygglov

#### 8. **Värmekarta (5_Värmekarta.py)**
- Visuell densitetsanalys
- Befolkningstäthet per område
- Utvecklingskoncentration

#### 9. **Ortanalys (6_Ortanalys.py)**
- Detaljerad analys per ort
- Orters roll i kommunstrukturen
- Prioriterade orter vs. övriga

#### 10. **SCB Bostäder (8_SCB_Bostäder.py)**
- Bostadsstatistik från SCB
- Lägenhetstyper och hustyper
- Historiska trender

#### 11. **AI-Assistent (11_AI_Assistent.py)**
- Intelligent chatbot för planering
- Kunskapsbas om översiktsplanen
- Integration med kommunal data
- Automatiserade analyser

#### 12. **Karttjänst (12_Karttjänst.py)**
- Interaktiva kartor med Folium
- Planbesked och byggprojekt
- Ortsavgränsningar
- GeoJSON-visualisering
- Utvecklingsområden och planeringsinformation

#### 13. **Admin (99_Admin.py)**
- Systemadministration
- Cache-hantering
- API-status och hälsokontroller

## 🛠️ Teknisk Stack

### Huvudramverk
- **Streamlit** (1.28+) - Webb-framework för datavetenskap
- **Python** (3.11+) - Programmeringsspråk

### Datahantering & Analys
- **Pandas** (2.0+) - Dataanalys och manipulation
- **NumPy** (1.24+) - Numeriska beräkningar
- **Requests** (2.31+) - HTTP-förfrågningar till API:er

### Visualisering
- **Plotly** (5.15+) - Interaktiva grafer och diagram
- **Matplotlib** (3.7+) - Statistiska visualiseringar
- **Folium** (0.14+) - Interaktiva kartor
- **Streamlit-Folium** (0.15+) - Folium-integration i Streamlit

### Geospatial
- **GeoPandas** (0.13+) - Geografisk dataanalys
- **Shapely** (2.0+) - Geometrisk manipulation
- **PyProj** (3.6+) - Kartprojektioner

### Övriga
- **Pillow** (10+) - Bildhantering
- **python-pptx** (0.7+) - PowerPoint-parsing
- **BeautifulSoup4** - HTML/XML-parsing

## � Installation

### Förutsättningar
- Python 3.11 eller högre
- pip (Python package manager)
- Git

### Steg-för-steg installation

1. **Klona repositoryt**
```bash
git clone https://github.com/RaquelSandblad/indikator-dashboard.git
cd indikator-dashboard
```

2. **Skapa virtuell miljö (rekommenderas)**
```bash
python -m venv venv
source venv/bin/activate  # På Windows: venv\Scripts\activate
```

3. **Installera beroenden**
```bash
pip install -r requirements.txt
```

4. **Verifiera installation**
```bash
python --version  # Bör vara 3.11+
streamlit --version
```

## 🚀 Användning

### Lokal utveckling

1. **Starta dashboarden**
```bash
streamlit run Start.py
```

2. **Öppna i webbläsare**
- Streamlit öppnar automatiskt på `http://localhost:8501`
- Om inte, navigera manuellt till URL:en som visas i terminalen

3. **Navigera i dashboarden**
- Använd sidomenyn till vänster för att välja olika vyer
- Interagera med grafer, kartor och filter
- Exportera data via nedladdningsknappar

### Miljövariabler (Valfritt)

Skapa en `.env`-fil i projektets rot för API-nycklar:
```bash
# .env
SCB_API_KEY=din_nyckel_här  # Frivilligt, SCB är öppet
KOLADA_API_KEY=din_nyckel_här  # Frivilligt, Kolada är öppet
```

## 📁 Projektstruktur

```
indikator-dashboard/
│
├── Start.py                         # Startsida och huvudnavigation
├── config.py                        # Konfiguration för API:er och datakällor
├── requirements.txt                 # Python-beroenden
├── runtime.txt                      # Python-version för deployment
├── Procfile                         # Heroku deployment config
├── railway.toml                     # Railway deployment config
│
├── pages/                           # Streamlit-sidor (undersidor)
│   ├── 0_Styrdokument.py           # Kommunala styrdokument
│   ├── 0_Översiktsplanering.py     # ÖP-uppföljning
│   ├── 1_Nyckeltal.py              # KPI:er och indikatorer
│   ├── 2_Befolkning.py             # Befolkningsanalys (SCB)
│   ├── 3_Kolada.py                 # Kolada-integration
│   ├── 4_Boendebarometer.py        # Bostadsmarknadsanalys
│   ├── 5_Värmekarta.py             # Densitetsvisualisering
│   ├── 6_Ortanalys.py              # Ortsspecifik analys
│   ├── 8_SCB_Bostäder.py           # SCB bostadsstatistik
│   ├── 11_AI_Assistent.py          # AI-driven planerings­assistent
│   ├── 12_Karttjänst.py            # Interaktiva kartor
│   └── 99_Admin.py                 # Systemadministration
│
├── data/                            # Data och datakonnektorer
│   ├── kolada_connector.py         # Kolada API-klient
│   ├── scb_connector.py            # SCB API-klient
│   ├── infonet_loader.py           # PowerPoint data-parser
│   ├── oversiktsplan_kunskap.json  # ÖP kunskapsbas för AI
│   └── orter_avgransningar.geojson # Geografiska gränser
│
├── components/                      # Återanvändbara UI-komponenter
│   └── ui_components.py            # Gemensamma UI-element
│
├── data_sources.py                  # Förbättrade datakällor
├── enhanced_data_sources.py         # Avancerade datakällor
├── indicators.py                    # Indikatorberäkningar
├── utils.py                         # Hjälpfunktioner
├── maps.py                          # Kartfunktionalitet
├── map_integration.py               # Kartintegration
│
├── cache/                           # API-cache för prestanda
├── backups/                         # Säkerhetskopior av kod
├── __pycache__/                     # Python bytecode
│
└── docs/                            # Dokumentation
    ├── DEPLOYMENT_GUIDE.md          # Deployment-instruktioner
    ├── API_keys_and_endpoints.md    # API-dokumentation
    ├── PROJEKTPLAN_2_VECKOR.md      # Projektplan
    └── STATUS_RAPPORT.md            # Statusrapporter
```

## 🔌 API-integration

Dashboarden integrerar med flera öppna API:er:

### 1. **SCB (Statistiska Centralbyrån)**
- **Bas-URL**: `https://api.scb.se/OV0104/v1/doris/sv/ssd`
- **Autentisering**: Ingen nyckel krävs (öppet API)
- **Data**: 
  - Befolkning per ålder, kön, år
  - Befolkningsförändringar
  - Hushållsstatistik
  - Bostäder och byggnader
  - Inkomster och sysselsättning

**Exempel användning:**
```python
from data.scb_connector import SCBConnector

scb = SCBConnector()
befolkning = scb.get_population_data(region="1380")  # Kungsbacka
```

### 2. **Kolada (Kommun- och Landstingsdatabasen)**
- **Bas-URL**: `http://api.kolada.se/v2`
- **Autentisering**: Ingen nyckel krävs (öppet API)
- **Data**: 
  - 6000+ kommunala nyckeltal
  - Kommunjämförelser
  - Tidsserier över flera år
  - Verksamhetsstatistik

**Exempel användning:**
```python
from data.kolada_connector import kolada

# Hämta folkmängd
data = kolada.get_latest_value("N01951")

# Jämför med andra kommuner
jamforelse = kolada.compare_municipalities(
    kpi="N01951",
    municipalities=["1380", "1384", "1440"]
)
```

### 3. **GIS-data (GeoJSON)**
- Kommunens egna geodata
- Ortsavgränsningar
- Planbesked och byggprojekt
- Översiktsplaneområden

### 4. **Infonet (PowerPoint-parser)**
- Läser data från kommunens PowerPoint-presentationer
- Extraherar tabeller och nyckeltal
- Automatisk uppdatering från presentationer

## 🌐 Deployment

Dashboarden kan deployeras på flera plattformar:

### Streamlit Cloud (Rekommenderat - Gratis)

1. Skapa konto på [share.streamlit.io](https://share.streamlit.io)
2. Anslut GitHub-repository
3. Välj `Start.py` som huvudfil
4. Deployas automatiskt

**URL-format**: `https://[username]-indikator-dashboard-home-xxxxx.streamlit.app`

### Railway

1. Importera från GitHub
2. Railway detekterar automatiskt `railway.toml`
3. Deployas med ett klick

```toml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "streamlit run Start.py --server.port $PORT"
```

### Heroku

```bash
heroku create kungsbacka-dashboard
git push heroku main
```

Procfile finns redan:
```
web: streamlit run Start.py --server.port $PORT
```

### Lokal Docker (Framtida)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "Start.py"]
```

Se [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) för detaljerade instruktioner.

## 📊 Datakällor

### Inbyggda datakällor
- **SCB API** - Officiell svensk statistik
- **Kolada API** - Kommunal nyckeltal
- **Kommunens GIS-data** - Geografisk information
- **Infonet** - Interna kommunala dokument

### Cache-strategi
- API-svar cachas lokalt i `/cache`
- Cache-tid: 24 timmar för SCB, 1 vecka för Kolada
- Automatisk uppdatering vid behov

## 🧪 Testning

### Köra tester (framtida)
```bash
pytest tests/
```

### Manuell testning
1. Kontrollera API-status på Admin-sidan
2. Verifiera att alla sidor laddas korrekt
3. Testa datahämtning från SCB och Kolada
4. Kontrollera kartvisualisering

## 🤝 Bidra

Bidrag är välkomna! Följ dessa steg:

1. **Forka projektet**
2. **Skapa en feature branch**
   ```bash
   git checkout -b feature/min-nya-funktion
   ```
3. **Committa dina ändringar**
   ```bash
   git commit -m "Lägg till fantastisk funktion"
   ```
4. **Pusha till branchen**
   ```bash
   git push origin feature/min-nya-funktion
   ```
5. **Öppna en Pull Request**

### Code Style
- Följ PEP 8 Python style guide
- Kommentera komplexa funktioner
- Använd svenska kommentarer för domänspecifik kod
- Skriv beskrivande commit-meddelanden

## � Felsökning

### Vanliga problem

**Problem: "ModuleNotFoundError"**
- Lösning: Kör `pip install -r requirements.txt`

**Problem: SCB API returnerar fel**
- Kontrollera internet-anslutning
- Verifiera att SCB API är uppe (se Admin-sida)
- Kolla cache-filer i `/cache`

**Problem: Kartor visas inte**
- Säkerställ att GeoPandas är installerat
- Kontrollera att GeoJSON-filer finns i `/data`

**Problem: Streamlit kraschar**
- Kontrollera Python-version (3.11+)
- Rensa cache: `streamlit cache clear`

## 📝 Versionhistorik

### v2.0.0 (Aktuell)
- ✅ Komplett Kolada-integration med 50+ KPI:er
- ✅ SCB PX-Web API 2.0 implementation
- ✅ AI-assistent med översiktsplanekunskap
- ✅ Interaktiva kartor med Folium
- ✅ Ortanalys och geografisk visualisering
- ✅ Förbättrad felhantering och cache

### v1.0.0
- Initial release
- Grundläggande SCB-integration
- Befolkningsanalys
- Nyckeltal-dashboard

## 📄 Licens

Detta projekt är licensierat under MIT License - se [LICENSE](LICENSE) filen för detaljer.

## 👥 Utvecklingsteam

**Utvecklad för Kungsbacka kommun**

- Projektägare: Raquel Sandblad
- Repository: [github.com/RaquelSandblad/indikator-dashboard](https://github.com/RaquelSandblad/indikator-dashboard)

## 📧 Kontakt

För frågor eller support:
- Öppna ett issue på GitHub
- Kontakta utvecklingsteamet

## 🙏 Erkännanden

- **Statistiska Centralbyrån (SCB)** - Öppen statistikdata
- **Kolada** - Kommunal nyckeltalsdatabas
- **Streamlit** - Utmärkt webb-framework
- **Plotly** - Interaktiva visualiseringar
- **Kungsbacka kommun** - Data och domänkunskap

---

**Byggd med ❤️ för bättre samhällsplanering i Kungsbacka**

*Senast uppdaterad: Oktober 2025*