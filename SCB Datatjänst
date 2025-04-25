# scb_service.py
import requests
import pandas as pd
from datetime import datetime
import os
import json

class SCBService:
    def __init__(self, cache_dir="cache"):
        """Initialiserar SCB-tjänsten med cachefunktionalitet."""
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.base_url = "https://api.scb.se/OV0104/v1/doris/sv/ssd"
    
    def _get_cache_path(self, endpoint, query_hash):
        """Skapar en sökväg för cachefilen baserat på endpoint och fråga."""
        return os.path.join(self.cache_dir, f"{endpoint.replace('/', '_')}_{query_hash}.json")
    
    def _check_cache(self, cache_path, max_age_hours=24):
        """Kontrollerar om cachefilen finns och är färsk."""
        if not os.path.exists(cache_path):
            return False
        
        file_time = os.path.getmtime(cache_path)
        file_age_hours = (datetime.now().timestamp() - file_time) / 3600
        
        return file_age_hours <= max_age_hours
    
    def _query_hash(self, query):
        """Skapar en hash av frågan för cache-identifiering."""
        return str(hash(json.dumps(query, sort_keys=True)))
    
    def fetch_data(self, endpoint, query, max_cache_age_hours=24):
        """Hämtar data från SCB API med cache-stöd."""
        query_hash = self._query_hash(query)
        cache_path = self._get_cache_path(endpoint, query_hash)
        
        # Kontrollera cache
        if self._check_cache(cache_path, max_cache_age_hours):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Cache-läsfel: {e}")
        
        # Hämta från API om cache saknas eller är gammal
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.post(url, json=query)
            response.raise_for_status()
            data = response.json()
            
            # Spara till cache
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            
            return data
        except Exception as e:
            print(f"API-fel: {e}")
            raise
    
    def get_population_by_age_gender(self, region_code="1384", year="2023"):
        """Hämtar befolkningsdata per ålder och kön för en specifik region och år."""
        endpoint = "BE/BE0101/BE0101A/BefolkningNy"
        
        query = {
            "query": [
                {"code": "Region", "selection": {"filter": "item", "values": [region_code]}},
                {"code": "Kon", "selection": {"filter": "item", "values": ["1", "2"]}},
                {"code": "Alder", "selection": {"filter": "item", "values": [str(i) for i in range(0, 100)] + ["100+"]}},
                {"code": "Tid", "selection": {"filter": "item", "values": [year]}}
            ],
            "response": {"format": "json"}
        }
        
        data = self.fetch_data(endpoint, query)
        
        rows = data.get("data", [])
        parsed = []
        for row in rows:
            kön = "Män" if row["key"][1] == "1" else "Kvinnor"
            ålder = row["key"][2]
            antal = int(row["values"][0])
            parsed.append({"Kön": kön, "Ålder": ålder, "Antal": antal})
        
        df = pd.DataFrame(parsed)
        if not df.empty:
            df["Ålder"] = df["Ålder"].replace("100+", "100").astype(int)
            df = df.sort_values(by="Ålder")
        
        return df
    
    def get_region_list(self):
        """Hämtar en lista över alla kommuner och regioner."""
        endpoint = "BE/BE0101/BE0101A/BefolkningNy"
        
        try:
            url = f"{self.base_url}/{endpoint}/region"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            regions = []
            for i, code in enumerate(data["values"]):
                text = data["valueTexts"][i]
                regions.append({"kod": code, "namn": text})
            
            return pd.DataFrame(regions)
        except Exception as e:
            print(f"Fel vid hämtning av regioner: {e}")
            return pd.DataFrame(columns=["kod", "namn"])
    
    def get_population_trend(self, region_code="1384", years=None):
        """Hämtar befolkningsutveckling över tid för en specifik region."""
        if years is None:
            current_year = datetime.now().year
            years = [str(year) for year in range(current_year-10, current_year)]
        
        endpoint = "BE/BE0101/BE0101A/BefolkningNy"
        
        query = {
            "query": [
                {"code": "Region", "selection": {"filter": "item", "values": [region_code]}},
                {"code": "Kon", "selection": {"filter": "item", "values": ["1+2"]}},  # Båda könen
                {"code": "Alder", "selection": {"filter": "agg:Ålder5år", "values": ["TOT"]}},  # Alla åldrar
                {"code": "Tid", "selection": {"filter": "item", "values": years}}
            ],
            "response": {"format": "json"}
        }
        
        data = self.fetch_data(endpoint, query)
        
        rows = data.get("data", [])
        parsed = []
        for row in rows:
            år = row["key"][3]
            antal = int(row["values"][0])
            parsed.append({"År": år, "Antal": antal})
        
        df = pd.DataFrame(parsed)
        return df

# Exempel på användning
if __name__ == "__main__":
    scb = SCBService()
    df = scb.get_population_by_age_gender()
    print(df.head())
    
    regions = scb.get_region_list()
    print(regions.head())
    
    trend = scb.get_population_trend()
    print(trend.head())
