def calculate_risk_score(building_age: int, floor_count: int, has_soft_story: bool, earthquake_history: list) -> int:
    """
    Bina ve bölge verilerine göre deprem risk skoru hesaplar (1-100 arası).
    Düşük skor iyi, yüksek skor kötüdür.
    
    Parametreler:
    - building_age: Binanın yaşı (yıl)
    - floor_count: Binanın toplam kat sayısı
    - has_soft_story: Yumuşak kat var mı? (Zemin katta dükkan vb.) (True/False)
    - earthquake_history: get_earthquake_data() fonksiyonundan dönen deprem listesi
    """

    # Veri Doğrulama (Edge-case yönetimi ve tip kontrolleri)
    try:
        building_age = int(building_age)
        floor_count = int(floor_count)
    except ValueError:
        raise ValueError("Bina yaşı ve kat sayısı geçerli bir sayısal değer olmalıdır.")

    if building_age < 0 or building_age > 200:
        raise ValueError(f"Mantıksız bir bina yaşı girildi: {building_age}")
        
    if floor_count < 1 or floor_count > 160:
        raise ValueError(f"Mantıksız bir kat sayısı girildi: {floor_count}")
        
    if not isinstance(has_soft_story, bool):
        raise TypeError("Yumuşak kat bilgisi True veya False (Mantıksal) olmalıdır.")
    
    # Başlangıç Puanı
    risk_score = 10 
    
    # Bina Yaşı Etkisi (1999 depremi ve 2018 yönetmeliği kritik eşikler)
    if building_age > 25:
        risk_score += 35 # 1999 öncesi çok riskli
    elif 6 < building_age <= 25:
        risk_score += 20 # 1999-2018 arası orta riskli
    else:
        risk_score += 5  # yeni binalar daha güvenli
        
    # Kat Sayısı Etkisi
    if floor_count > 10:
        risk_score += 15
    elif 5 < floor_count <= 10:
        risk_score += 10
    else:
        risk_score += 5
        
    # Yumuşak Kat (Zemin katta dükkan/galeri boşluğu vs.)
    if has_soft_story:
        risk_score += 20
        
    # Bölgesel Sismik Aktivite Etkisi (earthquake_api.py den gelen veri)
    recent_strong_quakes = [eq for eq in earthquake_history if float(eq['magnitude']) >= 5.0]
    
    if len(recent_strong_quakes) > 5:
        risk_score += 20 # Çok aktif bölge
    elif 1 < len(recent_strong_quakes) <= 5:
        risk_score += 10 # Orta aktif bölge
        
    # Skoru 1-100 arasına sınırla (Matematiksel güvenlik)
    risk_score = max(1, min(100, risk_score))
    
    return risk_score

# Test Bloğu
if __name__ == "__main__":
    # Test verileri (kullanıcı bunları formdan girmiş gibi)
    test_age = 30
    test_floors = 7
    test_soft_story = True
    
    # earthquake_api.py den dönen veriyi taklit etmek için
    mock_eq_data = [
        {"magnitude": 5.2, "date": "2023-01-01"},
        {"magnitude": 4.5, "date": "2023-05-01"}
    ]
    
    # kritik hesaplama satırı burası
    score = calculate_risk_score(test_age, test_floors, test_soft_story, mock_eq_data)
    
    print(f"Bina Yaşı: {test_age}, Kat: {test_floors}, Yumuşak Kat: {test_soft_story}")
    print(f"Hesaplanan Risk Skoru: {score} / 100")