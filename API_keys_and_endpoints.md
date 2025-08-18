# API_keys_and_endpoints.md - Dokumentation för API-nycklar och endpoints

# 🔑 API-nycklar och endpoints för Kungsbacka Planeringsdashboard

## ✅ FUNGERANDE ÖPPNA API:er (ingen nyckel krävs)

### 1. SCB (Statistiska centralbyrån)
- **Bas-URL**: `https://api.scb.se/OV0104/v1/doris/sv/ssd`
- **Status**: ✅ Fungerar
- **Beskrivning**: Befolkning, bostäder, arbetslöshet, inkomster
- **Exempel endpoint**: `/BE/BE0101/BE0101A/BefolkningNy`
- **Dokumentation**: https://www.scb.se/vara-tjanster/oppna-data/api-for-statistikdatabasen/

**Testade funktioner:**
- ✅ Befolkning per kommun, kön, ålder
- ✅ Befolkningsutveckling över tid
- ✅ Regionlista (alla kommuner)

### 2. Kolada (Kommunala nyckeltal)
- **Bas-URL**: `http://api.kolada.se/v2`
- **Status**: ✅ Fungerar
- **Beskrivning**: Kommunala nyckeltal och jämförelser
- **Exempel endpoint**: `/data/kpi/N00914/municipality/1384`
- **Dokumentation**: https://github.com/Hypergene/kolada

**Testade funktioner:**
- ✅ Nyckeltal per kommun
- ✅ KPI-definitioner
- ✅ Tidsserier

### 3. SMHI (Väderdata)
- **Bas-URL**: `https://opendata-download-metfcst.smhi.se/api`
- **Status**: ✅ Fungerar
- **Beskrivning**: Väderdata och prognoser
- **Exempel**: `/category/pmp3g/version/2/geotype/point/lon/12.08/lat/57.49/data.json`
- **Dokumentation**: https://opendata.smhi.se/apidocs/

### 4. Naturvårdsverket (GIS)
- **WFS-URL**: `https://geodata.naturvardsverket.se/geoserver/naturreservat/wfs`
- **Status**: ✅ Fungerar
- **Beskrivning**: Naturreservat, nationalparker
- **Format**: GeoJSON via WFS

### 5. Lantmäteriet (Kartor)
- **WMS-URL**: `https://minkarta.lantmateriet.se/map/topowebbcache/`
- **Status**: ✅ Fungerar (begränsad)
- **Beskrivning**: Topografiska kartor
- **Licens**: CC BY 4.0

## 🔐 API:er SOM KRÄVER NYCKLAR

### 6. Trafiklab (Kollektivtrafik)
- **Bas-URL**: `https://api.resrobot.se/v2.1`
- **Status**: 🔑 Kräver API-nyckel
- **Beskrivning**: Kollektivtrafikdata, tidtabeller, hållplatser
- **Kostnad**: Gratis upp till 10,000 anrop/månad
- **Registrering**: https://www.trafiklab.se/

**Så här får du nyckel:**
1. Gå till https://www.trafiklab.se/
2. Skapa konto
3. Skapa nytt projekt
4. Begär API-nyckel för "ResRobot - Reseplanerare"

### 7. Trafikverket (Trafikdata)
- **URL**: `https://api.trafikinfo.trafikverket.se/v2/data.json`
- **Status**: 🔑 Kräver API-nyckel
- **Beskrivning**: Trafikflöden, vägarbeten, olycksstatistik
- **Kostnad**: Gratis
- **Registrering**: https://api.trafikinfo.trafikverket.se/

**Så här får du nyckel:**
1. Gå till https://api.trafikinfo.trafikverket.se/
2. Registrera dig
3. Begär API-nyckel
4. Läs dokumentationen för XML-queries

## 🏛️ KOMMUNALA OCH REGIONALA API:er

### 8. Kungsbacka kommun (GIS)
- **Status**: 🔍 Behöver identifieras
- **Troliga URL:er**:
  - `https://kartor.kungsbacka.se/geoserver/wms`
  - `https://gis.kungsbacka.se/arcgis/rest/services`
- **Beskrivning**: Detaljplaner, bygglov, kommunala lager

**Så här hittar du kommunens API:er:**
1. Kontakta IT-avdelningen på Kungsbacka kommun
2. Fråga efter WMS/WFS-endpoints för:
   - Detaljplaner
   - Översiktsplan
   - Bygglov/planbesked
   - Naturvärden
