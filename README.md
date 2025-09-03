# 🏙️ Kungsbacka Planeringsdashboard

Ett webbaserat verktyg för uppföljning av översiktsplanering och strategisk utveckling för Kungsbacka kommun.

![Dashboard](https://img.shields.io/badge/Status-Live-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.48+-red)

## 🎯 Projektets syfte

Detta verktyg hjälper planerare och beslutsfattare att:

- **Följa upp** översiktsplanens genomförande
- **Analysera** befolkningsutveckling och prognoser  
- **Visualisera** planbesked och byggprojekt på interaktiva kartor
- **Jämföra** nyckeltal med andra kommuner
- **Hämta** aktuell data från SCB, Kolada och andra myndigheter automatiskt

## ✨ Funktioner

### 📊 Indikatorer & KPI:er
- Befolkningsutveckling och demografisk analys
- Bostadsbyggande och planbesked
- Hållbarhetsindikatorer (kollektivtrafik, grönområden)
- Jämförelser med nationella och regionala mål

### 🗺️ Interaktiva kartor
- Planbesked visualiserade med ÖP-följsamhet
- Naturreservat och miljöskydd
- Kollektivtrafikstationer och tillgänglighet
- Trafikflöden och infrastruktur
- Befolkningstäthet som värmekarta

### 👥 Befolkningsanalys
- Interaktiva ålderspyramider
- Trendanalys över tid
- Prognoser och scenarioanalys

### 🌍 Datakällor
- **SCB** - Befolkning, bostäder, arbetslöshet
- **Kolada** - Kommunala nyckeltal
- **Naturvårdsverket** - Miljödata och naturreservat
- **Trafikverket** - Infrastruktur och trafikflöden

## 🚀 Kom igång

### Förutsättningar
- Python 3.8 eller senare
- Git

### Installation

1. **Klona projektet**
```bash
git clone https://github.com/RaquelSandblad/indikator-dashboard.git
cd indikator-dashboard
```

2. **Installera dependencies**
```bash
pip install -r requirements.txt
```

3. **Starta applikationen**
```bash
streamlit run main_dashboard.py
```

4. **Öppna i webbläsare**
   - Gå till `http://localhost:8501`

### Första gången
Dashboarden fungerar direkt med öppna API:er från SCB och Kolada. För utökad funktionalitet, se [API-nycklar](API_keys_and_endpoints.md).

## 📁 Projektstruktur

```
indikator-dashboard/
├── main_dashboard.py          # Huvudapplikation (ny förbättrad version)
├── indikator_dashboard.py     # Ursprunglig version 
├── config.py                  # Konfiguration och inställningar
├── data_sources.py           # API-klienter för alla datakällor
├── indicators.py             # Beräkning av nyckelindikatorer
├── maps.py                   # Kartfunktioner och visualisering
├── utils.py                  # Hjälpfunktioner
├── SCB_Dataservice.py        # Ursprunglig SCB-klass
├── requirements.txt          # Python-dependencies
├── API_keys_and_endpoints.md # Dokumentation för API:er
├── .streamlit/config.toml    # Streamlit-konfiguration
├── planbesked.json          # Planbesked (geodata)
├── op.json                  # Översiktsplan (geodata)
├── op.geojson              # Alternativ ÖP-format
└── image.png               # Kommunbild/logotyp
```

## 🔑 API-nycklar och datakällor

### ✅ Fungerar utan nycklar
- **SCB** - Statistiska centralbyrån (befolkning, bostäder)
- **Kolada** - Kommunala nyckeltal
- **Naturvårdsverket** - Miljödata via WFS

### 🔐 Kräver registrering (gratis)
- **Trafiklab** - Kollektivtrafikdata
- **Trafikverket** - Trafikflöden och vägdata

Se detaljerad guide i [API_keys_and_endpoints.md](API_keys_and_endpoints.md)

## 🛠️ Utveckling

### Lägga till nya datakällor

1. **Skapa ny klient i `data_sources.py`**
```python
class NewDataSource:
    def __init__(self):
        self.base_url = "https://api.example.com"
    
    def fetch_data(self):
        # Implementation
        return data
```

2. **Registrera i `config.py`**
```python
EXTERNAL_APIS = {
    "new_source": {
        "base_url": "https://api.example.com",
        "description": "Beskrivning av datakälla"
    }
}
```

3. **Lägg till i dashboard**
```python
# I main_dashboard.py
new_data = NewDataSource()
```

### Lägga till nya indikatorer

1. **Definiera i `indicators.py`**
```python
def calculate_new_indicator(self):
    return Indicator(
        name="Nytt nyckeltal",
        value=calculated_value,
        unit="enhet",
        trend="up/down/stable"
    )
```

2. **Inkludera i `get_all_indicators()`**

## 📊 Användning

### Startsida
- Översikt över alla nyckeltal
- Senaste aktiviteter och uppdateringar
- Snabbstatus för datakällor

### Indikatorer
- Filtrera per kategori (Befolkning, Planering, Hållbarhet)
- Jämför med målvärden
- Exportera rapporter

### Kartor
- Växla mellan olika lager
- Klicka på objekt för detaljer
- Rita och mäta verktyg
- Exportera som GeoJSON

### Administration
- Kontrollera API-anslutningar
- Rensa cache
- Systemstatus

## 🤝 Bidra

1. Forka projektet
2. Skapa en feature branch (`git checkout -b feature/amazing-feature`)
3. Committa dina ändringar (`git commit -m 'Add amazing feature'`)
4. Pusha till branchen (`git push origin feature/amazing-feature`)
5. Öppna en Pull Request

## 📈 Kommande funktioner

- [ ] Automatiska rapporter via e-post
- [ ] Prognosmodeller för befolkning
- [ ] Integrering med kommunens ärendehanteringssystem
- [ ] Mobile-optimerad vy
- [ ] Exportfunktioner (PDF, Excel)
- [ ] Användarhantering och behörigheter

## 🐛 Kända problem

- GIS-lager från kommunen behöver konfigureras
- Vissa API:er kräver registrering för full funktionalitet
- Naturreservat (exempelvis) kan vara långsamt att ladda

## 📞 Support

- **Issues**: Rapportera buggar på [GitHub Issues](https://github.com/RaquelSandblad/indikator-dashboard/issues)
- **Diskussioner**: [GitHub Discussions](https://github.com/RaquelSandblad/indikator-dashboard/discussions)
- **E-post**: raquel.sandblad@kungsbacka.se

## 📄 Licens

Detta projekt är licensierat under MIT License - se [LICENSE](LICENSE) filen för detaljer.

**Senast uppdaterad**: 2025-09-03  
**Version**: 2.0.0  
**Utvecklad för**: Kungsbacka kommun