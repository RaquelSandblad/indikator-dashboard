# 🚀 Deployment Guide - Kungsbacka Planeringsdashboard

Detta dokument beskriver olika sätt att få dashboarden ut på nätet.

## 📋 Innehållsförteckning

1. [Streamlit Cloud (Rekommenderat)](#streamlit-cloud)
2. [Heroku](#heroku)
3. [Digital Ocean App Platform](#digital-ocean)
4. [Railway](#railway)
5. [Render](#render)
6. [Lokal utveckling](#lokal-utveckling)

---

## 🌟 Streamlit Cloud (Rekommenderat)

**Fördelar:** Gratis, enkelt, specialbyggt för Streamlit-appar
**Nackdelar:** Begränsade resurser på gratisversionen

### Steg för Streamlit Cloud:

1. **Skapa konto på Streamlit Cloud:**
   - Gå till https://share.streamlit.io/
   - Logga in med ditt GitHub-konto

2. **Deploya appen:**
   - Klicka "New app"
   - Välj repository: `RaquelSandblad/indikator-dashboard`
   - Main file path: `main_dashboard.py`
   - Klicka "Deploy!"

3. **URL blir automatiskt:**
   ```
   https://raquelsandblad-indikator-dashboard-main-dashboard-xxxxx.streamlit.app/
   ```

### Konfiguration för Streamlit Cloud:

Filen `.streamlit/config.toml` är redan skapad med rätt inställningar:
```toml
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

---

## 🔥 Heroku

**Fördelar:** Robust, många tillägg tillgängliga
**Nackdelar:** Inte längre gratis, kräver betalning

### Steg för Heroku:

1. **Skapa `Procfile`:**
   ```
   web: streamlit run main_dashboard.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Skapa `runtime.txt`:**
   ```
   python-3.11.0
   ```

3. **Uppdatera `requirements.txt`:**
   Redan konfigurerad med alla nödvändiga paket.

4. **Deploy:**
   ```bash
   heroku create kungsbacka-dashboard
   git push heroku main
   ```

---

## 🌊 Digital Ocean App Platform

**Fördelar:** Enkel setup, bra prestanda
**Nackdelar:** Kostar pengar

### Konfiguration:

Skapa `.do/app.yaml`:
```yaml
name: kungsbacka-dashboard
services:
- name: web
  source_dir: /
  github:
    repo: RaquelSandblad/indikator-dashboard
    branch: main
  run_command: streamlit run main_dashboard.py --server.port=$PORT --server.address=0.0.0.0
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8501
```

---

## 🚂 Railway

**Fördelar:** Gratis tier, enkelt att använda
**Nackdelar:** Begränsade gratisresurser

### Steg för Railway:

1. Gå till https://railway.app/
2. Anslut GitHub-konto
3. Välj repository
4. Railway känner automatiskt igen Streamlit

Skapa `railway.toml`:
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "streamlit run main_dashboard.py --server.port=$PORT --server.address=0.0.0.0"
```

---

## 🎨 Render

**Fördelar:** Gratis tier, bra för statiska sidor
**Nackdelar:** Kan vara långsamt på gratis tier

### Konfiguration för Render:

1. Skapa `render.yaml`:
```yaml
services:
  - type: web
    name: kungsbacka-dashboard
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run main_dashboard.py --server.port=$PORT --server.address=0.0.0.0
```

---

## 💻 Lokal utveckling

För att köra lokalt:

```bash
# Installera dependencies
pip install -r requirements.txt

# Kör applikationen
streamlit run main_dashboard.py

# Eller på specifik port
streamlit run main_dashboard.py --server.port 8506
```

---

## 📁 Filstruktur för deployment

Kontrollera att alla dessa filer finns:

```
indikator-dashboard/
├── main_dashboard.py          # Huvudapplikation
├── config.py                  # Konfiguration
├── data_sources.py           # Datakällor
├── utils.py                  # Hjälpfunktioner
├── maps.py                   # Kartfunktioner
├── indicators.py             # Indikatorer
├── requirements.txt          # Python-dependencies
├── .streamlit/
│   └── config.toml           # Streamlit-konfiguration
├── planbesked.json          # Data
├── op.json                  # Data
├── op.geojson              # Data
└── image.png               # Kommun-bild
```

---

## 🔐 Miljövariabler (för känslig data)

Om du behöver API-nycklar eller känsliga data:

### För Streamlit Cloud:
Lägg till i "Secrets" sektionen i Streamlit Cloud dashboard:
```toml
[secrets]
api_key = "din_hemliga_nyckel"
database_url = "din_databas_url"
```

### För andra plattformar:
Använd miljövariabler och läs dem i koden:
```python
import os
api_key = os.getenv("API_KEY")
```

---

## 🚨 Viktiga tips för deployment

1. **Kontrollera alla dependencies i requirements.txt**
2. **Testa lokalt först** med `streamlit run main_dashboard.py`
3. **Kontrollera filstorleker** - stora datafiler kan orsaka problem
4. **Använd .gitignore** för cache-filer och känslig data
5. **Övervaka loggar** efter deployment för fel

---

## 📊 Rekommenderad deployment-strategi

**För utveckling/test:** Streamlit Cloud (gratis)
**För produktion:** Digital Ocean App Platform eller Railway

---

## 🆘 Felsökning

### Vanliga problem:

1. **"Module not found":**
   - Kontrollera requirements.txt
   - Se till att alla filer är committade till Git

2. **"Port already in use":**
   - Ändra port i kommandot: `--server.port=8502`

3. **"File not found":**
   - Kontrollera att datafiler (planbesked.json, etc.) finns i repository

4. **Långsam laddning:**
   - Optimera datafiler
   - Använd caching (@st.cache_data)

---

## 📞 Support

Om du behöver hjälp med deployment:
- Streamlit Community: https://discuss.streamlit.io/
- GitHub Issues: https://github.com/RaquelSandblad/indikator-dashboard/issues

---

**Lycka till med deployment! 🚀**
