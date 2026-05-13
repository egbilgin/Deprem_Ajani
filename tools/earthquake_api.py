import logging
import requests
from datetime import datetime, timedelta
from functools import lru_cache

# --- Loglama Ayarları ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# --- LRU Cache Dekoratörü (api ye gereksiz yüklenmeyi önler) ---
@lru_cache(maxsize=32)
def get_earthquake_data(latitude: float, longitude: float, radius_km: int = 100, min_magnitude: float = 4.0) -> list:
    """
    USGS API'sini kullanarak belirli bir konuma ait geçmiş deprem verilerini çeker.
    """
    end_time = datetime.now()
    start_time = end_time - timedelta(days=365 * 10)

    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    
    params = {
        "format": "geojson",
        "starttime": start_time.strftime("%Y-%m-%d"),
        "endtime": end_time.strftime("%Y-%m-%d"),
        "latitude": latitude,
        "longitude": longitude,
        "maxradiuskm": radius_km,
        "minmagnitude": min_magnitude
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status() 
        data = response.json()

        earthquakes = []
        if "features" in data:
            for feature in data["features"]:
                props = feature["properties"]
                earthquakes.append({
                    "place": props["place"],
                    "magnitude": props["mag"],
                    "date": datetime.fromtimestamp(props["time"]/1000).strftime('%Y-%m-%d')
                })
        
        # işlem başarılı olduğunda arka planda bilgi logu düş
        logger.info(f"{latitude}, {longitude} konumu için {len(earthquakes)} adet deprem verisi çekildi.")
        return earthquakes

    except Exception as e:
        # print yerine kurumsal loglama ->> hata olursa
        logger.error(f"Veri çekilirken API Hatası oluştu: {e}")
        return []

# --- Test Bloğu ---
if __name__ == "__main__":
    test_lat = 40.77
    test_lon = 30.36
    
    print("API'ye istek atılıyor...")
    sonuclar = get_earthquake_data(test_lat, test_lon)
    
    print(f"\nİlk 3 sonuç:")
    for d in sonuclar[:3]:
        print(f"-> Tarih: {d['date']} | Büyüklük: {d['magnitude']} | Konum: {d['place']}")