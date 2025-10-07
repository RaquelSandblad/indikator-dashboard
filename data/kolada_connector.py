"""
Kolada API Connector - Hämtar kommunala nyckeltal från Kolada
API Dokumentation: https://www.kolada.se/appspecific/rkalagret/api.html
"""

import requests
import pandas as pd
import streamlit as st
from typing import List, Dict, Optional
import json
import os
from datetime import datetime, timedelta

class KoladaConnector:
    """
    Klass för att hämta data från Kolada API
    Kolada är Sveriges största databas för kommunal nyckeltal och kvalitetsinformation
    """
    
    BASE_URL = "http://api.kolada.se/v2"
    CACHE_DIR = "cache"
    CACHE_DURATION_DAYS = 7  # Cache i 7 dagar
    
    # Kungsbacka kommun kod
    KUNGSBACKA_KOD = "1384"
    
    # Hallands kommuner
    HALLAND_KOMMUNER = {
        "1315": "Hylte",
        "1380": "Halmstad",
        "1381": "Laholm",
        "1382": "Falkenberg",
        "1383": "Varberg",
        "1384": "Kungsbacka"
    }
    
    # Göteborgsregionens kommuner (GR) - 13 kommuner i kommunalförbundet
    GOTEBORGSREGIONEN_KOMMUNER = {
        "1440": "Ale",
        "1489": "Alingsås",
        "1480": "Göteborg",
        "1401": "Härryda",
        "1384": "Kungsbacka",
        "1482": "Kungälv",
        "1441": "Lerum",
        "1462": "Lilla Edet",
        "1481": "Mölndal",
        "1402": "Partille",
        "1415": "Stenungsund",
        "1419": "Tjörn",
        "1407": "Öckerö"
    }
    
    # Standardjämförelse (närliggande kommuner)
    JAMFORELSE_KOMMUNER = {
        "1384": "Kungsbacka",
        "1480": "Göteborg",
        "1481": "Mölndal",
        "1482": "Kungälv",
        "1383": "Varberg",
        "1382": "Falkenberg",
        "1440": "Ale",
        "1401": "Härryda",
        "1402": "Partille"
    }
    
    # Viktiga KPI:er för planering
    VIKTIGA_KPIER = {
        # Befolkning och demografi
        "N01951": "Folkmängd 31 december",
        "N01952": "Folkmängd 1 november",
        "N01953": "Befolkningsprognos, antal invånare",
        
        # Bostäder och byggande
        "N00913": "Nybyggda lägenheter",
        "N00914": "Påbörjade lägenheter",
        "N07932": "Bostadslägenheter, antal",
        "N00945": "Bygglov för nybyggnad av bostäder",
        
        # Ekonomi
        "N00001": "Verksamhetens nettokostnader, tkr/inv",
        "N00002": "Skatteintäkter, tkr/inv",
        "N07909": "Skattesats, total",
        
        # Planering och markanvändning
        "N07925": "Detaljplaner, antal antagna",
        "N07924": "Detaljplaner, antal pågående",
        
        # Miljö och hållbarhet
        "N00974": "Andel som reser hållbart till arbetsplatsen, %",
        "N00956": "Gång- och cykelavstånd till närmaste hållplats, %",
    }
    
    # ARBETSMARKNAD KPI:er
    ARBETSMARKNAD_KPIER = {
        "N01720": "Arbetslösa eller i åtgärd minst en dag under året, 16-64 år, andel (%)",
        "N00967": "Sjukpenningtalet, 15–69 år, dagar/arbetskraften",
        "N02201": "Sysselsatta efter arbetsställets belägenhet, antal",
        "N02203": "Sysselsatta i kommun-/regionsektor, andel (%)",
        "N02205": "Sysselsatta i näringslivet, andel (%)",
        "N01004": "Nystartade arbetsställen, antal/1000 inv 16-64 år",
        "N01752": "Förvärvsarbetande dag 31 dec, 20-64 år, andel (%)",
        "N11800": "Förvärvsarbetande, andel (%) av befolkningen 20-64 år",
        "N00708": "Arbetslöshet någon gång under året, bland inrikes födda 20-64 år, andel (%)",
    }
    
    # UTBILDNING KPI:er
    UTBILDNING_KPIER = {
        "N15413": "Elever i åk 9, genomsnittligt meritvärde",
        "N15446": "Elever i åk 9 som är behöriga till yrkesprogram, andel (%)",
        "N15447": "Elever i åk 9 som är behöriga till estetiska pgm, andel (%)",
        "N18216": "Elever i åk 6, andel (%) med lägst betyget E i matematik",
        "N18605": "Elever i åk 6, andel (%) med lägst betyget E i svenska",
        "N18224": "Elever i åk 3, andel (%) med lägst betyget E i matematik",
        "N15533": "Gymnasieelever som slutfört med examen inom 3 år, andel (%)",
        "N15427": "Gymnasieelever som slutfört med examen inom 4 år, andel (%)",
        "N01953": "Elever i kommunal grundskola åk 1-9, antal",
        "N00531": "Medborgarundersökningen - Grundskolan fungerar bra, andel (%)",
        "N00532": "Medborgarundersökningen - Gymnasieskolan fungerar bra, andel (%)",
    }
    
    # BARNOMSORG & FÖRSKOLA KPI:er
    BARNOMSORG_KPIER = {
        "N15011": "Barn 1-5 år i förskola, andel (%) av alla barn",
        "N15361": "Invånare 0 år, antal",
        "N15362": "Barn 1-5 år inskrivna i förskola, antal",
        "N00530": "Medborgarundersökningen - Förskolan fungerar bra, andel (%)",
        "N11750": "Kvinnors förvärvsfrekvens, andel (%) 20-64 år",
        "N03201": "Kostnad förskola, kr/inv 1-5 år",
    }
    
    # ÄLDREOMSORG KPI:er
    ALDREOMSORG_KPIER = {
        "N00204": "Invånare 65+, antal",
        "N00205": "Invånare 80+, antal",
        "N00911": "Äldre 65+ i ordinärt boende med hemtjänst, andel (%)",
        "N00910": "Äldre 65+ i särskilt boende, andel (%)",
        "N00909": "Äldre 80+ i ordinärt boende med hemtjänst, andel (%)",
        "N00908": "Äldre 80+ i särskilt boende, andel (%)",
        "N00974": "Brukarundersökning äldreomsorg, helhetssyn, andel (%)",
        "N03301": "Kostnad äldreomsorg, kr/inv 65+",
    }
    
    # MILJÖ & HÅLLBARHET KPI:er
    MILJO_KPIER = {
        "N00302": "Miljökvalitet - Kommunindex",
        "N00371": "Miljömässig hållbarhet - Kommunindex",
        "N00974": "Andel som reser hållbart till arbetsplatsen, %",
        "N00956": "Gång- och cykelavstånd till närmaste hållplats, %",
        "N00636": "Kommunens arbete för att minska miljö- och klimatpåverkan, andel (%)",
        "N00304": "Utsläpp växthusgaser totalt, ton koldioxidekvivalenter/inv",
        "N00305": "Utsläpp växthusgaser från transporter, ton koldioxidekvivalenter/inv",
        "N07951": "Andel förnybara bränslen i kommunorganisationen, %",
        "N00546": "Medborgarundersökningen - Viktigt i boendemiljön - närhet till natur, andel (%)",
        "N17425": "Andel hushållsavfall som återvinns, %",
    }
    
    # KULTUR & FRITID KPI:er
    KULTUR_FRITID_KPIER = {
        "N00593": "Det lokala kultur- och nöjeslivet är bra, andel (%)",
        "N00594": "Kommunens arbete för att främja kulturlivet, andel (%)",
        "N09001": "Kostnad musik och kulturskola, kr/inv 7-15 år",
        "N09007": "Kostnad allmän kulturverksamhet, kr/inv",
        "N11801": "Biblioteksbesök, antal/inv",
        "N11929": "Bibliotekslån, antal/inv",
        "N00107": "Månadsavlönade inom kultur-, turism- och fritidsarbete, antal",
        "N00595": "Kommunens utbud av fritidsaktiviteter för barn och unga, andel (%)",
        "N00596": "Kommunens idrotts- och motionsanläggningar, andel (%)",
    }
    
    # KOLLEKTIVTRAFIK & INFRASTRUKTUR KPI:er
    INFRASTRUKTUR_KPIER = {
        "N00550": "Viktigt i boendemiljön - förbindelser med kollektivtrafik, andel (%)",
        "N00956": "Gång- och cykelavstånd till närmaste hållplats, %",
        "N00974": "Andel som reser hållbart till arbetsplatsen, %",
        "N00551": "Viktigt i boendemiljön - finns parkeringsmöjligheter, andel (%)",
        "N00552": "Viktigt i boendemiljön - begränsad biltrafik, andel (%)",
        "N07456": "Gång- och cykelvägar, meter/inv",
    }
    
    # SOCIAL VÄLFÄRD & TRYGGHET KPI:er
    SOCIAL_KPIER = {
        "N00944": "Polisanmälda brott, antal/1000 inv",
        "N00945": "Våldtäkter, antal/100000 inv",
        "N02404": "Personrån, antal/100000 inv",
        "N02405": "Bostadsinbrott, antal/1000 inv",
        "N02920": "Anmälda brott, stöld, antal/1000 inv",
        "N00635": "Medborgarundersökningen - Tryggheten i kommunen, andel (%)",
        "N00638": "Medborgarundersökningen - Förtroende för kommunstyrelsen, andel (%)",
    }
    
    def __init__(self):
        """Initierar Kolada-kopplingen"""
        # Skapa cache-katalog om den inte finns
        if not os.path.exists(self.CACHE_DIR):
            os.makedirs(self.CACHE_DIR)
    
    def get_kommun_namn(self, kommun_kod: str) -> str:
        """
        Hämtar kommunnamn från kommunkod
        Söker i alla tillgängliga listor
        """
        # Sök i alla listor
        for kommun_dict in [self.HALLAND_KOMMUNER, self.GOTEBORGSREGIONEN_KOMMUNER, self.JAMFORELSE_KOMMUNER]:
            if kommun_kod in kommun_dict:
                return kommun_dict[kommun_kod]
        
        # Om inte hittad, returnera "Kommun {kod}"
        return f"Kommun {kommun_kod}"
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Genererar filsökväg för cache"""
        return os.path.join(self.CACHE_DIR, f"kolada_{cache_key}.json")
    
    def _is_cache_valid(self, cache_path: str) -> bool:
        """Kontrollerar om cache är giltig (inte för gammal)"""
        if not os.path.exists(cache_path):
            return False
        
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        age = datetime.now() - file_time
        return age < timedelta(days=self.CACHE_DURATION_DAYS)
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Laddar data från cache om den finns och är giltig"""
        cache_path = self._get_cache_path(cache_key)
        
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Cache-läsfel: {e}")
                return None
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Sparar data till cache"""
        cache_path = self._get_cache_path(cache_key)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Cache-skrivfel: {e}")
    
    def get_kpi_metadata(self, kpi_id: str) -> Optional[Dict]:
        """
        Hämtar metadata för en KPI
        
        Args:
            kpi_id: KPI-ID (t.ex. "N01951")
        
        Returns:
            Dict med KPI-information
        """
        cache_key = f"kpi_meta_{kpi_id}"
        cached = self._load_from_cache(cache_key)
        if cached:
            return cached
        
        try:
            response = requests.get(f"{self.BASE_URL}/kpi/{kpi_id}")
            response.raise_for_status()
            data = response.json()
            
            if data.get('values'):
                kpi_info = data['values'][0]
                self._save_to_cache(cache_key, kpi_info)
                return kpi_info
        except Exception as e:
            st.error(f"Kunde inte hämta KPI-metadata: {e}")
        return None
    
    def get_kpi_data(self, kpi_id: str, kommun_kod: str = None) -> pd.DataFrame:
        """
        Hämtar KPI-data för en eller flera kommuner
        
        Args:
            kpi_id: KPI-ID (t.ex. "N01951")
            kommun_kod: Kommunkod (default: Kungsbacka)
        
        Returns:
            DataFrame med KPI-data
        """
        if kommun_kod is None:
            kommun_kod = self.KUNGSBACKA_KOD
        
        cache_key = f"kpi_data_{kpi_id}_{kommun_kod}"
        cached = self._load_from_cache(cache_key)
        if cached:
            return pd.DataFrame(cached)
        
        try:
            url = f"{self.BASE_URL}/data/kpi/{kpi_id}/municipality/{kommun_kod}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get('values'):
                # Skapa DataFrame
                rows = []
                for item in data['values']:
                    # Period är på denna nivå, inte i values
                    period = item['period']
                    
                    # Hitta värdet för totalt (gender = "T")
                    for value_data in item['values']:
                        if value_data.get('gender') == 'T':  # T = Total
                            rows.append({
                                'kpi': item['kpi'],
                                'kommun': item['municipality'],
                                'år': period,
                                'värde': value_data['value']
                            })
                            break  # Vi vill bara totalen
                
                df = pd.DataFrame(rows)
                
                # Spara till cache
                self._save_to_cache(cache_key, df.to_dict('records'))
                return df
        except Exception as e:
            st.error(f"Kunde inte hämta KPI-data: {e}")
        
        return pd.DataFrame()
    
    def get_multiple_kpis(self, kpi_ids: List[str], kommun_kod: str = None) -> Dict[str, pd.DataFrame]:
        """
        Hämtar flera KPI:er samtidigt
        
        Args:
            kpi_ids: Lista med KPI-ID:n
            kommun_kod: Kommunkod (default: Kungsbacka)
        
        Returns:
            Dict med KPI-ID som nyckel och DataFrame som värde
        """
        result = {}
        for kpi_id in kpi_ids:
            df = self.get_kpi_data(kpi_id, kommun_kod)
            if not df.empty:
                result[kpi_id] = df
        return result
    
    def compare_municipalities(self, kpi_id: str, kommun_koder: List[str] = None, year: str = None) -> pd.DataFrame:
        """
        Jämför en KPI mellan flera kommuner
        
        Args:
            kpi_id: KPI-ID
            kommun_koder: Lista med kommunkoder (default: jämförelsekommuner)
            year: Årtal (default: senaste tillgängliga)
        
        Returns:
            DataFrame med jämförelsedata
        """
        if kommun_koder is None:
            kommun_koder = list(self.JAMFORELSE_KOMMUNER.keys())
        
        all_data = []
        
        for kod in kommun_koder:
            df = self.get_kpi_data(kpi_id, kod)
            if not df.empty:
                # Lägg till kommunnamn (använd ny funktion som söker i alla listor)
                df['kommun_namn'] = self.get_kommun_namn(kod)
                all_data.append(df)
        
        if not all_data:
            return pd.DataFrame()
        
        combined = pd.concat(all_data, ignore_index=True)
        
        # Filtrera på år om specificerat
        if year:
            combined = combined[combined['år'] == year]
        else:
            # Ta senaste året för varje kommun
            latest_year = combined['år'].max()
            combined = combined[combined['år'] == latest_year]
        
        return combined
    
    def get_latest_value(self, kpi_id: str, kommun_kod: str = None) -> Optional[Dict]:
        """
        Hämtar senaste värdet för en KPI
        
        Args:
            kpi_id: KPI-ID
            kommun_kod: Kommunkod (default: Kungsbacka)
        
        Returns:
            Dict med senaste värdet och årtal
        """
        df = self.get_kpi_data(kpi_id, kommun_kod)
        if df.empty:
            return None
        
        latest = df.nlargest(1, 'år').iloc[0]
        return {
            'värde': latest['värde'],
            'år': latest['år'],
            'kpi': latest['kpi']
        }
    
    def get_trend_data(self, kpi_id: str, kommun_kod: str = None, years: int = 10) -> pd.DataFrame:
        """
        Hämtar trenddata för de senaste X åren
        
        Args:
            kpi_id: KPI-ID
            kommun_kod: Kommunkod (default: Kungsbacka)
            years: Antal år bakåt
        
        Returns:
            DataFrame med trenddata
        """
        df = self.get_kpi_data(kpi_id, kommun_kod)
        if df.empty:
            return pd.DataFrame()
        
        # Sortera och ta senaste X åren
        df = df.sort_values('år', ascending=False).head(years)
        return df.sort_values('år')  # Sortera stigande för graf
    
    @st.cache_data(ttl=3600*24*7)  # Cache i 7 dagar
    def get_all_municipalities(_self) -> pd.DataFrame:
        """
        Hämtar lista över alla kommuner
        
        Returns:
            DataFrame med alla kommuner
        """
        try:
            response = requests.get(f"{_self.BASE_URL}/municipality")
            response.raise_for_status()
            data = response.json()
            
            if data.get('values'):
                return pd.DataFrame(data['values'])
        except Exception as e:
            st.error(f"Kunde inte hämta kommunlista: {e}")
        
        return pd.DataFrame()
    
    # === ARBETSMARKNAD FUNKTIONER ===
    
    def get_arbetsmarknad_data(self, kommun_kod: str = None) -> Dict[str, pd.DataFrame]:
        """
        Hämtar all arbetsmarknadsdata för en kommun
        
        Returns:
            Dict med KPI-ID som nyckel och DataFrame som värde
        """
        return self.get_multiple_kpis(list(self.ARBETSMARKNAD_KPIER.keys()), kommun_kod)
    
    def get_arbetslöshet(self, kommun_kod: str = None, years: int = 10) -> pd.DataFrame:
        """Hämtar arbetslöshetsdata"""
        return self.get_trend_data("N01720", kommun_kod, years)
    
    def get_sysselsattning(self, kommun_kod: str = None, years: int = 10) -> pd.DataFrame:
        """Hämtar sysselsättningsdata"""
        return self.get_trend_data("N11800", kommun_kod, years)
    
    # === UTBILDNING FUNKTIONER ===
    
    def get_utbildning_data(self, kommun_kod: str = None) -> Dict[str, pd.DataFrame]:
        """
        Hämtar all utbildningsdata för en kommun
        
        Returns:
            Dict med KPI-ID som nyckel och DataFrame som värde
        """
        return self.get_multiple_kpis(list(self.UTBILDNING_KPIER.keys()), kommun_kod)
    
    def get_skolresultat_ak9(self, kommun_kod: str = None, years: int = 10) -> pd.DataFrame:
        """Hämtar genomsnittligt meritvärde åk 9"""
        return self.get_trend_data("N15413", kommun_kod, years)
    
    def get_gymnasie_examen(self, kommun_kod: str = None, years: int = 10) -> pd.DataFrame:
        """Hämtar andel med gymnasieexamen inom 3 år"""
        return self.get_trend_data("N15533", kommun_kod, years)
    
    # === BARNOMSORG FUNKTIONER ===
    
    def get_barnomsorg_data(self, kommun_kod: str = None) -> Dict[str, pd.DataFrame]:
        """
        Hämtar all barnomsorg/förskoledata
        
        Returns:
            Dict med KPI-ID som nyckel och DataFrame som värde
        """
        return self.get_multiple_kpis(list(self.BARNOMSORG_KPIER.keys()), kommun_kod)
    
    def get_forskola_andel(self, kommun_kod: str = None, years: int = 10) -> pd.DataFrame:
        """Hämtar andel barn i förskola"""
        return self.get_trend_data("N15011", kommun_kod, years)
    
    # === ÄLDREOMSORG FUNKTIONER ===
    
    def get_aldreomsorg_data(self, kommun_kod: str = None) -> Dict[str, pd.DataFrame]:
        """
        Hämtar all äldreomsorgsdata
        
        Returns:
            Dict med KPI-ID som nyckel och DataFrame som värde
        """
        return self.get_multiple_kpis(list(self.ALDREOMSORG_KPIER.keys()), kommun_kod)
    
    def get_aldreomsorg_hemtjanst(self, kommun_kod: str = None, years: int = 10) -> pd.DataFrame:
        """Hämtar andel 65+ med hemtjänst"""
        return self.get_trend_data("N00911", kommun_kod, years)
    
    def get_aldreomsorg_sarskilt(self, kommun_kod: str = None, years: int = 10) -> pd.DataFrame:
        """Hämtar andel 65+ i särskilt boende"""
        return self.get_trend_data("N00910", kommun_kod, years)
    
    # === MILJÖ & HÅLLBARHET FUNKTIONER ===
    
    def get_miljo_data(self, kommun_kod: str = None) -> Dict[str, pd.DataFrame]:
        """
        Hämtar all miljö- och hållbarhetsdata
        
        Returns:
            Dict med KPI-ID som nyckel och DataFrame som värde
        """
        return self.get_multiple_kpis(list(self.MILJO_KPIER.keys()), kommun_kod)
    
    def get_hallbart_resande(self, kommun_kod: str = None, years: int = 10) -> pd.DataFrame:
        """Hämtar andel som reser hållbart till arbetsplatsen"""
        return self.get_trend_data("N00974", kommun_kod, years)
    
    def get_vaxthusgas(self, kommun_kod: str = None, years: int = 10) -> pd.DataFrame:
        """Hämtar utsläpp växthusgaser totalt"""
        return self.get_trend_data("N00304", kommun_kod, years)
    
    def get_atervinning(self, kommun_kod: str = None, years: int = 10) -> pd.DataFrame:
        """Hämtar andel hushållsavfall som återvinns"""
        return self.get_trend_data("N17425", kommun_kod, years)
    
    # === KULTUR & FRITID FUNKTIONER ===
    
    def get_kultur_fritid_data(self, kommun_kod: str = None) -> Dict[str, pd.DataFrame]:
        """
        Hämtar all kultur- och fritidsdata
        
        Returns:
            Dict med KPI-ID som nyckel och DataFrame som värde
        """
        return self.get_multiple_kpis(list(self.KULTUR_FRITID_KPIER.keys()), kommun_kod)
    
    def get_biblioteksbesok(self, kommun_kod: str = None, years: int = 10) -> pd.DataFrame:
        """Hämtar biblioteksbesök per invånare"""
        return self.get_trend_data("N11801", kommun_kod, years)
    
    def get_bibliotekslan(self, kommun_kod: str = None, years: int = 10) -> pd.DataFrame:
        """Hämtar bibliotekslån per invånare"""
        return self.get_trend_data("N11929", kommun_kod, years)
    
    # === INFRASTRUKTUR FUNKTIONER ===
    
    def get_infrastruktur_data(self, kommun_kod: str = None) -> Dict[str, pd.DataFrame]:
        """
        Hämtar all infrastrukturdata
        
        Returns:
            Dict med KPI-ID som nyckel och DataFrame som värde
        """
        return self.get_multiple_kpis(list(self.INFRASTRUKTUR_KPIER.keys()), kommun_kod)
    
    # === SOCIAL VÄLFÄRD & TRYGGHET FUNKTIONER ===
    
    def get_social_data(self, kommun_kod: str = None) -> Dict[str, pd.DataFrame]:
        """
        Hämtar all social välfärd och trygghetsdata
        
        Returns:
            Dict med KPI-ID som nyckel och DataFrame som värde
        """
        return self.get_multiple_kpis(list(self.SOCIAL_KPIER.keys()), kommun_kod)
    
    def get_brott_total(self, kommun_kod: str = None, years: int = 10) -> pd.DataFrame:
        """Hämtar polisanmälda brott per 1000 inv"""
        return self.get_trend_data("N00944", kommun_kod, years)
    
    def get_trygghet(self, kommun_kod: str = None, years: int = 10) -> pd.DataFrame:
        """Hämtar medborgarnas upplevda trygghet"""
        return self.get_trend_data("N00635", kommun_kod, years)
    
    # === SMART SÖKNING ===
    
    def search_kpi_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """
        Söker efter KPI:er baserat på nyckelord
        
        Args:
            keywords: Lista med sökord (t.ex. ["skola", "betyg"])
        
        Returns:
            Lista med matchande KPI:er med ID, titel och beskrivning
        """
        all_kpis = {}
        
        # Samla alla KPI:er från alla kategorier
        for category_dict in [
            self.VIKTIGA_KPIER,
            self.ARBETSMARKNAD_KPIER,
            self.UTBILDNING_KPIER,
            self.BARNOMSORG_KPIER,
            self.ALDREOMSORG_KPIER,
            self.MILJO_KPIER,
            self.KULTUR_FRITID_KPIER,
            self.INFRASTRUKTUR_KPIER,
            self.SOCIAL_KPIER
        ]:
            all_kpis.update(category_dict)
        
        # Sök efter matchningar
        matches = []
        keywords_lower = [k.lower() for k in keywords]
        
        for kpi_id, kpi_title in all_kpis.items():
            kpi_title_lower = kpi_title.lower()
            
            # Om något nyckelord finns i titeln
            for keyword in keywords_lower:
                if keyword in kpi_title_lower:
                    matches.append({
                        'id': kpi_id,
                        'title': kpi_title,
                        'keyword_match': keyword
                    })
                    break
        
        return matches
    
    def get_relevant_kpis_for_question(self, question: str) -> List[Dict]:
        """
        Intelligent funktion som hittar relevanta KPI:er baserat på en fråga
        
        Args:
            question: Användarens fråga (t.ex. "Hur går det för skolorna?")
        
        Returns:
            Lista med relevanta KPI:er och deras senaste värde
        """
        question_lower = question.lower()
        
        # Nyckelordsmatching för olika områden
        keyword_map = {
            'skola|utbildning|betyg|elev|grundskola|gymnasium': list(self.UTBILDNING_KPIER.keys()),
            'arbete|arbetslöshet|sysselsättning|jobb|arbetsmarknad': list(self.ARBETSMARKNAD_KPIER.keys()),
            'barn|förskola|barnomsorg': list(self.BARNOMSORG_KPIER.keys()),
            'äldre|äldreomsorg|pensionär|senior|65\\+|80\\+': list(self.ALDREOMSORG_KPIER.keys()),
            'miljö|hållbarhet|klimat|utsläpp|återvinning': list(self.MILJO_KPIER.keys()),
            'kultur|fritid|bibliotek|idrott': list(self.KULTUR_FRITID_KPIER.keys()),
            'trafik|kollektiv|cykel|väg|infrastruktur': list(self.INFRASTRUKTUR_KPIER.keys()),
            'trygghet|brott|säkerhet': list(self.SOCIAL_KPIER.keys()),
            'bostad|lägenhet|byggande': ['N00913', 'N00914', 'N07932'],
        }
        
        import re
        relevant_kpis = []
        
        # Hitta matchande KPI:er
        for pattern, kpi_ids in keyword_map.items():
            if re.search(pattern, question_lower):
                for kpi_id in kpi_ids[:5]:  # Max 5 per kategori
                    try:
                        value = self.get_latest_value(kpi_id)
                        if value:
                            relevant_kpis.append(value)
                    except:
                        pass
        
        return relevant_kpis


# Globalt tillgänglig instans
kolada = KoladaConnector()