3. Be om documentation och eventuella API-nycklar

### 9. Region Halland
- **Status**: 🔍 Behöver identifieras
- **Möjliga källor**: Kollektivtrafik, sjukvård, miljödata
- **Kontakt**: https://www.regionhalland.se/

### 10. Länsstyrelsen Halland
- **Status**: 🔍 Behöver identifieras
- **Beskrivning**: Miljötillstånd, naturvård, kulturmiljö
- **Kontakt**: https://www.lansstyrelsen.se/halland

## 📋 IMPLEMENTERINGSSTATUS

### ✅ Implementerat och fungerar
- [x] SCB befolkningsdata
- [x] SCB regionlista
- [x] Kolada kommunala nyckeltal
- [x] SMHI väderdata
- [x] Naturvårdsverkets WFS
- [x] Baskartor (OpenStreetMap, CartoDB)

### 🔄 Delvis implementerat
- [x] Lantmäteriets kartor (WMS fungerar med begränsningar)
- [x] Trafikverket (dummy-data, väntar på API-nyckel)
- [x] Trafiklab (dummy-data, väntar på API-nyckel)

### ❌ Inte implementerat
- [ ] Kungsbacka kommuns GIS-tjänster
- [ ] Region Hallands data
- [ ] Länsstyrelsens data

## 🚀 NÄSTA STEG - Handlingsplan

### Kortsiktigt (denna vecka)
1. **Skaffa Trafiklab API-nyckel**
   - Registrera på https://www.trafiklab.se/
   - Begär ResRobot API-nyckel
   - Implementera kollektivtrafikdata

2. **Skaffa Trafikverket API-nyckel**
   - Registrera på https://api.trafikinfo.trafikverket.se/
   - Testa trafikflödesdata
   - Implementera i dashboarden

### Medellångsiktigt (nästa månad)
3. **Identifiera kommunala API:er**
   - Kontakta Kungsbacka kommuns IT-avdelning
   - Begär access till GIS-tjänster
   - Dokumentera endpoints och format

4. **Förbättra SCB-integration**
   - Lägg till fler tabeller (bostäder, näringsliv)
   - Implementera automatisk cache-uppdatering
   - Förbättra felhantering

### Långsiktigt (3-6 månader)
5. **Komplett datapipeline**
   - Schemalagda uppdateringar
   - Automatisk validering
   - Notifikationer vid fel

6. **Utökad funktionalitet**
   - Prognoser och trendanalys
   - Export till olika format
   - API för andra system

## 🛠️ TEKNISK IMPLEMENTATION

### Miljövariabler (.env)
```bash
# API-nycklar
TRAFIKLAB_API_KEY=din_nyckel_här
TRAFIKVERKET_API_KEY=din_nyckel_här

# Kommunala endpoints
KUNGSBACKA_WMS_URL=https://kartor.kungsbacka.se/geoserver/wms
KUNGSBACKA_WFS_URL=https://kartor.kungsbacka.se/geoserver/wfs

# Cache-inställningar
CACHE_TIMEOUT_HOURS=24
```

### Kodexempel för nya API:er
```python
# trafiklab_client.py
import requests
import os

class TrafiklabClient:
    def __init__(self):
        self.api_key = os.getenv('TRAFIKLAB_API_KEY')
        self.base_url = "https://api.resrobot.se/v2.1"
    
    def get_stops_near(self, lat, lon, radius=1000):
        url = f"{self.base_url}/location.nearbystops"
        params = {
            'key': self.api_key,
            'originCoordLat': lat,
            'originCoordLong': lon,
            'r': radius,
            'format': 'json'
        }
        response = requests.get(url, params=params)
        return response.json()
```

## 📞 KONTAKTUPPGIFTER

### För API-support
- **SCB**: https://www.scb.se/vara-tjanster/oppna-data/
- **Trafiklab**: support@trafiklab.se
- **Trafikverket**: https://api.trafikinfo.trafikverket.se/
- **SMHI**: opendata@smhi.se

### För kommunala frågor
- **Kungsbacka kommun IT**: (kontakta via växel 0300-83 40 00)
- **Kungsbacka stadsbyggnad**: stadsbyggnad@kungsbacka.se

---

**Uppdaterad**: 2024-08-18
**Version**: 1.0
