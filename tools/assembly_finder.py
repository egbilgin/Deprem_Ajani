import math
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# pilot bölgeler için örnek toplanma alanları (Serdivan ve Nilüfer)
ASSEMBLY_POINTS = [
    {"name": "Serdivan Gölpark Toplanma Alanı", "lat": 40.735, "lon": 30.340},
    {"name": "Serdivan AVM Yanı Açık Alan", "lat": 40.758, "lon": 30.364},
    {"name": "Nilüfer FSM Bulvarı Deprem Parkı", "lat": 40.218, "lon": 28.950},
    {"name": "Bursa Kültürpark Toplanma Alanı", "lat": 40.193, "lon": 29.043}
]

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Haversine formülü ile küresel yüzeydeki iki nokta arasındaki 
    kuş uçuşu mesafeyi kilometre cinsinden hesaplar.
    """
    R = 6371.0 # Dünya'nın ortalama yarıçapı (km)
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2)**2 + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def get_nearest_assembly_point(user_lat: float, user_lon: float) -> dict:
    """
    Kullanıcının koordinatlarına en yakın toplanma alanını listeden bularak döndürür.
    Ajanın acil eylem planı oluştururken kullanacağı kritik bir araçtır.
    """
    try:
        nearest_point = None
        min_dist = float('inf')
        
        for point in ASSEMBLY_POINTS:
            dist = calculate_distance(user_lat, user_lon, point["lat"], point["lon"])
            if dist < min_dist:
                min_dist = dist
                nearest_point = point.copy()
                nearest_point["distance_km"] = round(dist, 2)
                
        logger.info(f"{user_lat}, {user_lon} konumu için en yakın alan: {nearest_point['name']} ({nearest_point['distance_km']} km)")
        return nearest_point
        
    except Exception as e:
        logger.error(f"Toplanma alanı hesaplanırken hata oluştu: {e}")
        return {"error": "En yakın toplanma alanı hesaplanamadı."}

# Test Bloğu
if __name__ == "__main__":
    # Test: Saü kampüs civarı koordinat
    test_lat = 40.740
    test_lon = 30.330
    
    print("Konum analiz ediliyor...")
    en_yakin = get_nearest_assembly_point(test_lat, test_lon)
    
    if "error" not in en_yakin:
        print(f"\nEn Yakın Toplanma Alanı: {en_yakin['name']}")
        print(f"Mesafe: {en_yakin['distance_km']} km")
        print(f"Koordinatlar: {en_yakin['lat']}, {en_yakin['lon']}")