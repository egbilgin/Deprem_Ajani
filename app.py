"""
app.py
======
Deprem Hazırlık Ajanı — Streamlit Arayüzü
Çalıştırma: streamlit run app.py
"""

import streamlit as st
import time
from agent_core import EarthquakeAgent
from map_helper import create_map
import streamlit.components.v1 as components

# ── Sayfa Konfigürasyonu ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Deprem Hazırlık Ajanı",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,600;1,300&display=swap');

/* ── Genel ── */
html, body, [class*="css"] {
    background-color: #080808 !important;
    color: #ddd8cf;
    font-family: 'IBM Plex Sans', sans-serif;
}

/* ── Hero ── */
.hero-wrap   { padding: 2.5rem 0 0.75rem; }
.hero-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.35em;
    color: #ff3b30;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(3.5rem, 9vw, 6.5rem);
    line-height: 0.92;
    letter-spacing: 0.04em;
    color: #ddd8cf;
    margin: 0;
}
.hero-title span { color: #ff3b30; }
.hero-rule {
    border: none;
    border-top: 1.5px solid #ff3b30;
    margin: 1.25rem 0 2rem;
}

/* ── Section Label ── */
.sec-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.3em;
    color: #ff3b30;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}

/* ── Input overrides ── */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    background: #111 !important;
    border: 1px solid #252525 !important;
    border-radius: 3px !important;
    color: #ddd8cf !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem !important;
}
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stMultiSelect"] > div > div {
    background: #111 !important;
    border: 1px solid #252525 !important;
    border-radius: 3px !important;
    color: #ddd8cf !important;
}

/* ── Buton ── */
div[data-testid="stButton"] > button {
    background: #ff3b30 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 3px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    padding: 0.7rem 2rem !important;
    width: 100% !important;
    margin-top: 0.5rem !important;
    transition: opacity 0.15s !important;
}
div[data-testid="stButton"] > button:hover { opacity: 0.82 !important; }

/* ── Divider ── */
div[data-testid="stMarkdownContainer"] hr {
    border-color: #1c1c1c;
    margin: 0.75rem 0;
}

/* ── Risk Kartı ── */
.risk-card {
    border-radius: 4px;
    padding: 1.5rem 1.5rem 1.25rem;
    margin-bottom: 1rem;
    border: 1px solid;
}
.risk-num {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 5.5rem;
    line-height: 1;
    display: block;
}
.risk-tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-top: 0.3rem;
    display: block;
}
.risk-desc {
    font-size: 0.82rem;
    color: #999;
    font-style: italic;
    margin-top: 0.75rem;
    line-height: 1.55;
}

/* ── Metrik Kutuları ── */
.m-box {
    background: #0f0f0f;
    border: 1px solid #1c1c1c;
    border-radius: 4px;
    padding: 0.9rem 1rem;
    text-align: center;
}
.m-val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.1rem;
    color: #ddd8cf;
    display: block;
}
.m-lbl {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.55rem;
    letter-spacing: 0.2em;
    color: #444;
    text-transform: uppercase;
}

/* ── Ajan Yorumu ── */
.agent-box {
    background: #0f0f0f;
    border: 1px solid #1c1c1c;
    border-left: 3px solid #ff3b30;
    border-radius: 3px;
    padding: 0.85rem 1rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: #aaa;
    margin-bottom: 1.25rem;
    line-height: 1.6;
}
.agent-box strong { color: #ff3b30; }

/* ── Liste Satırları ── */
.list-row {
    display: flex;
    gap: 0.85rem;
    padding: 0.55rem 0;
    border-bottom: 1px solid #141414;
    align-items: flex-start;
    font-size: 0.86rem;
    line-height: 1.5;
}
.list-idx {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    color: #ff3b30;
    min-width: 1.75rem;
    padding-top: 3px;
}
.list-arrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: #ff3b30;
    min-width: 1.25rem;
    padding-top: 2px;
}
.step-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.55rem;
    letter-spacing: 0.2em;
    color: #ff3b30;
    display: block;
    margin-bottom: 2px;
}

/* ── Sekme override ── */
div[data-testid="stTabs"] button {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #555 !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #ddd8cf !important;
    border-bottom-color: #ff3b30 !important;
}

/* ── Uyarı ── */
.warn {
    background: #130a0a;
    border: 1px solid #ff3b30;
    border-radius: 3px;
    padding: 0.6rem 0.9rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: #ff6b62;
    margin-bottom: 0.75rem;
}

/* ── Boş durum ── */
.empty-state {
    display: flex;
    height: 55vh;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 0.75rem;
    text-align: center;
}
.empty-icon { font-size: 3.5rem; opacity: 0.25; }
.empty-text {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    color: #333;
    text-transform: uppercase;
}

