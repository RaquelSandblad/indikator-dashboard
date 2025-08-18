# config.py - Konfiguration för alla datakällor och API-nycklar

import os
from typing import Dict, List

# SCB API-konfiguration
SCB_CONFIG = {
    "base_url": "https://api.scb.se/OV0104/v1/doris/sv/ssd",
    "user_agent": "Kungsbacka-Planeringsdashboard/1.0",
    "timeout": 60,
    "cache_hours": 24
}

# Kungsbacka kommunkod (inte Ale!)
KOMMUN_KOD = "1380"  # Kungsbacka kommun

# SCB-tabeller och endpoints
SCB_TABLES = {
    "befolkning": {
        "endpoint": "BE/BE0101/BE0101A/BefolkningNy",
        "name": "Befolkning per kommun, kön, ålder, år",
        "description": "Folkmängd efter region, kön, ålder och år"
    },
    "befolkning_forandring": {
        "endpoint": "BE/BE0101/BE0101B/BefolkningNy", 
        "name": "Befolkningsförändringar",
        "description": "In- och utvandring, födda och döda"
    },
    "hushall": {
        "endpoint": "BE/BE0101/BE0101H/HushallT01",
        "name": "Hushåll per kommun",
        "description": "Antal hushåll efter hushållsstorlek"
    },
    "byggnader": {
        "endpoint": "BO/BO0104/BO0104T01",
        "name": "Byggnader efter region och hustyp",
        "description": "Antal byggnader per typ"
    },
    "bostader": {
        "endpoint": "BO/BO0104/BO0104T02", 
        "name": "Lägenheter efter region och hustyp",
        "description": "Antal lägenheter per bostadstyp"
    },
    "arbetslöshet": {
        "endpoint": "AM/AM0210/AM0210A01",
        "name": "Relativ arbetslöshet",
        "description": "Arbetslöshetsstatistik per kommun"
    },
    "inkomst": {
        "endpoint": "HE/HE0110/HE0110A01",
        "name": "Disponibel inkomst",
        "description": "Sammanräknad förvärvsinkomst per kommun"
    },
    "utbildning": {
        "endpoint": "UF/UF0506/UF0506B01",
        "name": "Befolkning efter utbildningsnivå",
        "description": "Utbildningsnivå 25-64 år"
    }
}

# GIS-källor och WMS/WFS-tjänster
GIS_SOURCES = {
    "lantmateriet": {
        "wms_url": "https://api.lantmateriet.se/open/topoweb-ccby/v1/wmts",
        "layers": ["topoweb_ccby"],
        "description": "Lantmäteriets topografiska webbkarta"
    },
    "geodataportalen": {
        "wms_url": "https://geodata.naturvardsverket.se/geoserver/wms",
        "layers": ["naturreservat", "nationalparker"],
        "description": "Naturvårdsverkets geodata"
    },
    "trafikverket": {
        "wms_url": "https://geo.trafikverket.se/geoserver/wms",
        "layers": ["vagnett", "jarnvagsnatet"],
        "description": "Trafikverkets väg- och järnvägsnät"
    },
    "kungsbacka_kommun": {
        # Dessa URL:er behöver uppdateras med riktiga från Kungsbacka
        "wms_url": "https://kartor.kungsbacka.se/geoserver/wms",
        "wfs_url": "https://kartor.kungsbacka.se/geoserver/wfs", 
        "layers": ["detaljplaner", "oversiktsplan", "bygglov"],
        "description": "Kungsbacka kommuns kartlager"
    }
}

# Andra öppna datakällor
EXTERNAL_APIS = {
    "trafiklab": {
        "base_url": "https://api.resrobot.se/v2.1",
        "description": "Kollektivtrafikdata från Trafiklab",
        "requires_key": True
    },
    "smhi": {
        "base_url": "https://opendata-download-metfcst.smhi.se/api",
        "description": "SMHI väderdata och prognoser",
        "requires_key": False
    },
    "kolada": {
        "base_url": "http://api.kolada.se/v2",
        "description": "Kommunala nyckeltal från Kolada",
        "requires_key": False
    },
    "trafikverket": {
        "base_url": "https://api.trafikinfo.trafikverket.se/v2/data.json",
        "description": "Trafikdata från Trafikverket",
        "requires_key": True,
        "api_key": ""  # Lägg till din API-nyckel här
    }
}

# Standardqueries för SCB
def get_standard_query(table_type: str, region_code: str = KOMMUN_KOD, years: List[str] = None) -> Dict:
    """Genererar standardqueries för olika SCB-tabeller"""
    
    if years is None:
        years = ["2023", "2022", "2021"]
    
    base_queries = {
        "befolkning": {
            "query": [
                {"code": "Region", "selection": {"filter": "item", "values": [region_code]}},
                {"code": "Kon", "selection": {"filter": "item", "values": ["1", "2"]}},  # Män och kvinnor separat
                {"code": "Alder", "selection": {"filter": "item", "values": ["tot"]}},  # Total ålder
                {"code": "Tid", "selection": {"filter": "item", "values": years}}
            ],
            "response": {"format": "json"}
        },
        "befolkning_alder": {
            "query": [
                {"code": "Region", "selection": {"filter": "item", "values": [region_code]}},
                {"code": "Kon", "selection": {"filter": "item", "values": ["1", "2"]}},  # Män och kvinnor separat
                {"code": "Alder", "selection": {"filter": "item", "values": ["0-19", "20-64", "65+"]}},  # Åldersgrupper
                {"code": "Tid", "selection": {"filter": "item", "values": years}}
            ],
            "response": {"format": "json"}
        },
        "hushall": {
            "query": [
                {"code": "Region", "selection": {"filter": "item", "values": [region_code]}},
                {"code": "HushallStorlek", "selection": {"filter": "all", "values": ["*"]}},
                {"code": "Tid", "selection": {"filter": "item", "values": years}}
            ],
            "response": {"format": "json"}
        }
    }
    
    return base_queries.get(table_type, {})

# Orter i Kungsbacka med koordinater
ORTER = {
    "Kungsbacka stad": {"lat": 57.4878, "lon": 12.0765, "befolkning": 23500},
    "Onsala": {"lat": 57.4056, "lon": 12.0119, "befolkning": 11900},
    "Särö": {"lat": 57.4167, "lon": 11.9333, "befolkning": 5200},
    "Vallda": {"lat": 57.5167, "lon": 12.0667, "befolkning": 4600},
    "Kullavik": {"lat": 57.3833, "lon": 11.9167, "befolkning": 4100},
    "Fjärås": {"lat": 57.4500, "lon": 12.1667, "befolkning": 3800},
    "Anneberg": {"lat": 57.5000, "lon": 12.1167, "befolkning": 3800},
    "Åsa": {"lat": 57.3500, "lon": 12.1167, "befolkning": 3400},
    "Frillesås": {"lat": 57.4167, "lon": 12.2000, "befolkning": 2500}
}

# Färgtema för visualiseringar
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e", 
    "success": "#2ca02c",
    "warning": "#ff9999",
    "danger": "#d62728",
    "op_green": "#6ab7a8",
    "op_red": "#ff6f69",
    "theme_yellow": "#f3d55b",
    "theme_blue": "#4ba3a4"
}
