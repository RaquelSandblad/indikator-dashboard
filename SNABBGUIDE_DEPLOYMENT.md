# 🚀 SNABBGUIDE: Dela Dashboarden

## ⚡ Push till GitHub (kör dessa kommandon):

```bash
# Steg 1: Lägg till ALLA ändringar
git add .

# Steg 2: Commit med beskrivning
git commit -m "Uppdatering: Ortgränser på kartan, Anneberg prioriterad ort, Admin flyttad"

# Steg 3: Pusha till GitHub
git push origin main
```

---

## 🌐 Deploy till Internet (välj ETT alternativ):

### ALTERNATIV 1: Railway.app (Rekommenderat)
✅ Gratis för små projekt  
✅ Automatisk deployment  
✅ Enkel setup

**Steg:**
1. Gå till https://railway.app
2. Logga in med GitHub
3. Klicka "New Project" → "Deploy from GitHub repo"
4. Välj `RaquelSandblad/indikator-dashboard`
5. Klart! Du får en URL typ: `https://indikator-dashboard.up.railway.app`

---

### ALTERNATIV 2: Streamlit Cloud (Även bra)
✅ Gjort för Streamlit  
✅ Helt gratis  
✅ Automatisk omstart vid push

**Steg:**
1. Gå till https://streamlit.io/cloud
2. Logga in med GitHub
3. Klicka "New app"
4. Välj:
   - Repo: `RaquelSandblad/indikator-dashboard`
   - Branch: `main`
   - File: `Home.py`
5. Klicka "Deploy"
6. Du får en URL typ: `https://kungsbacka-dashboard.streamlit.app`

---

## 📧 Dela med kollegor

När du fått din URL (från Railway eller Streamlit):

**Exempel-email:**
```
Hej!

Vår nya indikator-dashboard är nu live på:
👉 https://indikator-dashboard.up.railway.app

Du kan se:
- Kommunens nyckeltal och KPI:er
- Befolkningsstatistik från SCB
- Ortkartor med prioriterade orter
- AI-assistent för planeringsdata
- Planbesked på karta

/Raquel
```

---

## 🔄 Uppdatera live-versionen

Efter första deployment uppdateras sidan **automatiskt** när du pushar:

```bash
# Gör dina ändringar i koden
# Spara filer

# Push till GitHub
git add .
git commit -m "Min ändring"
git push

# Railway/Streamlit upptäcker ändringen och uppdaterar automatiskt! 
# Tar ~2-3 minuter
```

---

## 📊 Vad händer nu?

När du kört `git push`:
1. ✅ GitHub får alla dina ändringar
2. ✅ Railway/Streamlit ser att GitHub uppdaterats
3. ✅ De bygger om appen automatiskt
4. ✅ Din live-URL uppdateras med nya ändringarna
5. ✅ Kollegor ser den nya versionen direkt

**Ingen server-hantering behövs - allt sker automatiskt!** 🎉

---

## 🆘 Vanliga frågor

**Q: Kostar det något?**  
A: Nej! Både Railway och Streamlit Cloud är gratis för små projekt som detta.

**Q: Måste jag göra något varje gång jag ändrar kod?**  
A: Bara `git push` - resten sker automatiskt!

**Q: Kan jag ha båda (Railway OCH Streamlit)?**  
A: Ja! Du kan deploya till båda om du vill ha backup.

**Q: Hur ser jag om deployment fungerade?**  
A: Gå in på Railway/Streamlit-dashboarden, där ser du status och loggar.

**Q: Kan kollegor redigera?**  
A: Nej, de kan bara se. För att redigera behöver de tillgång till GitHub-repot.
