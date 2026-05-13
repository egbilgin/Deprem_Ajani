# 🌍 Otonom Deprem Hazırlık ve Afet Yönetim Ajanı

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Folium-77B829?style=for-the-badge&logo=leaflet&logoColor=white" />
</p>

> **Afet anında saniyeler hayati önem taşır.** Bu proje, kullanıcıların tam konumlarını, bina özelliklerini ve bölgesel sismik geçmişlerini analiz ederek saniyeler içinde kişiselleştirilmiş bir acil durum eylem planı üreten otonom bir AI Agent sistemidir.

---

## 🚀 Öne Çıkan Özellikler

-  **Dinamik Konum Analizi:** `Geopy` entegrasyonu ile sadece şehir değil, sokak ve bina düzeyinde konum belirleme.
- **Deterministik Risk Skoru:** Yapay zekanın "halüsinasyon" görmesini engelleyen, sismik gerçekliğe dayalı 1-100 arası matematiksel puanlama.
-  **İnteraktif Harita:** `Folium` ile kullanıcının evi ve en yakın toplanma alanı arasındaki rotayı görselleştirme.
-  **Akıllı Çanta Hesabı:** Hanedeki kişi sayısına (bebek, yaşlı, evcil hayvan durumu) göre otomatik hesaplanan ihtiyaç listesi.
-  **Otonom Karar Mekanizması:** Arka plandaki araçlardan (tools) gelen verileri yorumlayarak empati kuran bir eylem planı sunan mimari.

---

## 🛠️ Mimari Yaklaşım: Context-Augmented Agent

Bu proje, geleneksel bir chatbot yerine **Ajan-Araç (Agent-Tool)** mimarisi üzerine inşa edilmiştir.

1. **Veri Katmanı (Backend Tools):** USGS API'den deprem verisi çeken ve Haversine formülüyle mesafe hesaplayan Python modülleri.
2. **Bağlam Katmanı (Context):** Araçlardan gelen kesin verilerin prompt mühendisliği ile ajana aktarılması.
3. **Sunum Katmanı (Frontend):** Modern ve karanlık tema (Dark UI) odaklı Streamlit arayüzü.

---

## 📦 Kurulum ve Çalıştırma

Projeyi yerel makinenizde ayağa kaldırmak için şu adımları izleyin:

### 1. Depoyu Klonlayın
```bash
git clone [https://github.com/egbilgin/deprem_ajani.git](https://github.com/egbilgin/deprem_ajani.git)
cd deprem_ajani
