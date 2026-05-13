"""
agent_core.py
=============

"""

from tools.earthquake_api import get_earthquake_data
from tools.assembly_finder import get_nearest_assembly_point
from geopy.geocoders import Nominatim

class EarthquakeAgent:
    def __init__(self):
        self.memory = []

    def analyze(self, user_data: dict) -> dict:
        self.memory.append({"rol": "kullanici", "veri": user_data})
        result = self._real_analyze(user_data)
        self.memory.append({"rol": "ajan", "sonuc": result})
        return result

    def _real_analyze(self, d: dict) -> dict:
        # 1. ARAYÜZDEN GELEN TÜM VERİLER (Esma'nın Değişkenleri)
        bina_yasi = d.get("bina_yasi", 1990)
        kat       = d.get("kat_sayisi", 5)
        fay_km    = d.get("yakin_fay_km", 15.0)
        zemin     = d.get("zemin_turu", "Bilinmiyor")
        bina_turu = d.get("bina_turu", "Betonarme (Perde Duvarsız)")
        hane      = d.get("hane_sayisi", 4)
        ozel      = d.get("ozel_ihtiyac", [])
        adres     = d.get("adres", "Sakarya")

        # 2. GEOCODING VE GERÇEK API VERİSİ 
        # 2. DİNAMİK GEOCODING (Ev Adresi Hassasiyetinde)
        try:
            geolocator = Nominatim(user_agent="deprem_ajani_melisa")
            # timeout=10 ekledik; detaylı adreslerde sunucu yanıtı için daha fazla süre tanıyoruz.
            location = geolocator.geocode(adres, timeout=10) 
            
            if location:
                lat, lon = location.latitude, location.longitude
                print(f"DEBUG: Konum Bulundu -> {lat}, {lon}") # Terminalden kontrol etmek için
            else:
                # Tam adresi bulamazsa hata vermemesi için varsayılan Sakarya kalabilir
                lat, lon = 40.74, 30.33 
        except Exception as e:
            print(f"DEBUG: Geocoding Hatası -> {e}")
            lat, lon = 40.74, 30.33

        gecmis_depremler = get_earthquake_data(lat, lon)
        toplanma_verisi = get_nearest_assembly_point(lat, lon)
        alan_adi = toplanma_verisi.get('name', 'Bölgedeki Açık Alan')

        # 3. DETAYLI SKOR HESABI (Esma'nın Algoritması + API Verisi)
        skor = 0
        if bina_yasi < 1975:   skor += 35
        elif bina_yasi < 1999: skor += 25
        elif bina_yasi < 2007: skor += 12
        else:                  skor += 5

        skor += min(kat * 2, 20)

        if fay_km < 5:    skor += 25
        elif fay_km < 15: skor += 15
        elif fay_km < 30: skor += 8
        else:             skor += 2

        skor += {"Dolgu Zemin": 15, "Alüvyon (Dere Yatağı)": 12,
                 "Kum / Çakıl": 8, "Bilinmiyor": 5, "Sağlam Kaya": 0}.get(zemin, 5)

        skor += {"Yığma Tuğla": 10, "Betonarme (Perde Duvarsız)": 6,
                 "Ahşap / Diğer": 8, "Prefabrik": 4,
                 "Betonarme (Perde Duvarlı)": 0}.get(bina_turu, 5)

        # API'den gelen veriye göre ek risk
        if len(gecmis_depremler) > 10: skor += 10 

        skor = max(0, min(100, skor))

        if skor >= 80:   etiket = "KRİTİK"
        elif skor >= 60: etiket = "YÜKSEK"
        elif skor >= 40: etiket = "ORTA"
        else:            etiket = "DÜŞÜK"

        # 4. BİNA DEĞERLENDİRMESİ 
        if bina_yasi < 1975:   yon = "1975 öncesi yönetmelik dışı yapı"
        elif bina_yasi < 1999: yon = "1975–1998 arası eski yönetmelik"
        elif bina_yasi < 2007: yon = "1999–2006 arası yönetmelik"
        else:                  yon = "2007+ güncel deprem yönetmeliği"

        bina_deg = (
            f"{bina_yasi} yılında inşa edilen bu {kat} katlı yapı ({bina_turu}) "
            f"{yon} kapsamındadır. Zemin türü '{zemin}', "
            f"en yakın fay hattına uzaklık {fay_km} km. "
            f"**Ek Bilgi:** Girdiğiniz koordinat çevresinde son 10 yılda 4.0 üstü {len(gecmis_depremler)} deprem kaydedilmiştir."
        )

        # 5. ACİL ÇANTA LİSTESİ (Esma'nın Orijinali)
        canta = [
            f"Su — kişi başı 3 lt/gün × 3 gün → toplam {hane * 9} litre",
            f"Kuru gıda / enerji barı (3 günlük, {hane} kişilik)",
            "İlk yardım çantası (bandaj, antiseptik, makas, flaster)",
            "Kişisel ilaçlar (en az 1 haftalık stok)",
            "El feneri + yedek pil / krank feneri",
            "Düdük (enkaz altı iletişim)",
            f"Şarj edilmiş powerbank × {max(1, hane // 2)} adet",
            "Önemli belgeler — fotokopi + dijital yedek (kimlik, tapu, sigorta)",
            "Nakit para — küçük banknotlar",
            "N95 toz maskesi (kişi başı 2 adet)",
            "Isı battaniyesi / mylar örtü",
            "Yedek kıyafet ve sağlam ayakkabı",
        ]
        if "Bebek / küçük çocuk" in ozel: canta.append("Bebek bezi, maması, biberon, steril su")
        if "Yaşlı birey" in ozel: canta.append("İşitme cihazı pili, gözlük yedeği, hareket yardımcısı")
        if "Engelli birey" in ozel: canta.append("Tekerlekli sandalye şarj aleti / yedek güç kaynağı")
        if "Kronik hasta" in ozel: canta.append("Kronik ilaçlar (2 haftalık), tıbbi belgeler")
        if "Evcil hayvan" in ozel: canta.append("Evcil hayvan maması (3 günlük), taşıma çantası, aşı karnesi")

        # 6. EYLEM PLANI (Liste + Toplanma Alanı)
        plan = [
            "Evin güvenli köşelerini (iç duvar dipleri) ve tehlikeli noktalarını (camlar, dolap üstleri) tespit edin.",
            f"Haritada işaretlenen en yakın toplanma alanınız olan **{alan_adi}** noktasını ailenizle önceden ziyaret edin.",
            "Komşularla iletişim ağı kurun — yaşlı, çocuk ve engelli komşulara öncelik verin.",
            "Su ve gaz vanalarının kapatma konumlarını öğrenin; 6 ayda bir tatbikat yapın.",
            "Acil çantanızı kapıya yakın, erişimi kolay yerde tutun ve yılda iki kez içini kontrol edin.",
            "AFAD veya Kızılay temel ilk yardım eğitimine katılın.",
        ]
        if skor >= 60: plan.insert(1, "Risk seviyeniz yüksek — lisanslı bir yapı mühendisine bina güçlendirme başvurusu yapın.")
        if "Alüvyon" in zemin or "Dolgu" in zemin: plan.append("Zemin türünüz sıvılaşma riski taşıyabilir; belediyeden statik rapor talep edin.")

        # 7. AJAN YORUMU (Esma'nın Orijinali)
        yorum = f"Gerçek verilerle analiz tamamlandı. Risk skoru {skor}/100 ({etiket}). "
        if skor >= 80:   yorum += "ACİL önlem alın; bina güçlendirme başvurusu önceliklidir."
        elif skor >= 60: yorum += "Kısa vadede uzman incelemesi ve çanta hazırlığı yapılmalıdır."
        elif skor >= 40: yorum += "Temel hazırlıkları tamamlayın ve yılda iki kez gözden geçirin."
        else:            yorum += "Risk görece düşük; rutin hazırlıklarınızı güncel tutun."

        # 8. HARİTA İÇİN VERİ HAZIRLIĞI
        harita_noktalari = [{
            "ad": toplanma_verisi.get("name"),
            "lat": toplanma_verisi.get("lat", lat),
            "lon": toplanma_verisi.get("lon", lon),
            "tip": "park"
        }]

        return {
            "risk_skoru": skor,
            "risk_etiketi": etiket,
            "bina_degerlendirmesi": bina_deg,
            "acil_canta_listesi": canta,
            "eylem_plani": plan,
            "ajan_yorumu": yorum,
            "user_lat": lat,
            "user_lon": lon,
            "toplanma_alanlari_listesi": harita_noktalari
        }

    def get_memory_summary(self) -> list[dict]:
        return self.memory