# data_sources.py - Förbättrade datakällor med bättre felhantering

import requests
import pandas as pd
import geopandas as gpd
from typing import Dict, List, Optional
import json
from datetime import datetime, timedelta
import os
from config import SCB_CONFIG, SCB_TABLES, GIS_SOURCES, EXTERNAL_APIS, get_standard_query

class SCBDataSource:
    """Förbättrad SCB-klass med bättre felhantering och fler endpoints"""
    
    def __init__(self):
        self.base_url = SCB_CONFIG["base_url"]
        self.user_agent = SCB_CONFIG["user_agent"]
        self.timeout = SCB_CONFIG["timeout"]
        self.cache_dir = "cache"
        
        # Skapa cache-katalog om den inte finns
        os.makedirs(self.cache_dir, exist_ok=True)

    def fetch_population_data(self, region_code: str = "1384") -> pd.DataFrame:
        """Hämtar befolkningsdata från SCB"""
        endpoint = SCB_TABLES["befolkning"]["endpoint"]
        query = get_standard_query("befolkning", region_code)
        
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.post(url, json=query, 
                                   headers={"User-Agent": self.user_agent},
                                   timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_population_response(data)
            
        except Exception as e:
            print(f"Fel vid hämtning av befolkningsdata: {e}")
            return pd.DataFrame()
    
    def fetch_age_groups_data(self, region_code: str = "1384") -> pd.DataFrame:
        """Hämtar åldersgrupperade befolkningsdata från SCB"""
        endpoint = SCB_TABLES["befolkning"]["endpoint"]
        
        # Skapa query för åldersgrupper
        query = {
            "query": [
                {"code": "Region", "selection": {"filter": "item", "values": [region_code]}},
                {"code": "Alder", "selection": {"filter": "item", "values": ["0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80-84", "85-89", "90-94", "95+"]}},
                {"code": "Kon", "selection": {"filter": "item", "values": ["1", "2"]}},
                {"code": "Tid", "selection": {"filter": "item", "values": ["2023", "2022", "2021"]}}
            ],
            "response": {"format": "json"}
        }
        
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.post(url, json=query, 
                                   headers={"User-Agent": self.user_agent},
                                   timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_population_response(data)
            
        except Exception as e:
            print(f"Fel vid hämtning av åldersgruppdata: {e}")
            return pd.DataFrame()
    
    def _parse_population_response(self, data: Dict) -> pd.DataFrame:
        """Parsar SCB-svar för befolkningsdata"""
        rows = []
        for item in data.get("data", []):
            region = item["key"][0]
            alder = item["key"][1]  # Ålder är andra positionen
            kon_code = item["key"][2]  # Kön är tredje positionen
            ar = item["key"][3]
            antal = int(item["values"][0]) if item["values"][0] != ".." else 0
            
            # Konvertera kön-kod till text
            kon = "Män" if kon_code == "1" else "Kvinnor" if kon_code == "2" else "Totalt"
            
            rows.append({
                "Region": region,
                "Kön": kon,
                "Ålder": alder,
                "År": ar,
                "Antal": antal
            })
        
        return pd.DataFrame(rows)

    def fetch_kolada_data(self, indicator_codes: List[str], region_code: str = "1384") -> pd.DataFrame:
        """Hämtar data från Kolada API"""
        try:
            base_url = EXTERNAL_APIS["kolada"]["base_url"]
            
            all_data = []
            for code in indicator_codes:
                url = f"{base_url}/v2/data/kpi/{code}/municipality/{region_code}"
                response = requests.get(url, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("values", []):
                        all_data.append({
                            "indicator": code,
                            "year": item.get("period"),
                            "value": item.get("value"),
                            "municipality": item.get("municipality")
                        })
            
            return pd.DataFrame(all_data)
            
        except Exception as e:
            print(f"Fel vid hämtning från Kolada: {e}")
            return pd.DataFrame()

    def safe_api_request(self, url: str, json_data: Dict = None, max_retries: int = 3) -> Optional[Dict]:
        """Säker API-anrop med retry-logik"""
        for attempt in range(max_retries):
            try:
                if json_data:
                    response = requests.post(url, json=json_data, 
                                           headers={"User-Agent": self.user_agent},
                                           timeout=self.timeout)
                else:
                    response = requests.get(url, 
                                          headers={"User-Agent": self.user_agent},
                                          timeout=self.timeout)
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    print(f"API-anrop misslyckades efter {max_retries} försök: {e}")
                    return None
                else:
                    print(f"Försök {attempt + 1} misslyckades, försöker igen...")
                    time.sleep(1)
        
        return None

class KoladaAPI:
    """Kolada API för kommunala nyckeltal"""
    
    def __init__(self):
        self.base_url = EXTERNAL_APIS["kolada"]["base_url"]
        self.timeout = 30
    
    def get_available_indicators(self) -> pd.DataFrame:
        """Hämtar lista över tillgängliga indikatorer"""
        try:
            url = f"{self.base_url}/v2/kpi"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            return pd.DataFrame(data.get("values", []))
            
        except Exception as e:
            print(f"Fel vid hämtning av Kolada-indikatorer: {e}")
            return pd.DataFrame()
    
    def get_municipality_data(self, kpi_id: str, municipality_id: str = "1384") -> pd.DataFrame:
        """Hämtar data för specifik kommun och indikator"""
        try:
            url = f"{self.base_url}/v2/data/kpi/{kpi_id}/municipality/{municipality_id}"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            return pd.DataFrame(data.get("values", []))
            
        except Exception as e:
            print(f"Fel vid hämtning av Kolada-data: {e}")
            return pd.DataFrame()

class SMHIWeatherAPI:
    """SMHI API för väderdata"""
    
    def __init__(self):
        self.base_url = EXTERNAL_APIS["smhi"]["base_url"]
        self.timeout = 30
    
    def get_weather_observations(self, parameter: int = 1, station: int = 71420) -> pd.DataFrame:
        """Hämtar väderobservationer"""
        try:
            url = f"{self.base_url}/observations/parameter/{parameter}/station/{station}/period/latest-day/data.json"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            observations = []
            
            for obs in data.get("value", []):
                observations.append({
                    "date": obs.get("date"),
                    "value": obs.get("value"),
                    "quality": obs.get("quality")
                })
            
            return pd.DataFrame(observations)
            
        except Exception as e:
            print(f"Fel vid hämtning av SMHI-data: {e}")
            return pd.DataFrame()

class TrafikverketAPI:
    """Trafikverket API för trafikdata"""
    
    def __init__(self):
        self.base_url = EXTERNAL_APIS["trafikverket"]["base_url"]
        self.api_key = EXTERNAL_APIS["trafikverket"].get("api_key", "")
        self.timeout = 30
    
    def get_traffic_data(self, query: str) -> pd.DataFrame:
        """Hämtar trafikdata"""
        if not self.api_key:
            print("Trafikverket API-nyckel saknas")
            return pd.DataFrame()
        
        try:
            headers = {
                "Content-Type": "text/xml",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.post(self.base_url, data=query, 
                                   headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Detta behöver anpassas baserat på Trafikverkets XML-format
            return pd.DataFrame()
            
        except Exception as e:
            print(f"Fel vid hämtning av Trafikverket-data: {e}")
            return pd.DataFrame()

# Skapa globala instanser
scb_data = SCBDataSource()
kolada_api = KoladaAPI()
smhi_api = SMHIWeatherAPI()
trafikverket_api = TrafikverketAPI()