/* ── Footer ── */
.footer {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.15em;
    color: #252525;
    text-align: center;
    margin-top: 2.5rem;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "agent" not in st.session_state:
    st.session_state.agent = EarthquakeAgent()

# ── Yardımcılar ───────────────────────────────────────────────────────────────
def risk_style(score: int) -> tuple[str, str]:
    """(hex_renk, etiket) döndürür."""
    if score >= 80:   return "#ff3b30", "KRİTİK"
    elif score >= 60: return "#e07b00", "YÜKSEK"
    elif score >= 40: return "#c9a800", "ORTA"
    return "#2db34a", "DÜŞÜK"

# ════════════════════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-wrap">
  <p class="hero-eyebrow">// Yapay Zeka Destekli Sistem — v1.0</p>
  <h1 class="hero-title">DEPREM<br><span>HAZIRLIK</span><br>AJANI</h1>
</div>
<hr class="hero-rule">
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# İKİ SÜTUN
# ════════════════════════════════════════════════════════════════════════════
col_form, col_out = st.columns([1, 1.55], gap="large")

# ═══════════════════ SOL — FORM ══════════════════════════════════════════════
with col_form:
    st.markdown('<p class="sec-label">// Konum Bilgileri</p>', unsafe_allow_html=True)
    adres = st.text_input("Adres / İlçe", placeholder="örn: Adapazarı, Sakarya")

    st.markdown("---")
    st.markdown('<p class="sec-label">// Bina Bilgileri</p>', unsafe_allow_html=True)

    bina_turu = st.selectbox("Yapı Türü", [
        "Betonarme (Perde Duvarsız)",
        "Betonarme (Perde Duvarlı)",
        "Yığma Tuğla",
        "Prefabrik",
        "Ahşap / Diğer",
    ])

    c1, c2 = st.columns(2)
    with c1:
        bina_yasi = st.number_input("İnşaat Yılı", 1900, 2025, 1995, step=1)
    with c2:
        kat = st.number_input("Kat Sayısı", 1, 40, 5)

    zemin = st.selectbox("Zemin Türü", [
        "Bilinmiyor",
        "Sağlam Kaya",
        "Kum / Çakıl",
        "Alüvyon (Dere Yatağı)",
        "Dolgu Zemin",
    ])

    fay_km = st.number_input(
        "En Yakın Fay Hattı Mesafesi (km)",
        min_value=0.0, max_value=500.0, value=15.0, step=0.5,
    )

    st.markdown("---")
    st.markdown('<p class="sec-label">// Hane Bilgileri</p>', unsafe_allow_html=True)

    hane = st.number_input("Hanedeki Kişi Sayısı", 1, 20, 4)
    ozel = st.multiselect("Özel İhtiyaç (varsa)", [
        "Bebek / küçük çocuk",
        "Yaşlı birey",
        "Engelli birey",
        "Kronik hasta",
        "Evcil hayvan",
    ])

    analiz_btn = st.button("ANALİZİ BAŞLAT")

    if analiz_btn:
        if not adres.strip():
            st.markdown('<div class="warn">⚠ Lütfen adres alanını doldurun.</div>', unsafe_allow_html=True)
        else:
            user_data = {
                "adres": adres,
                "bina_turu": bina_turu,
                "bina_yasi": bina_yasi,
                "kat_sayisi": kat,
                "zemin_turu": zemin,
                "yakin_fay_km": fay_km,
                "hane_sayisi": hane,
                "ozel_ihtiyac": ozel,
            }
            st.session_state.user_data = user_data

            with st.spinner("Ajan analiz yapıyor…"):
                time.sleep(0.9)
                st.session_state.result = st.session_state.agent.analyze(user_data)

# ═══════════════════ SAĞ — SONUÇLAR ══════════════════════════════════════════
with col_out:
    if st.session_state.result is None:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🔴</div>
            <p class="empty-text">Formu doldurun ve analizi başlatın</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        r     = st.session_state.result
        ud    = st.session_state.user_data
        skor  = r["risk_skoru"]
        rclr, retk = risk_style(skor)

        # ── Risk Kartı ──────────────────────────────────────────────────────
        st.markdown('<p class="sec-label">// Risk Analizi</p>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="risk-card" style="border-color:{rclr}; background:#0d0d0d;">
            <span class="risk-num" style="color:{rclr};">{skor}</span>
            <span class="risk-tag" style="color:{rclr};">Risk Seviyesi: {retk}</span>
            <p class="risk-desc">{r['bina_degerlendirmesi']}</p>
        </div>
        """, unsafe_allow_html=True)

        # ── Metrikler ───────────────────────────────────────────────────────
        m1, m2, m3 = st.columns(3)
        for col, val, lbl in [
            (m1, ud.get("bina_yasi", "—"), "İnşaat Yılı"),
            (m2, ud.get("kat_sayisi", "—"), "Kat Sayısı"),
            (m3, f'{ud.get("yakin_fay_km","—")} km', "Fay Mesafesi"),
        ]:
            with col:
                st.markdown(f"""
                <div class="m-box">
                    <span class="m-val">{val}</span>
                    <span class="m-lbl">{lbl}</span>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Ajan Yorumu ─────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="agent-box">
            <strong>🤖 Ajan:</strong> {r['ajan_yorumu']}
        </div>""", unsafe_allow_html=True)

        # ── Sekmeler ────────────────────────────────────────────────────────
        # ── Sekmeler ────────────────────────────────────────────────────────
        tab_canta, tab_plan, tab_harita = st.tabs(["🎒  Acil Çanta", "📋  Eylem Planı", "🗺️ Toplanma Haritası"])

        with tab_canta:
            for i, item in enumerate(r["acil_canta_listesi"], 1):
                st.markdown(f"- {item}")

        with tab_plan:
            for i, adim in enumerate(r["eylem_plani"], 1):
                st.markdown(f"**ADIM {i}:** {adim}")
                
        with tab_harita:
            st.markdown(f"### 📍 En Yakın Toplanma Alanı: {r['toplanma_alanlari_listesi'][0]['ad']}")
            
            # SABİT KOORDİNATLARI SİLDİK, AJANDAN GELEN GERÇEK KONUMU VERİYORUZ
            m = create_map(
                lat=r["user_lat"], 
                lon=r["user_lon"], 
                adres=ud.get("adres", ""), 
                toplanma_alanlari=r["toplanma_alanlari_listesi"], 
                risk_skoru=skor
            )
            components.html(m._repr_html_(), height=500)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""<hr style="border-color:#141414; margin-top:3rem;">
<p class="footer">DEPREM HAZIRLIK AJANI — EĞİTİM AMAÇLIDIR — AFAD &amp; KOERI VERİLERİYLE ÇALIŞIR</p>
""", unsafe_allow_html=True)