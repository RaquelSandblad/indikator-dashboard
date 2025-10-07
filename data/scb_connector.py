"""
SCB API Connector - Komplett integration med Statistiska Centralbyrån
Hämtar befolkning, bostäder, arbetsmarknad med robust caching och felhantering
"""

import requests
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import streamlit as st


class SCBConnector:
    """Komplett SCB API-integration med caching"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.base_url = "https://api.scb.se/OV0104/v1/doris/sv/ssd"
        self.cache_dir = cache_dir
        self.cache_days = 7  # Cache i 7 dagar
        self.timeout = 30
        
        # Kommuner
        self.KUNGSBACKA_KOD = "1384"
        self.HALLAND_KOMMUNER = {
            "1383": "Varberg",
            "1384": "Kungsbacka", 
            "1380": "Halmstad",
            "1381": "Laholm",
            "1382": "Falkenberg",
            "1315": "Hylte"
        }
        
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, endpoint: str, params_hash: str) -> str:
        """Skapar cache-filväg"""
        safe_endpoint = endpoint.replace('/', '_')
        return os.path.join(self.cache_dir, f"scb_{safe_endpoint}_{params_hash}.json")
    
    def _is_cache_valid(self, cache_path: str) -> bool:
        """Kontrollerar om cache är giltig"""
        if not os.path.exists(cache_path):
            return False
        
        modified_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        age = datetime.now() - modified_time
        
        return age < timedelta(days=self.cache_days)
    
    def _load_cache(self, cache_path: str) -> Optional[dict]:
        """Laddar data från cache"""
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Cache-läsfel: {e}")
            return None
    
    def _save_cache(self, cache_path: str, data: dict):
        """Sparar data till cache"""
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Cache-skrivfel: {e}")
    
    def _fetch_from_api(self, endpoint: str, query: dict) -> dict:
        """Hämtar data från SCB API"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.post(
                url,
                json=query,
                headers={"User-Agent": "Kungsbacka-Dashboard/2.0"},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"❌ SCB API-fel: {e}")
            raise
    
    def get_data(self, endpoint: str, query: dict, use_cache: bool = True) -> dict:
        """Generisk metod för att hämta data med cache"""
        params_hash = str(hash(json.dumps(query, sort_keys=True)))
        cache_path = self._get_cache_path(endpoint, params_hash)
        
        # Försök läsa från cache
        if use_cache:
            cached_data = self._load_cache(cache_path)
            if cached_data and self._is_cache_valid(cache_path):
                return cached_data
        
        # Hämta från API
        data = self._fetch_from_api(endpoint, query)
        
        # Spara till cache
        if use_cache:
            self._save_cache(cache_path, data)
        
        return data
    
    # ==================== BEFOLKNING ====================
    
    def get_population_total(self, kommun_kod: str = None, years: List[str] = None) -> pd.DataFrame:
        """Hämtar total befolkning per år och kön"""
        if kommun_kod is None:
            kommun_kod = self.KUNGSBACKA_KOD
        
        if years is None:
            current_year = datetime.now().year
            # SCB har ofta endast föregående års data tillgänglig
            years = [str(y) for y in range(current_year - 10, current_year)]
        
        endpoint = "BE/BE0101/BE0101A/BefolkningNy"
        query = {
            "query": [
                {"code": "Region", "selection": {"filter": "item", "values": [kommun_kod]}},
                {"code": "Alder", "selection": {"filter": "item", "values": ["tot"]}},
                {"code": "Kon", "selection": {"filter": "item", "values": ["1", "2"]}},
                {"code": "Tid", "selection": {"filter": "item", "values": years}}
            ],
            "response": {"format": "json"}
        }
        
        data = self.get_data(endpoint, query)
        
        # Parsa respons
        rows = []
        for item in data.get("data", []):
            # values[0] är folkmängd, values[1] är folkökning (om det finns)
            value = item["values"][0]
            rows.append({
                "År": item["key"][3],
                "Kön": "Män" if item["key"][2] == "1" else "Kvinnor",
                "Antal": int(value) if value != ".." else 0
            })
        
        return pd.DataFrame(rows)
    
    def get_age_distribution(self, kommun_kod: str = None, year: str = None) -> pd.DataFrame:
        """Hämtar åldersfördelning för ett specifikt år"""
        if kommun_kod is None:
            kommun_kod = self.KUNGSBACKA_KOD
        
        if year is None:
            year = str(datetime.now().year - 1)  # Senaste kompletta året
        
        endpoint = "BE/BE0101/BE0101A/BefolkningNy"
        
        # SCB har gräns på antal värden - dela upp i batchar
        all_rows = []
        
        # Batch åldrar i grupper om 50
        for batch_start in range(0, 100, 50):
            batch_end = min(batch_start + 50, 100)
            ages = [str(i) for i in range(batch_start, batch_end)]
            
            query = {
                "query": [
                    {"code": "Region", "selection": {"filter": "item", "values": [kommun_kod]}},
                    {"code": "Alder", "selection": {"filter": "item", "values": ages}},
                    {"code": "Kon", "selection": {"filter": "item", "values": ["1", "2"]}},
                    {"code": "Tid", "selection": {"filter": "item", "values": [year]}}
                ],
                "response": {"format": "json"}
            }
            
            try:
                data = self.get_data(endpoint, query)
                
                # Parsa respons och gruppera i åldersintervall
                for item in data.get("data", []):
                    age = item["key"][1]
                    if age == "100+":
                        age_num = 100
                    else:
                        age_num = int(age)
                    
                    # Gruppera i 5-årsintervall
                    if age_num < 5:
                        age_group = "0-4"
                    elif age_num < 10:
                        age_group = "5-9"
                    elif age_num < 15:
                        age_group = "10-14"
                    elif age_num < 20:
                        age_group = "15-19"
                    elif age_num < 25:
                        age_group = "20-24"
                    elif age_num < 30:
                        age_group = "25-29"
                    elif age_num < 35:
                        age_group = "30-34"
                    elif age_num < 40:
                        age_group = "35-39"
                    elif age_num < 45:
                        age_group = "40-44"
                    elif age_num < 50:
                        age_group = "45-49"
                    elif age_num < 55:
                        age_group = "50-54"
                    elif age_num < 60:
                        age_group = "55-59"
                    elif age_num < 65:
                        age_group = "60-64"
                    elif age_num < 70:
                        age_group = "65-69"
                    elif age_num < 75:
                        age_group = "70-74"
                    elif age_num < 80:
                        age_group = "75-79"
                    elif age_num < 85:
                        age_group = "80-84"
                    elif age_num < 90:
                        age_group = "85-89"
                    elif age_num < 95:
                        age_group = "90-94"
                    else:
                        age_group = "95+"
                    
                    value = item["values"][0]
                    all_rows.append({
                        "Åldersgrupp": age_group,
                        "Kön": "Män" if item["key"][2] == "1" else "Kvinnor",
                        "Antal": int(value) if value != ".." else 0
                    })
            except Exception as e:
                print(f"⚠️ Fel vid hämtning av åldrar {batch_start}-{batch_end}: {e}")
        
        # Aggregera per åldersgrupp
        df = pd.DataFrame(all_rows)
        if not df.empty:
            df = df.groupby(["Åldersgrupp", "Kön"], as_index=False)["Antal"].sum()
        
        return df
    
    def get_population_change(self, kommun_kod: str = None, years: List[str] = None) -> pd.DataFrame:
        """Hämtar befolkningsförändringar (födda, döda, inflyttade, utflyttade)"""
        if kommun_kod is None:
            kommun_kod = self.KUNGSBACKA_KOD
        
        if years is None:
            current_year = datetime.now().year
            # Hämta de senaste 6 åren, men INTE innevarande år (data inte tillgängligt än)
            years = [str(y) for y in range(current_year - 6, current_year)]
        
        # UPPDATERAD ENDPOINT 2025
        endpoint = "BE/BE0101/BE0101G/BefforandrKvRLK"
        query = {
            "query": [
                {"code": "Region", "selection": {"filter": "item", "values": [kommun_kod]}},
                {"code": "Tid", "selection": {"filter": "item", "values": years}}
            ],
            "response": {"format": "json"}
        }
        
        try:
            data = self.get_data(endpoint, query)
            
            # Parsa respons - ny struktur
            # Key[0]=Region, Key[1]=Förändringskod, Key[2]=Period, Key[3]=År
            rows = []
            forandringar_map = {
                "110": "Folkökning",
                "115": "Födda",
                "130": "Döda",
                "135": "Födelseöverskott",
                "140": "Inflyttade",
                "150": "Utflyttade",
                "230": "Flyttnetto"
            }
            
            for item in data.get("data", []):
                period = item["key"][2]
                # Filtrera endast helårsdata
                if period == "hel":
                    forandring_code = item["key"][1]
                    # Bara relevanta koder
                    if forandring_code in forandringar_map:
                        rows.append({
                            "År": item["key"][3],
                            "Typ": forandringar_map[forandring_code],
                            "Antal": int(item["values"][0]) if item["values"][0] != ".." else 0
                        })
            
            return pd.DataFrame(rows)
        
        except Exception as e:
            print(f"⚠️ Kunde inte hämta befolkningsförändringar: {e}")
            return pd.DataFrame(columns=["År", "Typ", "Antal"])
    
    # ==================== BOSTÄDER ====================
    
    def get_housing_stock(self, kommun_kod: str = None, years: List[str] = None) -> pd.DataFrame:
        """Hämtar bostadsbestånd (lägenheter i flerbostadshus och småhus)"""
        if kommun_kod is None:
            kommun_kod = self.KUNGSBACKA_KOD
        
        if years is None:
            current_year = datetime.now().year
            # Använd bara år där data finns (2013-2024)
            years = [str(y) for y in range(max(2013, current_year - 5), min(2025, current_year + 1))]
        
        endpoint = "BO/BO0104/BO0104D/BO0104T01"
        query = {
            "query": [
                {"code": "Region", "selection": {"filter": "item", "values": [kommun_kod]}},
                {"code": "Hustyp", "selection": {"filter": "item", "values": ["FLERBOST", "SMÅHUS"]}},
                {"code": "ContentsCode", "selection": {"filter": "item", "values": ["BO0104AG"]}},
                {"code": "Tid", "selection": {"filter": "item", "values": years}}
            ],
            "response": {"format": "json"}
        }
        
        try:
            data = self.get_data(endpoint, query)
            
            # Parsa respons
            rows = []
            hustyp_mapping = {"FLERBOST": "Flerbostadshus", "SMÅHUS": "Småhus"}
            
            for item in data.get("data", []):
                rows.append({
                    "År": item["key"][2],  # Index 2 är år i denna tabell
                    "Hustyp": hustyp_mapping.get(item["key"][1], item["key"][1]),
                    "Antal": int(item["values"][0]) if item["values"][0] != ".." else 0
                })
            
            return pd.DataFrame(rows)
        
        except Exception as e:
            print(f"⚠️ Kunde inte hämta bostadsbestånd: {e}")
            return pd.DataFrame(columns=["År", "Hustyp", "Antal"])
    
    def get_new_construction(self, kommun_kod: str = None, years: List[str] = None) -> pd.DataFrame:
        """Hämtar nybyggnation av bostäder"""
        if kommun_kod is None:
            kommun_kod = self.KUNGSBACKA_KOD
        
        if years is None:
            current_year = datetime.now().year
            years = [str(y) for y in range(current_year - 5, current_year)]
        
        endpoint = "BO/BO0101/BO0101A/NyByggBostLghAr"
        query = {
            "query": [
                {"code": "Region", "selection": {"filter": "item", "values": [kommun_kod]}},
                {"code": "Hustyp", "selection": {"filter": "item", "values": ["FLERB", "SMÅ"]}},
                {"code": "ContentsCode", "selection": {"filter": "item", "values": ["BO0101N1"]}},  # Färdigställda
                {"code": "Tid", "selection": {"filter": "item", "values": years}}
            ],
            "response": {"format": "json"}
        }
        
        try:
            data = self.get_data(endpoint, query)
            
            # Parsa respons
            rows = []
            hustyp_mapping = {"FLERB": "Flerbostadshus", "SMÅ": "Småhus"}
            
            for item in data.get("data", []):
                rows.append({
                    "År": item["key"][3],
                    "Hustyp": hustyp_mapping.get(item["key"][1], item["key"][1]),
                    "Antal": int(item["values"][0]) if item["values"][0] != ".." else 0
                })
            
            return pd.DataFrame(rows)
        
        except Exception as e:
            print(f"⚠️ Kunde inte hämta nybyggnation: {e}")
            return pd.DataFrame(columns=["År", "Hustyp", "Antal"])
    
    # ==================== JÄMFÖRELSER ====================
    
    def compare_municipalities(self, metric: str, kommun_koder: List[str] = None, year: str = None) -> pd.DataFrame:
        """Jämför kommuner för ett specifikt nyckeltal"""
        if kommun_koder is None:
            kommun_koder = list(self.HALLAND_KOMMUNER.keys())
        
        if year is None:
            year = str(datetime.now().year - 1)
        
        if metric == "befolkning":
            results = []
            for kod in kommun_koder:
                df = self.get_population_total(kod, [year])
                if not df.empty:
                    total = df['Antal'].sum()
                    results.append({
                        "Kommun": self.HALLAND_KOMMUNER.get(kod, kod),
                        "Kod": kod,
                        "Värde": total
                    })
            return pd.DataFrame(results)
        
        return pd.DataFrame()
    
    def get_kommun_namn(self, kod: str) -> str:
        """Hämtar kommunnamn från kod"""
        return self.HALLAND_KOMMUNER.get(kod, f"Kommun {kod}")


# Testfunktion
if __name__ == "__main__":
    print("🔄 Testar SCB Connector...")
    
    scb = SCBConnector()
    
    # Test 1: Total befolkning
    print("\n📊 Test 1: Total befolkning")
    pop = scb.get_population_total()
    if not pop.empty:
        print(f"✅ Hämtade {len(pop)} rader")
        print(pop.head())
    
    # Test 2: Åldersfördelning
    print("\n👥 Test 2: Åldersfördelning")
    age = scb.get_age_distribution()
    if not age.empty:
        print(f"✅ Hämtade {len(age)} rader")
        print(age.head())
    
    # Test 3: Bostadsbestånd
    print("\n🏠 Test 3: Bostadsbestånd")
    housing = scb.get_housing_stock()
    if not housing.empty:
        print(f"✅ Hämtade {len(housing)} rader")
        print(housing.head())
    
    print("\n✅ Alla tester genomförda!")
