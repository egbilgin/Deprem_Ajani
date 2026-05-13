"""
map_helper.py
=============
Kullanıcı konumunu ve toplanma alanlarını Folium haritasında gösterir.
app.py tarafından çağrılır; agent_core.py'den dönen toplanma_alanlari
listesini alarak marker'ları dinamik olarak oluşturur.
"""

import folium
from folium.plugins import MarkerCluster


# ─── Renk & İkon Paleti ──────────────────────────────────────────────────────
_TIP_CONFIG = {
    "park":  {"color": "green",  "icon": "tree-conifer", "prefix": "glyphicon"},
    "okul":  {"color": "blue",   "icon": "education",    "prefix": "glyphicon"},
    "spor":  {"color": "purple", "icon": "star",         "prefix": "glyphicon"},
    "hastane": {"color": "red",  "icon": "plus-sign",    "prefix": "glyphicon"},
    "default": {"color": "gray", "icon": "map-marker",   "prefix": "glyphicon"},
}


def _risk_circle_color(risk_skoru: int) -> str:
    """Risk skoruna göre çember rengi."""
    if risk_skoru >= 80:
        return "#ff3b30"
    elif risk_skoru >= 60:
        return "#ff9500"
    elif risk_skoru >= 40:
        return "#ffcc00"
    return "#34c759"


def create_map(
    lat: float,
    lon: float,
    adres: str = "",
    toplanma_alanlari: list[dict] | None = None,
    risk_skoru: int = 0,
) -> folium.Map:
    """
    Folium haritası oluşturur ve döndürür.

    Parametreler
    ------------
    lat, lon          : Kullanıcının konumu
    adres             : Popup'ta gösterilecek adres metni
    toplanma_alanlari : [{"ad": str, "lat": float, "lon": float, "tip": str}, ...]
    risk_skoru        : 0-100 arası risk skoru (çember rengi için)

    Döndürür
    --------
    folium.Map objesi
    """
    toplanma_alanlari = toplanma_alanlari or []

    # ── Harita Tabanı ────────────────────────────────────────────────────────
    m = folium.Map(
        location=[lat, lon],
        zoom_start=15,
        tiles="CartoDB dark_matter",   # Koyu tema — arayüzle uyumlu
        control_scale=True,
    )

    # ── Kullanıcı Konumu: Kırmızı Çember + Marker ───────────────────────────
    circle_color = _risk_circle_color(risk_skoru)

    folium.Circle(
        location=[lat, lon],
        radius=200,
        color=circle_color,
        fill=True,
        fill_color=circle_color,
        fill_opacity=0.15,
        weight=2,
        tooltip="Risk bölgesi (yaklaşık 200m)",
    ).add_to(m)

    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(
            f"""
            <div style="font-family:monospace; font-size:12px; min-width:160px;">
                <b style="color:#ff3b30;">📍 Konumunuz</b><br>
                {adres or 'Girilen Konum'}<br>
                <hr style="border-color:#333; margin:4px 0;">
                Risk Skoru: <b style="color:{circle_color};">{risk_skoru}/100</b>
            </div>
            """,
            max_width=220,
        ),
        tooltip="📍 Konumunuz",
        icon=folium.Icon(color="red", icon="home", prefix="glyphicon"),
    ).add_to(m)

    # ── Toplanma Alanları ────────────────────────────────────────────────────
    if toplanma_alanlari:
        cluster = MarkerCluster(name="Toplanma Alanları").add_to(m)

        for alan in toplanma_alanlari:
            tip = alan.get("tip", "default")
            cfg = _TIP_CONFIG.get(tip, _TIP_CONFIG["default"])
            alan_lat = alan.get("lat", lat)
            alan_lon = alan.get("lon", lon)
            alan_ad  = alan.get("ad", "Toplanma Alanı")

            # Mesafe hesapla (Haversine basit yaklaşım — km)
            dist_km = _approx_distance(lat, lon, alan_lat, alan_lon)

            folium.Marker(
                location=[alan_lat, alan_lon],
                popup=folium.Popup(
                    f"""
                    <div style="font-family:monospace; font-size:12px; min-width:160px;">
                        <b>🏃 {alan_ad}</b><br>
                        Tür: {tip.capitalize()}<br>
                        Mesafe: ~{dist_km:.2f} km
                    </div>
                    """,
                    max_width=200,
                ),
                tooltip=f"🏃 {alan_ad}",
                icon=folium.Icon(
                    color=cfg["color"],
                    icon=cfg["icon"],
                    prefix=cfg["prefix"],
                ),
            ).add_to(cluster)

            # Konum → Toplanma alanı arası kesik çizgi
            folium.PolyLine(
                locations=[[lat, lon], [alan_lat, alan_lon]],
                color=cfg["color"],
                weight=1.5,
                dash_array="6 4",
                opacity=0.5,
                tooltip=f"{alan_ad} rotası",
            ).add_to(m)

    # ── Katman Kontrolü ──────────────────────────────────────────────────────
    folium.LayerControl(collapsed=False).add_to(m)

    # ── Lejant (sağ alt köşe) ────────────────────────────────────────────────
    legend_html = """
    <div style="
        position: fixed;
        bottom: 20px; right: 10px; z-index: 1000;
        background: #111; border: 1px solid #333; border-radius: 4px;
        padding: 8px 12px; font-family: monospace; font-size: 11px; color: #ccc;
    ">
        <b style="color:#ff3b30; letter-spacing:1px;">LEJANT</b><br>
        <span style="color:#ff3b30;">●</span> Konumunuz<br>
        <span style="color:green;">●</span> Park<br>
        <span style="color:#4488ff;">●</span> Okul<br>
        <span style="color:purple;">●</span> Spor Alanı<br>
        <span style="color:red;">●</span> Hastane
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


# ─── Yardımcı: Yaklaşık mesafe ───────────────────────────────────────────────
def _approx_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine formülüyle iki nokta arası km mesafesi."""
    import math
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))