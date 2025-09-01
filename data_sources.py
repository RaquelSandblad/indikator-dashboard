# data_sources.py - Förbättrade datakällor med bättre felhantering

import requests
import pandas as pd
import geopandas as gpd
from typing import Dict, List, Optional
import json
from datetime import datetime, timedelta
import os
import time
from config import SCB_CONFIG, SCB_TABLES, GIS_SOURCES, EXTERNAL_APIS, get_standard_query
from pathlib import Path

# PPTX loader (infonet)
try:
    from data.infonet_loader import load_pptx_tables
except Exception:
    load_pptx_tables = None

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
        try:
            url = f"{EXTERNAL_APIS['scb']['base_url']}/v1/sv/ssd/START/BE/BE0101/BE0101A/BefolkningNy"
            
            # Standard query för befolkning
            query = get_standard_query(region_code)
            
            response = requests.post(url, json=query, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_population_response(data)
            else:
                print(f"Fel vid hämtning av data: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Fel vid hämtning av befolkningsdata: {e}")
            return pd.DataFrame()

    def fetch_age_distribution(self, region_code: str = "1384") -> pd.DataFrame:
        """Hämtar åldersfördelning från SCB för ålderspyramid"""
        try:
            # Använd en mer detaljerad åldersindeling
            url = f"{EXTERNAL_APIS['scb']['base_url']}/v1/sv/ssd/START/BE/BE0101/BE0101A/BefolkningNy"
            
            # Query för att få åldersfördelning per kön
            query = {
                "query": [
                    {
                        "code": "Region",
                        "selection": {"filter": "vs:RegionKommun07", "values": [region_code]}
                    },
                    {
                        "code": "Alder",
                        "selection": {"filter": "item", "values": [
                            "0", "1", "2", "3", "4", "5-9", "10-14", "15-19", 
                            "20-24", "25-29", "30-34", "35-39", "40-44", "45-49",
                            "50-54", "55-59", "60-64", "65-69", "70-74", "75-79",
                            "80-84", "85-89", "90-94", "95+"
                        ]}
                    },
                    {
                        "code": "Kon",
                        "selection": {"filter": "item", "values": ["1", "2"]}  # Män och kvinnor
                    },
                    {
                        "code": "ContentsCode",
                        "selection": {"filter": "item", "values": ["BE0101N1"]}
                    },
                    {
                        "code": "Tid",
                        "selection": {"filter": "item", "values": ["2023"]}
                    }
                ],
                "response": {"format": "json"}
            }
            
            response = requests.post(url, json=query, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_age_distribution_response(data)
            else:
                # Fallback till grundläggande data
                print(f"Fel vid hämtning av åldersdata: {response.status_code}")
                return self._create_dummy_age_data()
                
        except Exception as e:
            print(f"Fel vid hämtning av åldersfördelning: {e}")
            return self._create_dummy_age_data()

    def _parse_age_distribution_response(self, data: dict) -> pd.DataFrame:
        """Parsar SCB-respons för åldersfördelning"""
        rows = []
        
        for item in data.get("data", []):
            region = item["key"][0]
            alder = item["key"][1]
            kon_code = item["key"][2]
            ar = item["key"][3]
            antal = int(item["values"][0]) if item["values"][0] != ".." else 0
            
            kon = "Män" if kon_code == "1" else "Kvinnor"
            
            rows.append({
                "Region": region,
                "Ålder": alder,
                "Kön": kon,
                "År": ar,
                "Antal": antal
            })
        
        return pd.DataFrame(rows)

    def _create_dummy_age_data(self) -> pd.DataFrame:
        """Skapar exempel-data för ålderspyramid när API inte fungerar"""
        age_groups = ["0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", 
                     "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", 
                     "65-69", "70-74", "75-79", "80-84", "85+"]
        
        # Realistiska siffror baserade på svensk åldersstruktur
        men_data = [2850, 2950, 3100, 2800, 2600, 3200, 3400, 3600, 3800, 3500, 
                   3200, 2900, 2600, 2400, 2100, 1800, 1200, 600]
        
        kvinnor_data = [2700, 2800, 2950, 2650, 2500, 3050, 3250, 3450, 3650, 3350,
                       3050, 2750, 2500, 2300, 2050, 1850, 1400, 950]
        
        rows = []
        for i, age_group in enumerate(age_groups):
            rows.append({"Ålder": age_group, "Kön": "Män", "Antal": men_data[i], "År": "2023"})
            rows.append({"Ålder": age_group, "Kön": "Kvinnor", "Antal": kvinnor_data[i], "År": "2023"})
        
        return pd.DataFrame(rows)
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
        
        # Skapa query för enskilda åldrar (65+)
        elderly_ages = [str(age) for age in range(65, 101)] + ["100+"]
        
        query = {
            "query": [
                {"code": "Region", "selection": {"filter": "item", "values": [region_code]}},
                {"code": "Alder", "selection": {"filter": "item", "values": elderly_ages}},
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

    def fetch_nature_reserves(self) -> pd.DataFrame:
        """Hämtar naturreservat från Naturvårdsverket"""
        try:
            # Naturvårdsverkets öppna geodata API
            base_url = "https://geodata.naturvardsverket.se/naturvardsregistret/rest/services/Naturvardsregistret_Publikt/Naturreservat/MapServer/0/query"
            
            params = {
                'where': "1=1",  # Hämta alla
                'outFields': "*",
                'f': 'json',
                'returnGeometry': 'true',
                'spatialRel': 'esriSpatialRelIntersects',
                # Begränsa till Kungsbacka kommun (ungefärligt område)
                'geometry': '{"xmin":11.8,"ymin":57.3,"xmax":12.3,"ymax":57.6,"spatialReference":{"wkid":4326}}',
                'geometryType': 'esriGeometryEnvelope',
                'inSR': '4326',
                'outSR': '4326'
            }
            
            response = requests.get(base_url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'features' in data and data['features']:
                    records = []
                    for feature in data['features']:
                        attributes = feature.get('attributes', {})
                        records.append({
                            'namn': attributes.get('NAMN', 'Okänt naturreservat'),
                            'kommun': attributes.get('KOMMUN', ''),
                            'beslutsdatum': attributes.get('BESLUTSDATUM', ''),
                            'areal_ha': attributes.get('AREAL_HA', 0),
                            'beskrivning': attributes.get('BESKRIVNING', ''),
                            'geometry': feature.get('geometry', {})
                        })
                    
                    df = pd.DataFrame(records)
                    return df[df['kommun'].str.contains('Kungsbacka', case=False, na=False)]
                
            # Fallback data om API inte fungerar
            return self._create_dummy_nature_data()
            
        except Exception as e:
            print(f"Fel vid hämtning av naturreservat: {e}")
            return self._create_dummy_nature_data()

    def _create_dummy_nature_data(self) -> pd.DataFrame:
        """Skapar exempel-data för naturreservat när API inte fungerar"""
        return pd.DataFrame([
            {
                'namn': 'Kungsbacka Kommun Naturområde 1',
                'kommun': 'Kungsbacka',
                'areal_ha': 150,
                'beskrivning': 'Blandskog med höga naturvärden',
                'lat': 57.4789,
                'lon': 12.0456
            },
            {
                'namn': 'Kungsbacka Kommun Naturområde 2', 
                'kommun': 'Kungsbacka',
                'areal_ha': 89,
                'beskrivning': 'Våtmark och ängsmark',
                'lat': 57.4167,
                'lon': 12.1234
            },
            {
                'namn': 'Kungsbacka Kommun Naturområde 3',
                'kommun': 'Kungsbacka', 
                'areal_ha': 203,
                'beskrivning': 'Gammelskog med ek och bok',
                'lat': 57.4445,
                'lon': 11.9876
            }
        ])

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

def get_all_data_sources():
    """Returnerar dictionary med alla tillgängliga datakällor"""
    return {
        "SCB": scb_data,
        "Kolada": kolada_api,
        "SMHI": smhi_api,
        "Trafikverket": trafikverket_api
    }


def normalize_infonet_tables(filepath: str) -> Dict[str, pd.DataFrame]:
    """Läser tabeller från en infonet-presentation (.pptx) och försöker mappa dem
    till meningsfulla DataFrames som dashboarden kan använda.

    Heuristisk mapping baserat på kolumnnamn.
    """
    if load_pptx_tables is None:
        raise RuntimeError("pptx-loader saknas. Installera python-pptx och säkerställ att data/infonet_loader.py finns.")

    tables, text = load_pptx_tables(filepath)
    mapped: Dict[str, pd.DataFrame] = {}
    others = []

    def make_unique_columns(df: pd.DataFrame) -> pd.DataFrame:
        cols = list(df.columns)
        seen = {}
        new_cols = []
        for c in cols:
            name = str(c)
            if name in seen:
                seen[name] += 1
                new_name = f"{name}_{seen[name]}"
            else:
                seen[name] = 0
                new_name = name
            new_cols.append(new_name)
        df = df.copy()
        df.columns = new_cols
        return df

    for df in tables:
        # Ensure unique column names to avoid pyarrow/streamlit errors on display
        try:
            df = make_unique_columns(df)
        except Exception:
            pass
        # Normalisera kolumnnamn till str
        cols = [str(c).strip() for c in df.columns]
        cols_join = " ".join(cols).lower()

        # Heuristiska regler
        if any('ort' in c for c in cols) or 'inv/ha' in cols_join:
            mapped['orter'] = pd.concat([mapped.get('orter', pd.DataFrame()), df], ignore_index=True)
        elif any('planbesked' in c.lower() or 'antal bost' in c.lower() for c in cols):
            mapped['planbesked'] = pd.concat([mapped.get('planbesked', pd.DataFrame()), df], ignore_index=True)
        elif 'referensområde' in cols_join or 'ö p-zon' in cols_join or 'storlek (ha)' in cols_join:
            mapped['referens'] = pd.concat([mapped.get('referens', pd.DataFrame()), df], ignore_index=True)
        else:
            others.append(df)

    mapped['text'] = text
    if others:
        mapped['other'] = others

    # Försök städa 'orter' tabellen
    if 'orter' in mapped and not mapped['orter'].empty:
        df = mapped['orter']
        # Ensure unique columns again after concatenation
        df = make_unique_columns(df)
        rename_map = {}
        for col in df.columns:
            low = str(col).lower()
            if 'ort' in low:
                rename_map[col] = 'ort'
            if 'inv/ha' in low or 'inv/ha' in col.lower():
                rename_map[col] = 'inv_per_ha'
            if low in ('inv', 'inv/ha', 'antal') or 'bost' in low or 'invån' in low:
                rename_map[col] = 'befolkning'
            if 'ha' in low and 'storlek' in low:
                rename_map[col] = 'ha'

        df = df.rename(columns=rename_map)

        # Konsolidera dubblett-kolumner som kan ha uppstått vid sammanslagning
        unique_cols = []
        new_df = pd.DataFrame()
        for col in df.columns:
            if col in new_df.columns:
                # Redundant, skip here (we'll handle fully below)
                continue
            # Hitta alla kolumner med detta namn (pga dubbletter efter rename)
            cols_with_name = [c for c in df.columns if c == col]
            if len(cols_with_name) == 1:
                new_df[col] = df[cols_with_name[0]]
            else:
                # Försök summera numeriska kolumner, annars ta första icke-null
                try:
                    numeric = df[cols_with_name].apply(lambda s: pd.to_numeric(s.astype(str).replace({r'[^0-9\.,-]': ''}, regex=True).str.replace(',', ''), errors='coerce'))
                    summed = numeric.sum(axis=1, skipna=True).fillna(0)
                    new_df[col] = summed.astype(int)
                except Exception:
                    new_df[col] = df[cols_with_name].bfill(axis=1).iloc[:, 0]

        df = new_df

        # Rensa numeriska kolumner robustare (undvik .str på DataFrame)
        for num_col in ['inv_per_ha', 'befolkning', 'ha']:
            if num_col in df.columns:
                try:
                    s = df[num_col].astype(str).replace({r'[^0-9\.,-]': ''}, regex=True)
                    s = s.str.replace(',', '', regex=False)
                    df[num_col] = pd.to_numeric(s, errors='coerce').fillna(0).astype(int)
                except Exception:
                    def to_int(x):
                        try:
                            txt = str(x)
                            cleaned = __import__('re').sub(r'[^0-9\.-]', '', txt).replace(',', '')
                            return int(float(cleaned)) if cleaned not in ('', None) else 0
                        except Exception:
                            return 0
                    df[num_col] = df[num_col].apply(to_int)

        mapped['orter'] = df

    return mapped


def get_infonet_data(filepath: Optional[str] = None) -> Dict[str, pd.DataFrame]:
    """Wrapper som returnerar mappade DataFrames från infonet-presentationen i repo-root.

    Om filen inte finns returneras en tom dict.
    """
    if filepath is None:
        default = Path.cwd() / "Första uppföljning av ÖP-steg 2.pptx"
        filepath = str(default)

    if not Path(filepath).exists():
        print(f"Infonet PPTX hittades inte: {filepath}")
        return {}

    try:
        return normalize_infonet_tables(filepath)
    except Exception as e:
        print(f"Fel vid normalisering av infonet-data: {e}")
        return {}
