# indicators.py - Beräkning och analys av nyckelindikatorer

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import streamlit as st
from data_sources import scb_data

@dataclass
class Indicator:
    """Klass för att definiera en indikator"""
    name: str
    value: float
    unit: str
    trend: str  # "up", "down", "stable"
    target: Optional[float] = None
    description: str = ""
    source: str = ""
    updated: str = ""

class PlanningIndicators:
    """Klass för att beräkna och hantera planeringsindikatorer"""
    
    def __init__(self, scb_data, kolada_data, planbesked_df, op_df):
        self.scb_data = scb_data
        self.kolada_data = kolada_data  
        self.planbesked_df = planbesked_df
        self.op_df = op_df
        
    def calculate_population_indicators(self, region_code: str = "1384") -> List[Indicator]:
        """Beräknar befolkningsindikatorer"""
        indicators = []
        
        try:
            # Hämta befolkningsdata
            pop_df = self.scb_data.fetch_population_data(region_code)
            
            if not pop_df.empty:
                # Total befolkning senaste året - använd "tot" åldersgrupp
                latest_year = pop_df["År"].max()
                total_pop = pop_df[
                    (pop_df["År"] == latest_year) &
                    (pop_df["Ålder"] == "tot")
                ]["Antal"].sum()  # Summera män och kvinnor
                
                indicators.append(Indicator(
                    name="Total befolkning",
                    value=total_pop,
                    unit="personer",
                    trend="up",
                    description=f"Total befolkning {latest_year}",
                    source="SCB",
                    updated=datetime.now().strftime("%Y-%m-%d")
                ))
                
                # Befolkningstillväxt
                if len(pop_df["År"].unique()) >= 2:
                    years = sorted(pop_df["År"].unique())
                    current_year = years[-1]
                    prev_year = years[-2]
                    
                    pop_current = pop_df[
                        (pop_df["År"] == current_year) &
                        (pop_df["Ålder"] == "tot")
                    ]["Antal"].sum()  # Summera män och kvinnor
                    
                    pop_prev = pop_df[
                        (pop_df["År"] == prev_year) &
                        (pop_df["Ålder"] == "tot")
                    ]["Antal"].sum()  # Summera män och kvinnor
                    
                    if pop_prev > 0:
                        growth_rate = ((pop_current - pop_prev) / pop_prev) * 100
                        trend = "up" if growth_rate > 0 else "down" if growth_rate < 0 else "stable"
                        
                        indicators.append(Indicator(
                            name="Befolkningstillväxt",
                            value=round(growth_rate, 2),
                            unit="%",
                            trend=trend,
                            target=1.0,  # Målsättning 1% tillväxt
                            description=f"Årlig tillväxt {prev_year}-{current_year}",
                            source="SCB",
                            updated=datetime.now().strftime("%Y-%m-%d")
                        ))
                
                # Åldersstruktur - andel över 65 (använd enskilda åldrar 65+)
                try:
                    age_data = scb_data.fetch_age_groups_data()
                    if not age_data.empty:
                        # Filtrera åldrar 65 och uppåt
                        elderly_pop = age_data[
                            (age_data["År"] == latest_year) & 
                            (age_data["Ålder"].astype(str).str.isdigit()) &
                            (age_data["Ålder"].astype(int) >= 65)
                        ]["Antal"].sum()
                    else:
                        elderly_pop = 0
                except Exception:
                    elderly_pop = 0
                
                if total_pop > 0:
                    elderly_percent = (elderly_pop / total_pop) * 100
                    indicators.append(Indicator(
                        name="Andel 65+ år",
                        value=round(elderly_percent, 1),
                        unit="%",
                        trend="up",
                        description="Andel av befolkningen över 65 år",
                        source="SCB",
                        updated=datetime.now().strftime("%Y-%m-%d")
                    ))
                
        except Exception as e:
            st.warning(f"Kunde inte beräkna befolkningsindikatorer: {e}")
            
        return indicators
    
    def calculate_planning_indicators(self) -> List[Indicator]:
        """Beräknar planeringsindikatorer baserat på planbesked och ÖP"""
        indicators = []
        
        try:
            if not self.planbesked_df.empty:
                total_planbesked = len(self.planbesked_df)
                planbesked_op = self.planbesked_df["följer_op"].sum()
                
                # Andel planbesked som följer ÖP
                if total_planbesked > 0:
                    op_compliance = (planbesked_op / total_planbesked) * 100
                    trend = "up" if op_compliance >= 70 else "down"
                    
                    indicators.append(Indicator(
                        name="ÖP-följsamhet planbesked",
                        value=round(op_compliance, 1),
                        unit="%",
                        trend=trend,
                        target=80.0,
                        description="Andel planbesked som följer översiktsplanen",
                        source="Kommunens ärendehantering",
                        updated=datetime.now().strftime("%Y-%m-%d")
                    ))
                
                # Antal planbesked senaste året
                indicators.append(Indicator(
                    name="Antal planbesked",
                    value=total_planbesked,
                    unit="st",
                    trend="stable",
                    description="Totalt antal planbesked under perioden",
                    source="Kommunens ärendehantering",
                    updated=datetime.now().strftime("%Y-%m-%d")
                ))
                
        except Exception as e:
            st.warning(f"Kunde inte beräkna planeringsindikatorer: {e}")
            
        return indicators
    
    def calculate_sustainability_indicators(self) -> List[Indicator]:
        """Beräknar hållbarhetsindikatorer"""
        indicators = []
        
        # Dummy-data för demonstration - ersätt med riktiga beräkningar
        indicators.extend([
            Indicator(
                name="Grönområden per invånare",
                value=45.2,
                unit="m²",
                trend="stable",
                target=50.0,
                description="Tillgång till grönområden per person",
                source="GIS-analys",
                updated=datetime.now().strftime("%Y-%m-%d")
            ),
            Indicator(
                name="Kollektivtrafikåtkomst",
                value=78.5,
                unit="%",
                trend="up",
                target=85.0,
                description="Andel som bor inom 500m från kollektivtrafik",
                source="Trafikverket/Västtrafik",
                updated=datetime.now().strftime("%Y-%m-%d")
            ),
            Indicator(
                name="Cykelvägstäthet",
                value=1.2,
                unit="km/km²",
                trend="up",
                target=1.5,
                description="Längd cykelvägar per kvadratkilometer",
                source="Kommunens väghållning",
                updated=datetime.now().strftime("%Y-%m-%d")
            )
        ])
        
        return indicators
    
    def calculate_housing_indicators(self) -> List[Indicator]:
        """Beräknar bostadsindikatorer"""
        indicators = []
        
        try:
            # Använd Kolada-data för bostadsindikatorer
            kolada_df = self.kolada_data.get_municipality_data("1384")
            
            if not kolada_df.empty:
                # Hitta nybyggda lägenheter
                nybyggda = kolada_df[kolada_df["indikator"].str.contains("lägenheter", na=False)]
                if not nybyggda.empty:
                    value = nybyggda.iloc[0]["värde"]
                    indicators.append(Indicator(
                        name="Nybyggda lägenheter",
                        value=value,
                        unit="per 1000 inv",
                        trend="up" if value > 4.0 else "down",
                        target=5.0,
                        description="Nybyggda lägenheter per 1000 invånare",
                        source="Kolada/SCB",
                        updated=datetime.now().strftime("%Y-%m-%d")
                    ))
        
        except Exception as e:
            st.warning(f"Kunde inte beräkna bostadsindikatorer: {e}")
        
        # Lägg till dummy-indikatorer
        indicators.extend([
            Indicator(
                name="Bostadskö",
                value=2850,
                unit="personer",
                trend="up",
                description="Antal personer i bostadskö",
                source="Kommunens bostadsförmedling",
                updated=datetime.now().strftime("%Y-%m-%d")
            ),
            Indicator(
                name="Genomsnittlig boyta",
                value=118,
                unit="m²",
                trend="stable",
                description="Genomsnittlig boyta per hushåll",
                source="SCB Bostads- och byggnadsstatistik",
                updated=datetime.now().strftime("%Y-%m-%d")
            )
        ])
        
        return indicators
    
    def get_all_indicators(self) -> Dict[str, List[Indicator]]:
        """Returnerar alla indikatorer grupperade per kategori"""
        return {
            "Befolkning": self.calculate_population_indicators(),
            "Planering": self.calculate_planning_indicators(), 
            "Hållbarhet": self.calculate_sustainability_indicators(),
            "Bostäder": self.calculate_housing_indicators()
        }
    
    def get_dashboard_summary(self) -> Dict:
        """Returnerar en sammanfattning för dashboard"""
        all_indicators = self.get_all_indicators()
        
        summary = {
            "total_indicators": sum(len(indicators) for indicators in all_indicators.values()),
            "categories": len(all_indicators),
            "trends": {"up": 0, "down": 0, "stable": 0},
            "targets_met": 0,
            "total_targets": 0
        }
        
        for category, indicators in all_indicators.items():
            for indicator in indicators:
                summary["trends"][indicator.trend] += 1
                
                if indicator.target is not None:
                    summary["total_targets"] += 1
                    if ((indicator.trend == "up" and indicator.value >= indicator.target) or
                        (indicator.trend == "down" and indicator.value <= indicator.target)):
                        summary["targets_met"] += 1
        
        if summary["total_targets"] > 0:
            summary["target_achievement_rate"] = (summary["targets_met"] / summary["total_targets"]) * 100
        else:
            summary["target_achievement_rate"] = 0
            
        return summary

