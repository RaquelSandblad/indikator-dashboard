# 🚀 PROJEKTPLAN - 2 VECKORS SPRINT
## Kungsbacka Dashboard - Från Monolith till Modern Arkitektur

**Startdatum:** 2 oktober 2025  
**Deadline:** 16 oktober 2025  
**Status:** 🟢 PÅGÅENDE - Dag 1 av 14

---

## 📊 NULÄGE (2 oktober - Kväll)

### ✅ KLART (Dag 1)
1. ✅ **Navigationsomstrukturering** - Alla 10 ändringar från designbild
   - Home → "Inledning"
   - Översiktsplanering (rätt stavning med Ö)
   - Översikt (förenklad)
   - Befolkning (detaljerad)
   - Kolada (placeholder, redo för integration)
   - Boendebarometer
   - Värmekarta (terrakottafärger)
   - Ortanalys
   - Admin (sammanslagen Om + Admin)

2. ✅ **Inledning-flik** i Översiktsplanering
   - Kartor och planbesked
   - Interaktiv karta med färgkodning
   - Statistik och förklarande text

3. ✅ **Multi-page struktur** fungerar
   - 8 sidor med korrekt numrering
   - Automatisk navigation
   - Ren filstruktur

### 🚧 PÅGÅENDE
- **Kolada-integration** (startar NU)

---

## 🎯 MÅLBILD - MODERN ARKITEKTUR

### Från:
```
main_dashboard.py (1500+ rader, allt i en fil)
→ Sårbar, svår att debugga, duplicerad kod
```

### Till:
```
indikator-dashboard/
├── Home.py                     # Huvudsida
├── config.py                   # Konfiguration
├── pages/                      # Auto-navigation (✅ KLART)
│   ├── 0_Översiktsplanering.py
│   ├── 1_Oversikt.py
│   ├── 2_Befolkning.py
│   ├── 3_Kolada.py
│   ├── 4_Boendebarometer.py
│   ├── 5_Värmekarta.py
│   ├── 6_Ortanalys.py
│   └── 7_Admin.py
├── data/                       # Datakällor (modulärt)
│   ├── scb_connector.py       # SCB API
│   ├── kolada_connector.py    # Kolada API (🚧 NÄSTA)
│   └── antura_connector.py    # Antura (framtida)
├── components/                 # Återanvändbara komponenter
│   ├── metrics.py
│   ├── charts.py
│   └── maps.py
└── utils/                      # Hjälpfunktioner
    ├── formatters.py
    └── cache_manager.py
```

---

## 📅 SPRINT-PLAN (14 DAGAR)

### 🏃 **VECKA 1: DATA & INTEGRATION**

#### **Dag 1-2 (2-3 okt)** - Kolada Integration ⏰ NU
- [x] Navigationsomstrukturering
- [ ] `data/kolada_connector.py` - Hämta kommundata
- [ ] `pages/3_Kolada.py` - Visa KPI:er och jämförelser
- [ ] Interaktiva grafer för kommun-jämförelser
- [ ] Cache för snabbare laddning

#### **Dag 3-4 (4-5 okt)** - SCB Modulärisering
- [ ] Refaktorera SCB-kod till `data/scb_connector.py`
- [ ] Separera befolknings-, bostads- och arbetsmarknadsdata
- [ ] Förbättra cache och felhantering
- [ ] Uppdatera Befolkning-sidan med nya moduler

#### **Dag 5-6 (6-7 okt)** - Komponenter & Återanvändning
- [ ] `components/charts.py` - Återanvändbara diagram
- [ ] `components/metrics.py` - Standardiserade metrics
- [ ] `components/maps.py` - Kartkomponenter
- [ ] Uppdatera alla sidor att använda komponenter

#### **Dag 7 (8 okt)** - Mellansteg & Testing
- [ ] Testa alla datakällor
- [ ] Verifiera felhantering
- [ ] Performance-optimering
- [ ] Cache-strategier

### 🏃 **VECKA 2: AUTOMATION & DEPLOYMENT**

#### **Dag 8-9 (9-10 okt)** - Antura Integration (om möjligt)
- [ ] Kontakta kommun-IT för API-access
- [ ] `data/antura_connector.py`
- [ ] Automatisk planbesked-hämtning
- [ ] Uppdatera Översiktsplanering med live data

#### **Dag 10-11 (11-12 okt)** - Extra API:er
- [ ] Trafiklab (kollektivtrafik) - om tid finns
- [ ] Naturvårdsverket (miljödata) - om tid finns
- [ ] Automatiska uppdateringar

#### **Dag 12-13 (13-14 okt)** - Deployment & Dokumentation
- [ ] Deploy till Streamlit Cloud
- [ ] Användarguide för kollegor
- [ ] API-dokumentation
- [ ] Teknisk dokumentation
- [ ] Backup-rutiner

