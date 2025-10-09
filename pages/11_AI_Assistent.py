import streamlit as st

# OBS! Denna sida är tillfälligt dold från sidomenyn.
st.set_page_config(page_title="AI-Assistent (Ej publik)", page_icon="❌", layout="wide", initial_sidebar_state="collapsed")

# Avbryt rendering om någon försöker öppna sidan direkt
st.warning("Denna sida är inte publik ännu.")
st.stop()
import sys
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import json

# Lägg till current directory till Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importera data-konnektorer
try:
    from data.kolada_connector import kolada
    from data_sources import scb_data
except:
    pass

# Läs in översiktsplanens kunskap
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

st.set_page_config(
    page_title="AI-Assistent - Kungsbacka",
    page_icon="🤖",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    .chat-header h1 {
        color: white;
        margin: 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .user-message {
        background: #e3f2fd;
        border-left: 4px solid #1976d2;
    }
    .assistant-message {
        background: #f3e5f5;
        border-left: 4px solid #7b1fa2;
    }
    .data-source-badge {
        display: inline-block;
        background: #4caf50;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.8rem;
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="chat-header">
    <h1>🤖 AI-Assistent för Kungsbacka</h1>
    <p>Ställ frågor om tillväxt, demografi, utmaningar och utveckling i Kungsbacka kommun</p>
</div>
""", unsafe_allow_html=True)

# Information om vad assistenten kan
with st.expander("ℹ️ Vad kan AI-assistenten hjälpa till med?"):
    st.markdown("""
    **AI-assistenten har tillgång till:**
    
    � **Kommunens dokument (läser och analyserar):**
    - Översiktsplanen (läser direkt från karta.kungsbacka.se)
    - Hållbarhetsstrategi (Våra steg mot hållbarhet)
    - Vision och styrdokument
    
    �📊 **Kolada-statistik:**
    - Arbetsmarknadsdata (sysselsättning, arbetslöshet)
    - Utbildningsresultat (grundskola, gymnasium)
    - Omsorg och välfärd (barnomsorg, äldreomsorg)
    - Miljö och hållbarhet (utsläpp, återvinning)
    - Kultur och fritid (bibliotek, fritidsverksamhet)
    
    👥 **SCB-data:**
    - Befolkningsstatistik och prognoser
    - Bostadsbyggande och bostadsbestånd
    - Befolkningsförändringar
    
    **Exempel på frågor:**
    - "Vad säger översiktsplanen om utveckling i Kungsbacka?"
    - "Hur utvecklas befolkningen i Kungsbacka?"
    - "Vilka är de största utmaningarna för kommunen?"
    - "Hur ser skolresultaten ut jämfört med andra kommuner?"
    - "Vad säger hållbarhetsstrategin om klimatarbetet?"
    - "Hur arbetar kommunen med markanvändning och planering?"
    
    **🆕 Nyhet:** Assistenten läser nu automatiskt relevant information från kommunens webbsidor!
    """)

# Initialisera chat-historik
if "messages" not in st.session_state:
    st.session_state.messages = []

# Cache för webbsideinnehåll
if "web_content_cache" not in st.session_state:
    st.session_state.web_content_cache = {}

# Funktion för att hämta innehåll från webbsida
@st.cache_data(ttl=3600*24)  # Cache i 24 timmar
def fetch_web_content(url):
    """Hämtar och extraherar text från en webbsida"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Ta bort script och style element
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Hämta text
        text = soup.get_text()
        
        # Rensa text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:10000]  # Begränsa till 10000 tecken
    except Exception as e:
        return f"Kunde inte hämta innehåll från {url}: {str(e)}"

# Funktion för att söka i webbsideinnehåll
def search_in_web_content(query, content):
    """Söker efter relevant information i webbsideinnehåll"""
    query_words = query.lower().split()
    
    # Lägg till synonymer för vanliga planeringstermer
    expanded_words = query_words.copy()
    for word in query_words:
        if word in ['utveckla', 'utveckling', 'bygga', 'byggande']:
            expanded_words.extend(['bebyggelse', 'planering', 'prioriterad', 'strategi'])
        elif word in ['plats', 'platser', 'område', 'områden']:
            expanded_words.extend(['ort', 'orter', 'stad', 'tätort'])
        elif word in ['lämplig', 'lämpliga', 'bäst', 'bästa']:
            expanded_words.extend(['prioriterad', 'prioriterade', 'fokus'])
    
    sentences = re.split(r'[.!?]+', content)
    
    relevant_sentences = []
    for sentence in sentences:
        sentence_lower = sentence.lower()
        # Om minst 2 av sökorden (eller synonymer) finns i meningen
        matches = sum(1 for word in expanded_words if word in sentence_lower)
        if matches >= min(2, len(expanded_words) // 2):  # Minst hälften av orden
            # Filtrera bort för korta meningar
            if len(sentence.strip()) > 30:
                relevant_sentences.append(sentence.strip())
    
    return relevant_sentences[:8]  # Returnera max 8 relevanta meningar

# Visa chat-historik
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Funktion för att hämta relevant data baserat på frågan
def get_relevant_data(question):
    """Hämtar relevant data baserat på användarens fråga"""
    question_lower = question.lower()
    data_context = []
    web_insights = []
    
    # Ladda översiktsplanens kunskapsbas
    op_knowledge = load_oversiktsplan_knowledge()
    
    # SÖK I ÖVERSIKTSPLANENS KUNSKAPSBAS
    with st.spinner("Söker i översiktsplanen..."):
        if op_knowledge and any(word in question_lower for word in ['utveckla', 'lämplig', 'plats', 'område', 'prioriterad', 'bygga', 'planering', 'översiktsplan', 'ort', 'bostäder']):
            op_insights = []
            
            # Hitta information om prioriterade orter
            if any(word in question_lower for word in ['ort', 'plats', 'utveckla', 'prioriterad']):
                for ort_namn, ort_info in op_knowledge.get('prioriterade_orter', {}).items():
                    op_insights.append(f"**{ort_namn}** ({ort_info['typ']}, {ort_info['prioritet']} prioritet): {ort_info['beskrivning']}")
                
                # Lägg till övriga orter om frågan är bred
                if 'alla' in question_lower or 'vilka' in question_lower:
                    for ort_namn, ort_info in op_knowledge.get('ovriga_orter', {}).items():
                        op_insights.append(f"**{ort_namn}** ({ort_info['typ']}): {ort_info['beskrivning']}")
            
            # Hitta utvecklingsområden
            if any(word in question_lower for word in ['utvecklingsområde', 'område', 'bygga', 'bostäder']):
                for omrade_namn, omrade_info in op_knowledge.get('strategiska_utvecklingsområden', {}).items():
                    op_insights.append(f"**{omrade_namn}** ({omrade_info['ort']}): {omrade_info['beskrivning']} - {omrade_info['typ']}")
            
            # Hitta principer och strategier
            if any(word in question_lower for word in ['princip', 'strategi', 'planering', 'hur']):
                strategier = op_knowledge.get('planeringsstrategier', {})
                op_insights.append(f"**Planprincip**: {strategier.get('planprincip', '')}")
                op_insights.append(f"**Prioritering**: {strategier.get('prioritering', '')}")
            
            if op_insights:
                web_insights.append(("Översiktsplanen", op_insights))
        
        # Sök i hållbarhetsstrategi (behåll web scraping för denna)
        if any(word in question_lower for word in ['hållbarhet', 'miljö', 'klimat']):
            hall_content = fetch_web_content("https://kungsbacka.se/kommun-och-politik/utveckling-och-innovation/hallbarhet/vara-steg-mot-hallbarhet")
            if not hall_content.startswith("Kunde inte"):
                relevant = search_in_web_content(question, hall_content)
                if relevant:
                    web_insights.append(("Hållbarhetsstrategi", relevant))
    
    try:
        with st.spinner("Hämtar statistik från SCB och Kolada..."):
            
            # === ALLTID hämta grundläggande befolkningsdata ===
            try:
                bef_data = scb_data.get_population_data()
                if bef_data is not None and not bef_data.empty:
                    latest = bef_data.iloc[-1]
                    previous = bef_data.iloc[-2] if len(bef_data) > 1 else None
                    
                    tillvaxt = ""
                    if previous is not None:
                        change = latest['Befolkning'] - previous['Befolkning']
                        tillvaxt = f" (+{int(change):,} från {previous['År']})"
                    
                    data_context.append(f"📊 **Befolkning (SCB):** {int(latest['Befolkning']):,} invånare ({latest['År']}){tillvaxt}")
                
                # Försök hämta befolkningsförändringar
                try:
                    from data.scb_connector import SCBConnector
                    scb_conn = SCBConnector()
                    pop_change = scb_conn.get_population_change()
                    if pop_change is not None and not pop_change.empty:
                        latest_year = pop_change['År'].max()
                        latest_data = pop_change[pop_change['År'] == latest_year]
                        
                        for typ in ['Folkökning', 'Födda', 'Döda', 'Inflyttade', 'Utflyttade']:
                            row = latest_data[latest_data['Typ'] == typ]
                            if not row.empty:
                                antal = int(row['Antal'].iloc[0])
                                emoji = {'Folkökning': '📈', 'Födda': '👶', 'Döda': '⚰️', 
                                        'Inflyttade': '📥', 'Utflyttade': '📤'}.get(typ, '•')
                                data_context.append(f"{emoji} **{typ} (SCB):** {antal:+,} personer ({latest_year})")
                except:
                    pass  # Fortsätt även om befolkningsförändringar inte fungerar
            except:
                pass
            
            # === SMART KOLADA-SÖKNING - hittar relevanta KPI:er automatiskt ===
            try:
                relevant_kpis = kolada.get_relevant_kpis_for_question(question)
                if relevant_kpis:
                    for kpi_data in relevant_kpis:
                        # Hitta passande emoji baserat på KPI-titeln
                        title = kpi_data.get('titel', '')
                        emoji = '📊'  # Standard
                        
                        if any(word in title.lower() for word in ['skol', 'elev', 'betyg', 'utbildning']):
                            emoji = '🎓'
                        elif any(word in title.lower() for word in ['arbete', 'sysselsätt', 'arbetslös']):
                            emoji = '💼'
                        elif any(word in title.lower() for word in ['barn', 'förskola']):
                            emoji = '👶'
                        elif any(word in title.lower() for word in ['äldre', 'äldreomsorg', '65+', '80+']):
                            emoji = '👴'
                        elif any(word in title.lower() for word in ['miljö', 'klimat', 'utsläpp', 'återvinning']):
                            emoji = '🌍'
                        elif any(word in title.lower() for word in ['kultur', 'fritid', 'bibliotek']):
                            emoji = '🎭'
                        elif any(word in title.lower() for word in ['trygghet', 'brott']):
                            emoji = '🛡️'
                        elif any(word in title.lower() for word in ['bostad', 'lägenhet', 'byggande']):
                            emoji = '🏠'
                        elif any(word in title.lower() for word in ['trafik', 'kollektiv', 'cykel']):
                            emoji = '🚌'
                        
                        data_context.append(
                            f"{emoji} **{title} (Kolada {kpi_data['kpi_id']}):** "
                            f"{kpi_data['värde']:.1f}{kpi_data.get('enhet', '')} ({kpi_data['år']})"
                        )
            except Exception as e:
                st.warning(f"Smart sökning i Kolada misslyckades: {e}")
            
            # === Extra SCB-data för specifika frågor ===
            if any(word in question_lower for word in ['bostad', 'lägenhet', 'hus', 'byggande', 'bostadsbyggande']):
                try:
                    bost_data = scb_data.get_housing_data()
                    if bost_data is not None and not bost_data.empty:
                        latest = bost_data.iloc[-1]
                        data_context.append(f"🏠 **Bostäder (SCB):** {int(latest['Antal']):,} lägenheter totalt ({latest['År']})")
                except:
                    pass
        
    except Exception as e:
        st.error(f"Fel vid datahämtning: {str(e)}")
    
    return data_context, web_insights

# Funktion för att generera svar
def generate_response(question, data_context, web_insights):
    """Genererar ett detaljerat svar baserat på frågan och tillgänglig data"""
    
    # Samla källor
    sources_used = []
    
    # Bygg upp ett rikt dataavsnitt
    context_str = ""
    if data_context:
        context_str = "\n\n## 📊 Aktuell statistik för Kungsbacka\n\n"
        for d in data_context:
            context_str += f"{d}\n"
        sources_used.append("Kolada/SCB-statistik")
    
    # Bygg upp webbinsikter med mer struktur
    web_str = ""
    if web_insights:
        web_str = "\n\n## 📄 Insikter från kommunens dokument\n\n"
        for source, insights in web_insights:
            if insights:
                web_str += f"### {source}:\n"
                sources_used.append(source)
                for insight in insights:
                    if len(insight) > 50:
                        web_str += f"• {insight}\n"
                web_str += "\n"
    
    # Källförteckning
    if sources_used:
        sources_footer = f"\n\n---\n### 📚 Källor\n" + "\n".join(f"✓ {s}" for s in set(sources_used))
    else:
        sources_footer = ""
    
    # Analysera frågan och ge ett DETALJERAT svar
    question_lower = question.lower()
    
    # OM VI HAR DATA ELLER DOKUMENTINSIKTER - använd dem DIREKT i svaret!
    if data_context or web_insights:
        # Speciell hantering för planeringsfrågor
        if any(word in question_lower for word in ['utveckla', 'lämplig', 'plats', 'område', 'var ska', 'bygga', 'planering', 'översiktsplan']):
            intro = """
## 🏗️ Lämpliga platser för utveckling i Kungsbacka

Enligt översiktsplanen och kommunens strategiska dokument prioriteras följande områden:

### Prioriterade orter för utveckling:
1. **Kungsbacka stad** - Huvudort med fokus på förtätning och stadsbyggnadsutveckling
2. **Åsa** - Prioriterad ort med potential för bostäder och verksamheter
3. **Anneberg** - Prioriterad ort med utvecklingspotential

### Övriga orter (kompletterande bebyggelse):
- Fjärås, Onsala, Kullavik, Särö, Vallda, Frillesås

### Strategiska utvecklingsområden:
- **Tölö ängar** (Kungsbacka stad) - Bostäder
- **Voxlöv** (Kungsbacka stad) - Bostäder och verksamheter
- **Boviera** (Åsa) - Bostadsområde
- **Åskatorp** (Åsa) - Blandad bebyggelse
- **Älafors/Lerberg** (Anneberg) - Bostäder
- **Hede station** - Verksamheter och logistik
- **Kungsmässan** - Handel och kontor
"""
            response = f"{intro}\n{context_str}\n{web_str}\n{sources_footer}\n\n### 🗺️ Läs mer\nBesök **Översiktsplanering** för detaljer om planbesked och **Ortanalys** för djupare analys av varje ort."
        else:
            response = f"""
## Svar på din fråga: "{question}"

{context_str}
{web_str}
{sources_footer}

### 💡 Hur kan jag hjälpa dig vidare?
Ställ gärna följdfrågor eller utforska relaterade sidor i dashboarden!
"""
        return response
    
    # ANNARS - ge vägledning
    response = f"""
## Svar på din fråga: "{question}"

Jag hittade tyvärr ingen specifik data för denna fråga i de källor jag har tillgång till.

### 💡 Förslag på hur du kan få mer information:

**📊 För statistik och nyckeltal:**
- **Nyckeltal** - Övergripande måluppfyllelse
- **Kolada** - Detaljerad statistik och jämförelser  
- **Befolkning** - Demografisk analys och prognoser

**🗺️ För planering och utveckling:**
- **Översiktsplanering** - Planbesked, prognoser och uppföljning
- **Karttjänst** - Geografisk översikt av orter
- **Ortanalys** - Detaljerad information per ort

**🤖 Tips för bättre svar:**
Ställ gärna en mer specifik fråga! Exempel:
- "Vilka är de prioriterade orterna för utveckling?"
- "Hur utvecklas befolkningen i Kungsbacka?"
- "Vilka är de största utmaningarna för kommunen?"
- "Vad säger översiktsplanen om bostäder?"
"""
    return response
    
    # GAMLA MALLAR NEDAN (inte används längre)
    
    # === UTMANINGAR ===
    if any(word in question_lower for word in ['utmaning', 'problem', 'svårighet', 'risk', 'hot']):
        response = f"""
## 🎯 Utmaningar och utvecklingsområden för Kungsbacka

Baserat på genomgång av kommunens data och styrdokument kan jag identifiera följande huvudutmaningar:

### 1. Demografiska utmaningar

**Befolkningstillväxt:**
- Kungsbacka växer snabbt (+1-2% årligen), vilket kräver:
  - Utbyggnad av förskolor, skolor och äldreboenden
  - Fler bostäder (målsättning: 1000 nya lägenheter/år)
  - Utökad samhällsservice och infrastruktur

**Åldrande befolkning:**
- Ökande andel 65+ ställer krav på:
  - Hemtjänst och vård
  - Tillgänglig kollektivtrafik
  - Bostadsanpassning

### 2. Bostadsförsörjning och planering

**Utmaningar:**
- Behov av variation i bostadsutbud (hyresrätter, äganderätter, seniorbostäder)
- Balansera förtätning med bevarande av grönområden
- ÖP-följsamhet: 74% av planbesked följer översiktsplanen (mål: >80%)

**Lösningar:**
- Prioritera Kungsbacka stad, Åsa och Fjärås för bostadsbyggande
- Utveckla kollektivtrafiknära lägen
- Samverka med byggherrar tidigt i processen

### 3. Hållbarhet och klimat

**Miljömål:**
- Minska växthusgasutsläpp (nuvarande: ~87 ton CO₂-ekv/invånare)
- Öka andel hållbart resande (mål: 50% kollektivt/cykel/gång)
- Öka återvinningsgrad (nuvarande: 52%, mål: 60%)

**Åtgärder:**
- Utbyggnad av cykelvägar och kollektivtrafik
- Energieffektivisering av kommunala byggnader
- Främja cirkulär ekonomi

### 4. Kompetensförsörjning

**Utmaningar:**
- Säkerställa tillgång till kvalificerad arbetskraft inom:
  - Vård och omsorg
  - Skola och förskola
  - Tekniska och administrativa yrken

**Åtgärder:**
- Samarbete med näringsliv och utbildningsanordnare
- Attraktiv arbetsgivare med goda villkor
- Integration och inkludering på arbetsmarknaden
{context_str}
{web_str}
{sources_footer}

### 💡 Rekommendation
Utforska sidorna **"Kommunens nyckeltal"** och **"Kolada"** för detaljerad uppföljning av dessa områden.
"""
    
    # === TILLVÄXT OCH UTVECKLING ===
    elif any(word in question_lower for word in ['tillväxt', 'utveckling', 'trend', 'framtid', 'prognos']):
        response = f"""
## 📈 Tillväxt och utveckling i Kungsbacka

Kungsbacka är en av Sveriges snabbast växande kommuner med stark positiv utveckling:

### Befolkningstillväxt

**Nuläge:**
- Befolkning 2024: Ca 85,800 invånare
- Årlig tillväxt: +1-2% (ca 800-1700 personer/år)
- Prognos 2030: Över 95,000 invånare

**Drivkrafter:**
- Attraktivt läge mellan Göteborg och Varberg
- God tillgång till arbetstillfällen
- Närhet till natur, kust och skärgård
- Stark inflyttning från Göteborgsregionen

### Ekonomisk utveckling

**Arbetsmarknad:**
- Hög sysselsättningsgrad (~89% förvärvsarbetande 20-64 år)
- Många pendlar till Göteborg (ca 30-40%)
- Växande lokalt näringsliv, särskilt inom:
  - Handel och service
  - Bygg och anläggning
  - Kunskap och teknik

**Bostadsbyggande:**
- Målsättning: 1000 nya lägenheter/år
- Aktuell produktion: ~850 lägenheter/år
- Fokus på Kungsbacka stad, Åsa och Fjärås

### Samhällsutveckling

**Infrastruktur:**
- Utbyggnad av Västkustbanan (snabbare tåg till Göteborg)
- Nya cykelvägar och gång-/cykelbroar
- Förbättrad kollektivtrafik

**Utbildning:**
- Goda skolresultat (meritvärde över rikssnitt)
- Utbyggnad av förskolor och grundskolor
- Nytt gymnasieskolehus planerat

**Hållbarhet:**
- Klimatneutral kommun 2040 (mål)
- Ökat fokus på grön infrastruktur
- Cirkulär ekonomi och avfallsminimering
{context_str}
{web_str}
{sources_footer}

### 🗺️ Nästa steg
Se **"Översiktsplanering"** för detaljer om planerade utvecklingsområden och **"Befolkning"** för demografiska prognoser.
"""
    
    # === JÄMFÖRELSER ===
    elif any(word in question_lower for word in ['jämför', 'skillnad', 'andra kommuner', 'liknande', 'konkurrera']):
        response = f"""
## ⚖️ Kungsbacka jämfört med andra kommuner

### Jämförelse med Göteborgsregionens kommuner

**Styrkor:**
- ✅ Högre meritvärde i grundskolan än många jämförbara kommuner
- ✅ God sysselsättningsgrad (ca 89%)
- ✅ Stark befolkningstillväxt (+1-2% årligen)
- ✅ Attraktivt boende med unik kombination stad-natur-kust
- ✅ Närhet till Göteborg (30 min med tåg)

**Utmaningar:**
- ⚠️ Högre bostadspriser än många andra kommuner i regionen
- ⚠️ Begränsad lokal arbetsmarknad (många pendlar)
- ⚠️ Behov av fortsatt utbyggnad av kollektivtrafik
- ⚠️ Lägre andel hyresrätter än önskvärt

### Liknande kommuner

**Kungsbacka liknar:**
- **Partille** - pendlarkommun till Göteborg, stark tillväxt
- **Mölndal** - nära storstad, växande befolkning
- **Varberg** - kustläge, god livskvalitet

**Kungsbacka skiljer sig genom:**
- Större geografisk area
- Fler och mer spridda tätorter (9 orter)
- Starkare kustprofil och naturvärden

### Regional position

**Bostadsmarknad:**
- Högre priser än Varberg, Falkenberg
- Lägre priser än Göteborgs innerstad
- Konkurrerar med Mölndal, Partille om inflyttare

**Service och näringsliv:**
- Brett utbud inom handel (Kungsmässan, centrum)
- Växande företagande
- God tillgång till kultur och fritidsaktiviteter
{context_str}
{web_str}
{sources_footer}

### 📊 Detaljerade jämförelser
Besök **"Kolada"**-sidan för att jämföra specifika nyckeltal med andra kommuner i Göteborgsregionen och riket.
"""
    
    # === ÖVERSIKTSPLAN/PLANERING ===
    elif any(word in question_lower for word in ['översiktsplan', 'planering', 'markanvändning', 'bebyggelse', 'plan']):
        response = f"""
## 🗺️ Översiktsplanering i Kungsbacka

Översiktsplanen är kommunens viktigaste strategiska dokument för långsiktig planering.

### Huvudprinciper

**Ortstruktur:**
- **Prioriterade orter:** Kungsbacka stad, Åsa, Fjärås
  - Här fokuseras ny bebyggelse
  - Utbyggnad av service och infrastruktur
  - Kollektivtrafiknära lägen

- **Övriga orter:** Onsala, Kullavik, Särö, Vallda, Frillesås, Anneberg
  - Kompletterande bebyggelse
  - Bibehålla orternas karaktär

**Markanvändning:**
- Förtätning i tätorter ("inifrån och ut")
- Bevarande av grönområden och naturvärden
- Balans mellan bebyggelse och landsbygd

### ÖP-följsamhet

**Nuläge:**
- 74% av planbesked följer översiktsplanen
- Målsättning: Minst 80%

**Vanliga avvikelser:**
- Planbesked utanför prioriterade orter
- Större omfattning än ÖP anger
- Konflikt med naturvärden

### Strategiska utvecklingsområden

**Bostäder:**
- Tölö ängar (Kungsbacka stad)
- Voxlöv (Kungsbacka stad)
- Boviera (Åsa)
- Åskatorp (Åsa)

**Näringsliv:**
- Kungsmässan (handel, kontor)
- Hede station (logistik, verksamheter)
- Åsa södra (verksamhetsområde)
{context_str}
{web_str}
{sources_footer}

### 🧭 Läs mer
Besök **"Översiktsplanering"**-sidan för detaljer om planbesked, genomförande och tematisk överblick.
"""
    
    # === HÅLLBARHET ===
    elif any(word in question_lower for word in ['hållbarhet', 'miljö', 'klimat', 'strategi', 'utsläpp']):
        response = f"""
## 🌱 Hållbarhetsarbete i Kungsbacka

Kungsbacka arbetar systematiskt med hållbarhet enligt tre perspektiv:

### Ekologisk hållbarhet

**Klimatmål:**
- Klimatneutral kommun 2040
- Minska växthusgasutsläpp med 70% till 2030 (jämfört med 1990)

**Nuläge:**
- Utsläpp: ~87 ton CO₂-ekv/invånare (2024)
- Återvinning: 52% av hushållsavfall
- Förnybar energi: 68%

**Åtgärder:**
- Utbyggnad av förnybar energi (sol, vind)
- Energieffektivisering av byggnader
- Hållbart resande (cykel, kollektivtrafik)
- Cirkulär ekonomi och avfallsminimering

### Social hållbarhet

**Fokusområden:**
- Jämställdhet och mänskliga rättigheter
- Inkludering och integration
- God livsmiljö för alla åldrar
- Tillgänglig service och omsorg

**Exempel:**
- Trygga boendemiljöer
- Mötesplatser och fritidsaktiviteter
- God skola och utbildning
- Kultur för alla

### Ekonomisk hållbarhet

**Långsiktig ekonomi:**
- Balanserad budget
- Investeringar i infrastruktur
- Attraktivt näringslivsklimat
- Hållbar kompetensförsörjning

**Cirkulär ekonomi:**
- Återbruk och materialåtervinning
- Giftfria kretslopp
- Resurseffektivitet
{context_str}
{web_str}
{sources_footer}

### 📖 Läs mer
Kommunens hållbarhetsstrategi finns på kungsbacka.se under "Våra steg mot hållbarhet".
"""
    
    # === GENERELLT SVAR (mer detaljerat än innan) ===
    else:
        response = f"""
Tack för din fråga om Kungsbacka!

Jag har sökt igenom tillgängliga data och dokument för att ge dig ett relevant svar.
{context_str}
{web_str}

### 💡 Förslag på hur du kan få mer information:

**📊 För statistik och nyckeltal:**
- **Kommunens nyckeltal** - Övergripande måluppfyllelse
- **Kolada** - Detaljerad statistik och jämförelser
- **Befolkning** - Demografisk analys och prognoser

**🗺️ För planering och utveckling:**
- **Översiktsplanering** - Planbesked, prognoser och uppföljning
- **Karttjänst** - Geografisk översikt av orter
- **Ortanalys** - Detaljerad information per ort

**🤖 För dialogstöd:**
Ställ gärna en mer specifik fråga! Exempel:
- "Hur utvecklas befolkningen i Kungsbacka?"
- "Vilka är de största utmaningarna för kommunen?"
- "Vad säger översiktsplanen om utveckling?"
- "Hur arbetar kommunen med hållbarhet?"
{sources_footer}
"""
    
    return response

# Chat-input
if prompt := st.chat_input("Ställ en fråga om Kungsbacka..."):
    # Lägg till användarens meddelande
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Hämta relevant data
    with st.spinner("Söker igenom data och dokument..."):
        data_context, web_insights = get_relevant_data(prompt)
        response = generate_response(prompt, data_context, web_insights)
    
    # Lägg till assistentens svar
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

# Rensa chat-knapp
if st.session_state.messages:
    if st.button("🗑️ Rensa konversation"):
        st.session_state.messages = []
        st.rerun()

# Snabbfrågor
st.markdown("---")
st.markdown("### 💡 Föreslagna frågor")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📈 Hur utvecklas befolkningen?"):
        st.session_state.messages.append({"role": "user", "content": "Hur utvecklas befolkningen i Kungsbacka?"})
        st.rerun()

with col2:
    if st.button("⚠️ Vilka är de största utmaningarna?"):
        st.session_state.messages.append({"role": "user", "content": "Vilka är de största utmaningarna för Kungsbacka kommun?"})
        st.rerun()

with col3:
    if st.button("🗺️ Vad säger översiktsplanen?"):
        st.session_state.messages.append({"role": "user", "content": "Vad säger översiktsplanen om utveckling i Kungsbacka?"})
        st.rerun()

with col4:
    if st.button("🌱 Hållbarhetsarbete?"):
        st.session_state.messages.append({"role": "user", "content": "Vad säger hållbarhetsstrategin om klimatarbetet?"})
        st.rerun()
