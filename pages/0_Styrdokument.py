import streamlit as st

st.set_page_config(
    page_title="Styrdokument - Kungsbacka",
    page_icon="📋",
    layout="wide"
)

# CSS för snygga kort
st.markdown("""
<style>
    .document-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #1e3a8a;
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
        display: flex;
        flex-direction: column;
        margin-bottom: 1.5rem;
    }
    .document-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .document-title {
        color: #1e3a8a;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    .document-description {
        color: #4b5563;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 1rem;
        flex-grow: 1;
    }
    .document-link {
        display: inline-block;
        background: #1e3a8a;
        color: white !important;
        padding: 0.6rem 1.2rem;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 500;
        font-size: 0.9rem;
        transition: background 0.2s;
        text-align: center;
    }
    .document-link:hover {
        background: #3b82f6;
        text-decoration: none;
    }
    .page-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    .page-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    .page-header p {
        color: #e0e7ff;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidhuvud
st.markdown("""
<div class="page-header">
    <h1>Styrdokument och Vision</h1>
    <p>Kungsbacka kommuns övergripande dokument och beslut</p>
</div>
""", unsafe_allow_html=True)

# Dokumentkort
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="document-card">
        <div class="document-title">Kungsbackas Vision</div>
        <div class="document-description">
            Översiktsplanen är kommunens strategiska planeringsdokument som visar hur mark- och vattenområden 
            ska användas och hur den bebyggda miljön ska utvecklas och bevaras.
        </div>
        <a href="https://kungsbacka.se/download/18.664f3731952dcb17b8813a4/1740567574918/Vision%202030.pdf" 
           target="_blank" class="document-link">Läs mer om visionen</a>
    </div>
    """, unsafe_allow_html=True)
    
with col2:
    st.markdown("""
    <div class="document-card">
        <div class="document-title">Översiktsplan</div>
        <div class="document-description">
            Översiktsplanen är kommunens strategiska planeringsdokument som visar hur mark- och vattenområden 
            ska användas och hur den bebyggda miljön ska utvecklas och bevaras.
        </div>
        <a href="https://karta.kungsbacka.se/oversiktsplan" 
           target="_blank" class="document-link">Gå till översiktsplanen</a>
    </div>
    """, unsafe_allow_html=True)

col3, col4 = st.columns(2, gap="large")

with col3:
    st.markdown("""
    <div class="document-card">
        <div class="document-title">Våra Steg mot Hållbarhet</div>
        <div class="document-description">
            Översiktsplanen är kommunens strategiska planeringsdokument som visar hur mark- och vattenområden 
            ska användas och hur den bebyggda miljön ska utvecklas och bevaras.
        </div>
        <a href="https://kungsbacka.se/kommun-och-politik/utveckling-och-innovation/hallbarhet/vara-steg-mot-hallbarhet" 
           target="_blank" class="document-link">Läs om hållbarhetsarbetet</a>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="document-card">
        <div class="document-title">Budget och Verksamhetsplan</div>
        <div class="document-description">
            Översiktsplanen är kommunens strategiska planeringsdokument som visar hur mark- och vattenområden 
            ska användas och hur den bebyggda miljön ska utvecklas och bevaras.
        </div>
        <a href="https://kungsbacka.se/kommun-och-politik/ekonomi-och-uppfoljning/budget-och-arsredovisning" 
           target="_blank" class="document-link">Se budget och verksamhetsplan</a>
    </div>
    """, unsafe_allow_html=True)

# Extra information
st.markdown("---")
st.markdown("""
### Om styrdokumenten

Dessa dokument utgör grunden för Kungsbacka kommuns planering och utveckling. De är antagna 
av kommunfullmäktige och revideras regelbundet för att säkerställa att de speglar kommunens 
aktuella mål och förutsättningar.

**Viktiga beslut och dokument:**
- Visionen anger den långsiktiga riktningen
- Översiktsplanen vägleder den fysiska planeringen
- Hållbarhetsstrategin integrerar ekonomisk, social och miljömässig hållbarhet
- Budget och verksamhetsplan konkretiserar de årliga prioriteringarna
""")