def create_indicator_dashboard(indicators_dict: Dict[str, List[Indicator]]):
    """Skapar en Streamlit-dashboard för indikatorer"""
    
    st.header("📊 Nyckelindikatorer för Kungsbacka")
    
    # Översikt
    all_indicators = []
    for indicators in indicators_dict.values():
        all_indicators.extend(indicators)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Totalt antal indikatorer", len(all_indicators))
    
    with col2:
        up_trends = sum(1 for ind in all_indicators if ind.trend == "up")
        st.metric("Positiv trend", up_trends, delta=f"{up_trends}/{len(all_indicators)}")
    
    with col3:
        targets_with_goals = [ind for ind in all_indicators if ind.target is not None]
        st.metric("Indikatorer med mål", len(targets_with_goals))
    
    with col4:
        last_updated = max((ind.updated for ind in all_indicators), default="Okänt")
        st.metric("Senast uppdaterad", last_updated)
    
    # Visa indikatorer per kategori
    for category, indicators in indicators_dict.items():
        with st.expander(f"📈 {category} ({len(indicators)} indikatorer)", expanded=True):
            
            for indicator in indicators:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    trend_emoji = {"up": "📈", "down": "📉", "stable": "➡️"}[indicator.trend]
                    st.write(f"**{indicator.name}** {trend_emoji}")
                    if indicator.description:
                        st.caption(indicator.description)
                
                with col2:
                    delta = None
                    if indicator.target is not None:
                        delta = f"Mål: {indicator.target} {indicator.unit}"
                    st.metric(indicator.name, f"{indicator.value} {indicator.unit}", delta=delta)
                
                with col3:
                    st.caption(f"Källa: {indicator.source}")
                    st.caption(f"Uppdaterad: {indicator.updated}")
                
                if indicator.target is not None:
                    progress = min(indicator.value / indicator.target, 1.0) if indicator.target > 0 else 0
                    st.progress(progress)
