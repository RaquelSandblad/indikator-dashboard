# 🚀 Deployment Guide - Dela Dashboarden med Kollegor

## Snabbstart: Push till GitHub och Deploy

### Steg 1: Spara alla ändringar till GitHub

```bash
# Lägg till alla ändringar
git add .

# Commit med beskrivning
git commit -m "Uppdaterad dashboard med ortgränser och korrigerad ort-prioritering"

# Pusha till GitHub
git push origin main
```

### Steg 2: Deploy till Railway.app (Gratis hosting)

#### A. Skapa konto på Railway
1. Gå till https://railway.app
2. Logga in med ditt GitHub-konto
3. Klicka "New Project"

#### B. Anslut ditt repository
1. Välj "Deploy from GitHub repo"
2. Välj `RaquelSandblad/indikator-dashboard`
3. Railway detekterar automatiskt `Procfile` och `requirements.txt`

#### C. Ange environment variables (om du har API-nycklar)
1. Gå till Settings → Variables
2. Lägg till eventuella API-nycklar från `config.py`

#### D. Deploy!
1. Railway börjar bygga automatiskt
2. Efter ~2-5 minuter får du en URL typ: `https://indikator-dashboard-production.up.railway.app`

**Den URL:en delar du med dina kollegor!** 🎉

---

## Alternativ: Deploy till Streamlit Cloud (Även gratis)

### Fördelar:
- Designat specifikt för Streamlit-appar
- Enklare setup
- Automatisk omstart vid push

### Steg:

1. **Gå till**: https://streamlit.io/cloud
2. **Logga in** med GitHub
3. **Klicka "New app"**
4. **Välj**:
   - Repository: `RaquelSandblad/indikator-dashboard`
   - Branch: `main`
   - Main file: `Home.py`
5. **Klicka "Deploy"**

Din app får en URL typ: `https://indikator-dashboard.streamlit.app`

---

## Vad händer efter deploy?

### Automatiska uppdateringar:
När du pushar nya ändringar till GitHub kommer appen att uppdateras automatiskt!

```bash
# Gör ändringar i koden
# Spara och testa lokalt

# Push till GitHub
git add .
git commit -m "Beskrivning av ändring"
git push

# Railway/Streamlit Cloud upptäcker ändringen och redeployar automatiskt!
```

---

## 📍 Nuvarande status

### Filer redo för deployment:
- ✅ `Home.py` - Huvudfil
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Railway deployment config
- ✅ `railway.toml` - Railway settings
- ✅ `runtime.txt` - Python version (3.11)
- ✅ Alla pages/ filer (0-12, 99)
- ✅ `data/oversiktsplan_kunskap.json` - Knowledge base
- ✅ `data/orter_avgransningar.geojson` - Ortgränser

### Senaste uppdateringar:
- 🟢 Ortgränser visualisering i Karttjänst
- 🟢 Anneberg korrigerad till prioriterad ort
- 🟢 Fjärås korrigerad till övrig ort
- 🟢 Admin flyttad till sista position (99_Admin.py)
- 🟢 CSS-fix för ljus text

---

## 🔗 Dela med kollegor

### Efter deployment får du en URL, exempel:

**Railway:**
```
https://indikator-dashboard-production.up.railway.app
```

**Streamlit Cloud:**
```
https://kungsbacka-indikator.streamlit.app
```

**Dela denna URL med:**
- Email
- Teams/Slack
- Intern wiki
- Bookmark i webbläsare

---

## 🛠️ Troubleshooting

### Problem: "Application error" efter deploy
**Lösning**: Kolla Railway/Streamlit logs, ofta saknade dependencies i `requirements.txt`

### Problem: API-nycklar fungerar inte
**Lösning**: Lägg till environment variables i Railway/Streamlit Cloud settings

### Problem: Sidan laddas långsamt
**Lösning**: Första besöket kan ta 30-60 sek (cold start), därefter snabbare

---

## 📞 Support

- **Railway**: https://docs.railway.app
- **Streamlit Cloud**: https://docs.streamlit.io/streamlit-community-cloud
- **GitHub**: https://github.com/RaquelSandblad/indikator-dashboard

---

## ⚡ Snabbkommando för push

```bash
# Kör detta varje gång du vill uppdatera live-versionen:
git add . && git commit -m "Uppdatering $(date +%Y-%m-%d)" && git push
```

🎉 **Lycka till med delningen!**