#### **Dag 14 (15 okt)** - Buffer & Polish
- [ ] Bugfixar
- [ ] UX-förbättringar
- [ ] Slutgiltig testning
- [ ] Överlämning

---

## 🎯 PRIORITERAD FEATURE-LISTA

### 🔥 MUST HAVE (Kritiskt)
1. ✅ Multi-page struktur
2. 🚧 Kolada-integration (KPI:er, jämförelser)
3. ⏳ SCB modulärisering (stabil datahämtning)
4. ⏳ Återanvändbara komponenter
5. ⏳ Deployment till produktion

### 🟡 SHOULD HAVE (Viktigt)
6. ⏳ Antura-integration (planbesked automation)
7. ⏳ Cache-optimering
8. ⏳ Felhantering per modul
9. ⏳ Admin-sida med systemstatus

### 🟢 NICE TO HAVE (Om tid finns)
10. ⏳ Trafiklab (kollektivtrafik)
11. ⏳ Naturvårdsverket (miljö)
12. ⏳ Export-funktioner
13. ⏳ Automatiska rapporter

---

## 💡 TEKNISK STRATEGI

### Arkitekturprinciper:
1. **Modulär design** - En fil, ett ansvar
2. **Isolerad felhantering** - En krasch påverkar inte andra
3. **DRY (Don't Repeat Yourself)** - Återanvänd komponenter
4. **API-first** - Separera data från presentation
5. **Cache smart** - Snabb UX, färre API-anrop

### Tech Stack:
- **Frontend:** Streamlit (multi-page app)
- **Data:** SCB API, Kolada API, Antura API
- **Kartor:** Folium + Leaflet
- **Grafer:** Plotly
- **Cache:** Streamlit cache + JSON-filer
- **Deployment:** Streamlit Cloud (gratis!)

---

## 🚨 RISKER & MITIGERING

| Risk | Sannolikhet | Impact | Mitigering |
|------|-------------|--------|------------|
| Antura API-access fördröjs | Hög | Medel | Fortsätt med statiska data, integration senare |
| API rate limits (SCB/Kolada) | Medel | Låg | Smart cache, begränsa API-anrop |
| Performance-problem | Låg | Medel | Lazy loading, cache, CDN |
| Deployment-problem | Låg | Hög | Testa deployment tidigt (Dag 8) |

---

## 📈 FRAMGÅNGSMETRIK

### Definition of Done:
- ✅ Alla sidor fungerar utan errors
- ✅ Data hämtas från minst 2 externa API:er (SCB + Kolada)
- ✅ Modulär struktur implementerad
- ✅ Deployed och tillgänglig via URL
- ✅ Dokumentation för användare och utvecklare
- ✅ Cache fungerar (snabba laddningstider)

### KPI:er:
- Sidladdningstid: < 3 sekunder
- API-framgång: > 95%
- Cache-träffar: > 80%
- Kodkvalitet: Inga dupliceringar, tydlig struktur

---

## 👥 TEAM

**AI Agent (GitHub Copilot):** Kodning, arkitektur, debugging  
**Du (Raquel):** Kravställning, testning, domänkunskap, koordinering  
**Kommunikation:** Ständig dialog, snabba iterationer

---

## 📝 DAGLIG LOGG

### **Dag 1 (2 oktober 2025) - ✅ FRAMGÅNGSRIK**
**Tid:** 14:00-17:00 (3h)  
**Genomfört:**
- ✅ Navigationsomstrukturering (A-I från designbild)
- ✅ Home.py → "Inledning"
- ✅ Översiktsplanering (fixat Ö-stavning)
- ✅ Simplified Översikt
- ✅ Kolada placeholder-sida
- ✅ Boendebarometer flyttad
- ✅ Jämförelser borttagen
- ✅ Värmekarta (terrakotta, mjuka kanter)
- ✅ Ortanalys flyttad
- ✅ Admin (sammanslagen)
- ✅ **Inledning-flik** i Översiktsplanering (KARTOR återställda!)

**Lärdomar:**
- Multi-page struktur fungerar perfekt med numrerade prefix
- Svenska tecken (Ö, Ä) i filnamn kräver UTF-8 hantering
- Cat heredoc i terminal är effektivt för filskapande

**Nästa:** Kolada-integration startar NU!

---

## 🎊 SLUTMÅL

**16 oktober 2025:**
- 🎯 Fullt fungerande dashboard
- 🎯 Modulär, skalbar arkitektur
- 🎯 Deployed och tillgänglig
- 🎯 Dokumenterad och testbar
- 🎯 Redo för användning i kommunen

**VI KLARAR DETTA!** 🚀💪

---

*Uppdaterad: 2 oktober 2025, 17:00*  
*Status: På schema - Dag 1 av 14 klar!*
