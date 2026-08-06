"""
Biga İktisadi ve İdari Bilimler Fakültesi
Boş Derslik Bulucu Uygulaması

Bu uygulama, haftalık ders programı PDF dosyasını analiz ederek
seçilen gün ve saatte boş olan derslikleri listeler.
"""

import streamlit as st
import pdfplumber
import re
from io import BytesIO

# ─────────────────────────────────────────────
# SAYFA YAPILANDIRMASI
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Boş Derslik Bulucu | Biga İİBF",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# SESSION STATE BAŞLATMA
# ─────────────────────────────────────────────
if "sonuc_dolu" not in st.session_state:
    st.session_state.sonuc_dolu = None
if "sonuc_bos" not in st.session_state:
    st.session_state.sonuc_bos = None
if "sonuc_debug" not in st.session_state:
    st.session_state.sonuc_debug = []
if "sonuc_yontem" not in st.session_state:
    st.session_state.sonuc_yontem = ""
if "sonuc_gun" not in st.session_state:
    st.session_state.sonuc_gun = ""
if "sonuc_saat" not in st.session_state:
    st.session_state.sonuc_saat = ""
if "sonuc_pdf_adi" not in st.session_state:
    st.session_state.sonuc_pdf_adi = ""

# ─────────────────────────────────────────────
# ÖZEL CSS STİLLERİ
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── LIGHT THEME BACKGROUND ────────────────── */
    .stApp {
        background: #f0f4f8;
        min-height: 100vh;
    }

    /* Main content area white card */
    [data-testid="stAppViewContainer"] > .main > .block-container {
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 2px 16px rgba(99, 102, 241, 0.07);
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* ── HERO CARD ──────────────────────────────── */
    .hero-card {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 50%, #0ea5e9 100%);
        border-radius: 20px;
        padding: 2.5rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.25);
        position: relative;
        overflow: hidden;
    }
    .hero-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%);
        animation: shimmer 5s ease-in-out infinite;
    }
    @keyframes shimmer {
        0%, 100% { transform: translateX(-10%) translateY(-10%); }
        50%       { transform: translateX(10%)  translateY(10%);  }
    }
    .hero-title {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 8px rgba(0,0,0,0.18);
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        color: rgba(255,255,255,0.88);
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }

    /* ── INFO BOX ───────────────────────────────── */
    .info-box {
        background: #eef2ff;
        border: 1px solid #c7d2fe;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 1.5rem;
        color: #3730a3;
        font-size: 0.875rem;
    }
    .info-box strong { color: #4338ca; }
    .info-box code {
        background: #c7d2fe;
        color: #3730a3;
        padding: 1px 5px;
        border-radius: 4px;
        font-size: 0.8rem;
    }

    /* ── CLASSROOM CARDS — EMPTY (available) ─────── */
    .classroom-card-empty {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 1.5px solid #34d399;
        border-radius: 14px;
        padding: 1rem 0.75rem;
        text-align: center;
        color: #065f46;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.25s ease;
        cursor: default;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.12);
        margin-bottom: 0.5rem;
    }
    .classroom-card-empty:hover {
        border-color: #059669;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.22);
        transform: translateY(-3px);
        background: linear-gradient(135deg, #a7f3d0 0%, #6ee7b7 100%);
    }

    /* ── CLASSROOM CARDS — OCCUPIED ─────────────── */
    .classroom-card-occupied {
        background: #fff1f2;
        border: 1.5px solid #fca5a5;
        border-radius: 14px;
        padding: 1rem 0.75rem;
        text-align: center;
        color: #9f1239;
        font-weight: 500;
        font-size: 0.9rem;
        opacity: 0.75;
        margin-bottom: 0.5rem;
    }

    /* ── RESULT HEADER ──────────────────────────── */
    .result-header {
        background: #f8faff;
        border: 1px solid #e0e7ff;
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        margin: 1.5rem 0 1rem 0;
        box-shadow: 0 1px 6px rgba(99,102,241,0.07);
    }
    .result-header h3 {
        color: #1e1b4b;
        margin: 0 0 0.25rem 0;
        font-size: 1.2rem;
        font-weight: 700;
    }
    .result-header p {
        color: #64748b;
        margin: 0;
        font-size: 0.875rem;
    }

    /* ── STAT BADGES ─────────────────────────────── */
    .stat-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 8px;
    }
    .stat-empty {
        background: #d1fae5;
        color: #065f46;
        border: 1px solid #6ee7b7;
    }
    .stat-occupied {
        background: #fee2e2;
        color: #991b1b;
        border: 1px solid #fca5a5;
    }

    /* ── ALERT BOXES ─────────────────────────────── */
    .warning-box {
        background: #fffbeb;
        border: 1px solid #fcd34d;
        border-left: 4px solid #f59e0b;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        color: #78350f;
        font-size: 0.875rem;
        margin: 1rem 0;
    }
    .success-box {
        background: #f0fdf4;
        border: 1px solid #86efac;
        border-left: 4px solid #22c55e;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        color: #14532d;
        font-size: 0.875rem;
        margin: 1rem 0;
    }
    .error-box {
        background: #fff1f2;
        border: 1px solid #fca5a5;
        border-left: 4px solid #ef4444;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        color: #7f1d1d;
        font-size: 0.875rem;
        margin: 1rem 0;
    }

    /* ── FILE UPLOADER ───────────────────────────── */
    [data-testid="stFileUploader"] {
        background: #f8faff !important;
        border: 2px dashed #a5b4fc !important;
        border-radius: 14px !important;
        padding: 0.75rem !important;
    }

    /* ── SELECT BOX & MULTISELECT ────────────────── */
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stMultiSelect"] > div > div {
        background: #ffffff !important;
        border: 1.5px solid #c7d2fe !important;
        border-radius: 10px !important;
        color: #1e1b4b !important;
    }

    /* ── BUTTON ──────────────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5, #6366f1) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.65rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
        width: 100% !important;
        letter-spacing: 0.01em !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 22px rgba(99, 102, 241, 0.45) !important;
        background: linear-gradient(135deg, #4338ca, #4f46e5) !important;
    }

    /* ── DIVIDER ─────────────────────────────────── */
    hr {
        border-color: #e2e8f0 !important;
        margin: 1.5rem 0 !important;
    }

    /* ── SIDEBAR ─────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: #f8f9fd !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    [data-testid="stSidebar"] h3 {
        color: #1e1b4b !important;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown strong {
        color: #374151 !important;
    }

    /* ── LABELS ──────────────────────────────────── */
    label {
        color: #4b5563 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }

    /* ── EXPANDER ────────────────────────────────── */
    [data-testid="stExpander"] {
        background: #fafbff !important;
        border: 1px solid #e0e7ff !important;
        border-radius: 12px !important;
    }

    /* ── DEBUG AREA ──────────────────────────────── */
    .debug-area {
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        font-size: 0.78rem;
        color: #475569;
        max-height: 300px;
        overflow-y: auto;
        margin-top: 1rem;
    }

    /* ── FOOTER ──────────────────────────────────── */
    div[style*="text-align:center"] {
        color: #94a3b8 !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SABİT VERİLER
# ─────────────────────────────────────────────

# Fakültedeki tüm derslikler (ana liste)
TUM_DERSLIKLER = [
    "101", "102", "103", "104", "105", "106", "107", "108",
    "201", "202", "203", "204", "205", "206", "207", "208",
    "B1", "B2", "B3", "B4",
    "Z01", "Z02", "Z04", "Z05", "Z06", "Z07", "Z08",
    "Bilgisayar Lab."
]

# Haftanın günleri (PDF sütun başlıklarıyla birebir eşleşmeli)
GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]

# Ders saatleri (PDF'deki zaman dilimleriyle birebir eşleşmeli)
SAATLER = [
    "09:00 - 09:45",
    "09:50 - 10:35",
    "10:40 - 11:25",
    "11:30 - 12:15",
    "12:20 - 13:05",
    "13:10 - 13:55",
    "14:00 - 14:45",
    "14:50 - 15:35",
    "15:40 - 16:25",
    "16:30 - 17:15",
    "17:20 - 18:05",
    "18:10 - 18:55",
    "19:00 - 19:45",
    "19:50 - 20:35",
    "20:40 - 21:25",
    "21:30 - 22:15",
]

# Zaman dilimlerini PDF formatından uygulama formatına eşleyen sözlük
# PDF'de "09:00\n09:45" şeklinde görünebilir; burada normalize ediyoruz.
SAAT_NORMALIZASYON = {s.replace(" - ", "\n"): s for s in SAATLER}
SAAT_NORMALIZASYON.update({s.replace(" - ", " "): s for s in SAATLER})
SAAT_NORMALIZASYON.update({s: s for s in SAATLER})


# ─────────────────────────────────────────────
# YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────

def normalize_saat(raw: str) -> str:
    """
    PDF'den okunan ham saat metnini standart formata dönüştürür.
    Örnek: '09:00\n09:45' → '09:00 - 09:45'
    """
    if not raw:
        return ""
    # Satır sonları ve fazla boşlukları temizle
    temiz = raw.strip().replace("\n", " ").replace("  ", " ")
    # "09:00 09:45" → "09:00 - 09:45"
    temiz = re.sub(r"(\d{2}:\d{2})\s+(\d{2}:\d{2})", r"\1 - \2", temiz)

    return temiz


def hucredeki_derslikleri_cikart(hucre_metni: str) -> list[str]:
    """
    Tablo hücresindeki metinden derslik isimlerini çıkarır.
    Derslik isimleri hücre içinde dikey olarak sıralanmıştır.
    """
    if not hucre_metni:
        return []

    dolu = []
    satırlar = hucre_metni.strip().split("\n")

    for satır in satırlar:
        satır = satır.strip()
        if not satır:
            continue
        for derslik in TUM_DERSLIKLER:
            # Tam kelime eşleşmesi (büyük/küçük harf duyarsız)
            if re.search(r"(?<!\w)" + re.escape(derslik) + r"(?!\w)", satır, re.IGNORECASE):
                if derslik not in dolu:
                    dolu.append(derslik)

    return dolu


def pdf_tablo_yontemiyle_isle(pdf_bytes: bytes, hedef_gun: str, hedef_saat: str) -> tuple[list, list, list, str]:
    """
    pdfplumber kullanarak PDF'den tablo verilerini çıkarır.

    Döndürür: (dolu_derslikler, bos_derslikler, ham_satirlar, debug_mesaj)
    """
    debug_satirlar = []
    dolu_derslikler = []

    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            for sayfa_no, sayfa in enumerate(pdf.pages):
                debug_satirlar.append(f"📄 Sayfa {sayfa_no + 1} işleniyor...")

                # ── Yöntem 1: Otomatik tablo algılama ──────────────────────
                tablolar = sayfa.extract_tables({
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                    "snap_tolerance": 5,
                    "join_tolerance": 5,
                    "edge_min_length": 10,
                    "min_words_vertical": 1,
                    "min_words_horizontal": 1,
                    "intersection_tolerance": 5,
                })

                if not tablolar:
                    # ── Yöntem 1b: Metin tabanlı tablo algılama ──────────
                    tablolar = sayfa.extract_tables({
                        "vertical_strategy": "text",
                        "horizontal_strategy": "text",
                        "snap_tolerance": 8,
                        "join_tolerance": 8,
                    })
                    if tablolar:
                        debug_satirlar.append("  ℹ️  Metin tabanlı tablo yöntemi kullanıldı.")

                if not tablolar:
                    debug_satirlar.append("  ⚠️  Bu sayfada tablo bulunamadı.")
                    continue

                for tablo_no, tablo in enumerate(tablolar):
                    debug_satirlar.append(f"  📊 Tablo {tablo_no + 1}: {len(tablo)} satır × {len(tablo[0]) if tablo else 0} sütun")

                    if not tablo or len(tablo) < 2:
                        continue

                    # Başlık satırını bul (gün adlarını içeriyor)
                    baslik_satir_idx = None
                    gun_sutun_idx = {gun: None for gun in GUNLER}

                    for satir_idx, satir in enumerate(tablo[:5]):  # İlk 5 satırı tara
                        satir_metni = " ".join(str(h or "") for h in satir).upper()
                        if any(gun.upper() in satir_metni for gun in GUNLER):
                            baslik_satir_idx = satir_idx
                            # Sütun indekslerini belirle
                            for sutun_idx, baslik in enumerate(satir):
                                baslik_str = str(baslik or "").strip()
                                for gun in GUNLER:
                                    if gun.lower() in baslik_str.lower():
                                        gun_sutun_idx[gun] = sutun_idx
                                        debug_satirlar.append(f"    ✅ '{gun}' → sütun {sutun_idx}")
                            break

                    if baslik_satir_idx is None:
                        debug_satirlar.append("  ⚠️  Gün başlıkları bulunamadı, sonraki tabloya geçiliyor.")
                        continue

                    # Hedef günün sütun indeksi
                    hedef_sutun = gun_sutun_idx.get(hedef_gun)
                    if hedef_sutun is None:
                        debug_satirlar.append(f"  ⚠️  '{hedef_gun}' sütunu bulunamadı.")
                        continue

                    debug_satirlar.append(f"  🎯 Hedef gün '{hedef_gun}' → sütun {hedef_sutun}")

                    # Veri satırlarını tara
                    for satir in tablo[baslik_satir_idx + 1:]:
                        if not satir or len(satir) < 2:
                            continue

                        # İlk sütun = saat bilgisi
                        ham_saat = str(satir[0] or "").strip()
                        norm_saat = normalize_saat(ham_saat)

                        debug_satirlar.append(f"    Satır saati: '{ham_saat}' → normalize: '{norm_saat}'")

                        # Saat eşleşiyor mu?
                        if norm_saat == hedef_saat or ham_saat == hedef_saat:
                            debug_satirlar.append(f"    🎯 SAAT EŞLEŞTİ: '{hedef_saat}'")
                            if hedef_sutun < len(satir):
                                hucre = str(satir[hedef_sutun] or "")
                                debug_satirlar.append(f"    Hücre içeriği: '{hucre}'")
                                dolu = hucredeki_derslikleri_cikart(hucre)
                                dolu_derslikler.extend(dolu)
                                debug_satirlar.append(f"    Bulunan dolu derslikler: {dolu}")

    except Exception as e:
        debug_satirlar.append(f"❌ Tablo yöntemi hatası: {str(e)}")
        return [], [], debug_satirlar, "hata"

    # Boş derslikleri hesapla
    dolu_set = set(dolu_derslikler)
    bos_derslikler = [d for d in TUM_DERSLIKLER if d not in dolu_set]

    return dolu_derslikler, bos_derslikler, debug_satirlar, "tablo"


def pdf_regex_yontemiyle_isle(pdf_bytes: bytes, hedef_gun: str, hedef_saat: str) -> tuple[list, list, list, str]:
    """
    Ham PDF metninden regex ile derslik bilgisi çıkarmaya çalışır.
    Bu yöntem, tablo algılama başarısız olduğunda devreye girer (yedek yöntem).
    """
    debug_satirlar = ["🔍 Regex yedek yöntemi devreye girdi..."]
    dolu_derslikler = []

    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            tum_metin = ""
            for sayfa in pdf.pages:
                tum_metin += (sayfa.extract_text() or "") + "\n"

        debug_satirlar.append(f"📝 Toplam metin uzunluğu: {len(tum_metin)} karakter")

        if not tum_metin.strip():
            debug_satirlar.append("❌ PDF'den metin çıkarılamadı.")
            return [], list(TUM_DERSLIKLER), debug_satirlar, "bos_metin"

        # Saat bloğunu bul
        saat_baslangic = hedef_saat.split(" - ")[0]  # "09:00"
        saat_bitis = hedef_saat.split(" - ")[1]       # "09:45"

        # Günü ve saati içeren bölümü ara
        # PDF'de her satır bir derslik veya ders bilgisi içerir
        satirlar = tum_metin.split("\n")

        # Gün ve saat sütunlarını konumla
        gun_pozisyon = None
        saat_satirlari = []

        for idx, satir in enumerate(satirlar):
            if hedef_gun in satir:
                gun_pozisyon = idx
                debug_satirlar.append(f"  Gün '{hedef_gun}' satır {idx}'de bulundu: '{satir[:80]}'")

            if saat_baslangic in satir and saat_bitis in satir:
                saat_satirlari.append(idx)
                debug_satirlar.append(f"  Saat '{hedef_saat}' satır {idx}'de bulundu")

        # Yakın satırlarda derslik ara
        if saat_satirlari:
            for saat_idx in saat_satirlari:
                # Saatin çevresindeki 5 satırı tara
                baslangic = max(0, saat_idx - 2)
                bitis = min(len(satirlar), saat_idx + 8)
                bolum = "\n".join(satirlar[baslangic:bitis])
                debug_satirlar.append(f"  Taranan bölüm: '{bolum[:200]}'")
                dolu = hucredeki_derslikleri_cikart(bolum)
                dolu_derslikler.extend(dolu)

        # Sonuçları tekilleştir
        dolu_derslikler = list(set(dolu_derslikler))
        debug_satirlar.append(f"  Regex ile bulunan dolu derslikler: {dolu_derslikler}")

    except Exception as e:
        debug_satirlar.append(f"❌ Regex yöntemi hatası: {str(e)}")
        return [], list(TUM_DERSLIKLER), debug_satirlar, "hata"

    bos_derslikler = [d for d in TUM_DERSLIKLER if d not in set(dolu_derslikler)]
    return dolu_derslikler, bos_derslikler, debug_satirlar, "regex"


def pdf_koordinat_yontemiyle_isle(pdf_bytes: bytes, hedef_gun: str, hedef_saat: str) -> tuple[list, list, list, str]:
    """
    pdfplumber'ın kelime koordinat bilgisini kullanarak derslik tespiti yapar.
    Tablo çizgileri olmayan PDF'ler için gelişmiş yöntem.
    """
    debug_satirlar = ["🗺️  Koordinat tabanlı yöntem devreye girdi..."]
    dolu_derslikler = []

    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            for sayfa_no, sayfa in enumerate(pdf.pages):
                debug_satirlar.append(f"📄 Sayfa {sayfa_no + 1} koordinat analizi...")

                kelimeler = sayfa.extract_words(
                    x_tolerance=5,
                    y_tolerance=5,
                    keep_blank_chars=False,
                    use_text_flow=False,
                )

                if not kelimeler:
                    debug_satirlar.append("  ⚠️  Kelime bulunamadı.")
                    continue

                # Gün ve saat kelimelerinin x,y konumlarını bul
                gun_x = None  # Hedef günün x koordinatı
                saat_y = None  # Hedef saatin y koordinatı
                saat_bitis_y = None  # Sonraki saatin y koordinatı

                gun_kelimeleri = []
                saat_kelimeleri = []

                for kelime in kelimeler:
                    metin = kelime["text"].strip()
                    if hedef_gun in metin or any(g in metin for g in GUNLER):
                        gun_kelimeleri.append(kelime)
                    saat_baslangic = hedef_saat.split(" - ")[0]
                    if saat_baslangic in metin:
                        saat_kelimeleri.append(kelime)

                # Gün sütununun x merkezini belirle
                for k in gun_kelimeleri:
                    if hedef_gun in k["text"]:
                        gun_x = (k["x0"] + k["x1"]) / 2
                        debug_satirlar.append(f"  Gün x konumu: {gun_x:.1f}")
                        break

                # Saat satırının y konumunu belirle
                saat_baslangic_str = hedef_saat.split(" - ")[0]
                saat_bitis_str = hedef_saat.split(" - ")[1]
                y_konumlari = []
                for k in kelimeler:
                    if saat_baslangic_str in k["text"] or saat_bitis_str in k["text"]:
                        y_konumlari.append(k["top"])

                if y_konumlari:
                    saat_y = min(y_konumlari)
                    saat_bitis_y = max(y_konumlari) + 30  # Tahmini hücre yüksekliği
                    debug_satirlar.append(f"  Saat y konumu: {saat_y:.1f} - {saat_bitis_y:.1f}")

                if gun_x is not None and saat_y is not None:
                    # İlgili bölgedeki kelimeleri bul
                    tolerans_x = 60  # Sütun genişliği toleransı
                    tolerans_y = 40  # Satır yüksekliği toleransı

                    bolge_kelimeleri = [
                        k for k in kelimeler
                        if abs((k["x0"] + k["x1"]) / 2 - gun_x) < tolerans_x
                        and saat_y - 5 <= k["top"] <= saat_bitis_y + 5
                    ]

                    bolge_metni = " ".join(k["text"] for k in bolge_kelimeleri)
                    debug_satirlar.append(f"  Bölge metni: '{bolge_metni}'")
                    dolu = hucredeki_derslikleri_cikart(bolge_metni)
                    dolu_derslikler.extend(dolu)
                    debug_satirlar.append(f"  Koordinat yöntemi ile bulunan derslikler: {dolu}")
                else:
                    debug_satirlar.append("  ⚠️  Yeterli koordinat bilgisi bulunamadı.")

    except Exception as e:
        debug_satirlar.append(f"❌ Koordinat yöntemi hatası: {str(e)}")

    dolu_set = set(dolu_derslikler)
    bos_derslikler = [d for d in TUM_DERSLIKLER if d not in dolu_set]
    return dolu_derslikler, bos_derslikler, debug_satirlar, "koordinat"


def derslikleri_bul_tek_saat(pdf_bytes: bytes, hedef_gun: str, hedef_saat: str, tum_yontemleri_dene: bool) -> tuple[list, list, list, str]:
    """
    Belirli bir saat için farklı yöntemleri sırayla deneyerek dolu/boş derslikleri bulur.
    """
    dolu, bos, debug_lines, yontem = pdf_tablo_yontemiyle_isle(pdf_bytes, hedef_gun, hedef_saat)
    tablo_basarili = len(dolu) > 0

    if not tablo_basarili and tum_yontemleri_dene:
        debug_lines.append("─" * 40)
        debug_lines.append(f"ℹ️ {hedef_saat} için tablo yöntemi sonuç vermedi, koordinat yöntemi deneniyor...")
        dolu, bos, debug2, yontem2 = pdf_koordinat_yontemiyle_isle(pdf_bytes, hedef_gun, hedef_saat)
        debug_lines.extend(debug2)
        yontem = "koordinat"

        if not dolu:
            debug_lines.append("─" * 40)
            debug_lines.append(f"ℹ️ {hedef_saat} için koordinat yöntemi sonuç vermedi, regex yöntemi deneniyor...")
            dolu, bos, debug3, yontem3 = pdf_regex_yontemiyle_isle(pdf_bytes, hedef_gun, hedef_saat)
            debug_lines.extend(debug3)
            yontem = "regex"
    else:
        yontem = "tablo"
        
    return dolu, bos, debug_lines, yontem


# ─────────────────────────────────────────────
# ANA UYGULAMA ARAYÜZÜ
# ─────────────────────────────────────────────

# ── Başlık ─────────────────────────────────
st.markdown("""
<div class="hero-card">
    <div style="font-size: 3rem; margin-bottom: 0.5rem;">🏫</div>
    <h1 class="hero-title">Boş Derslik Bulucu</h1>
    <p class="hero-subtitle">Biga İktisadi ve İdari Bilimler Fakültesi · Haftalık Ders Programı Analizi</p>
</div>
""", unsafe_allow_html=True)

# ── Yan Panel (Sidebar) ─────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Filtreler")
    st.markdown("---")

    # PDF yükleme
    st.markdown("**📎 Ders Programı PDF**")
    yuklenen_pdf = st.file_uploader(
        "PDF dosyasını buraya sürükleyin veya tıklayın",
        type=["pdf"],
        help="Haftalık ders programı PDF dosyasını yükleyin",
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Gün seçimi
    st.markdown("**📅 Gün**")
    secilen_gun = st.selectbox(
        "Gün seçin",
        options=GUNLER,
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("**🕐 Saat Dilimi**")
    secilen_saatler = st.multiselect(
        "Saat seçin",
        options=SAATLER,
        default=None,
        label_visibility="collapsed",
        placeholder="Saat(leri) seçin..."
    )

    st.markdown("---")

    # Gelişmiş seçenekler
    with st.expander("🔧 Gelişmiş Seçenekler"):
        debug_modu = st.checkbox("Hata ayıklama günlüğünü göster", value=False)
        tum_yontemleri_dene = st.checkbox(
            "Tüm yöntemleri sırayla dene",
            value=True,
            help="Tablo yöntemi başarısız olursa regex ve koordinat yöntemleri devreye girer.",
        )

    # Sorgula butonu
    st.markdown("---")
    sorgu_butonu = st.button("🔍 Boş Derslikleri Bul", type="primary")

# ── Ana İçerik ──────────────────────────────

if not yuklenen_pdf:
    # Karşılama ekranı
    st.markdown("""
    <div class="info-box">
        <strong>📋 Nasıl Kullanılır?</strong><br>
        1. Sol panelden <strong>haftalık ders programı PDF</strong> dosyasını yükleyin.<br>
        2. Sorgulamak istediğiniz <strong>gün</strong> ve <strong>saat(leri)</strong> seçin.<br>
        3. <strong>"Boş Derslikleri Bul"</strong> butonuna tıklayın.<br>
        4. Sistem PDF'yi analiz ederek seçilen saatlerin tamamında <strong>boş olan derslikleri</strong> yeşil renkte listeler.
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="classroom-card-empty">
            <div style="font-size:2rem;">📄</div>
            <div style="margin-top:0.5rem; font-size:0.85rem;">PDF yükle</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="classroom-card-empty">
            <div style="font-size:2rem;">📅</div>
            <div style="margin-top:0.5rem; font-size:0.85rem;">Gün & Saat seç</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="classroom-card-empty">
            <div style="font-size:2rem;">✅</div>
            <div style="margin-top:0.5rem; font-size:0.85rem;">Sonuçları gör</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        <strong>🏛️ Derslik Listesi (Ana Liste)</strong><br>
        Sistem şu derslikleri takip etmektedir:<br>
        <code>101-108</code> · <code>201-208</code> · <code>B1-B4</code> ·
        <code>Z01, Z02, Z04-Z08</code> · <code>Bilgisayar Lab.</code>
    </div>
    """, unsafe_allow_html=True)

elif not secilen_saatler:
    # Saat seçilmedi dostane uyarı mesajı
    st.markdown("""
    <div class="warning-box">
        ⚠️ <strong>Saat Seçimi Gerekli</strong><br>
        Lütfen sorgulama yapabilmek için sol paneldeki <strong>"Saat Dilimi"</strong> bölümünden en az bir saat dilimi seçin.
    </div>
    """, unsafe_allow_html=True)

else:
    if sorgu_butonu:
        # PDF işleme
        pdf_bytes = yuklenen_pdf.read()
        saatler_label = ", ".join(secilen_saatler)

        with st.spinner(f"⏳ PDF analiz ediliyor: {secilen_gun} · {saatler_label}..."):

            tum_debug = []
            bos_set = set(TUM_DERSLIKLER)
            kullanilan_yontemler = []

            for saat in secilen_saatler:
                dolu_tek, bos_tek, debug_tek, yontem_tek = derslikleri_bul_tek_saat(
                    pdf_bytes, secilen_gun, saat, tum_yontemleri_dene
                )
                tum_debug.append(f"\n⏰ {saat} Dilimi Analiz Sonuçları:")
                tum_debug.extend(debug_tek)
                bos_set = bos_set.intersection(bos_tek)
                kullanilan_yontemler.append(f"{saat}: {yontem_tek}")

            # Dolu derslikler, genel derslik listesinde olup boş olmayanlardır.
            dolu = [d for d in TUM_DERSLIKLER if d not in bos_set]
            bos = sorted(list(bos_set))
            dolu = sorted(list(dolu))
            kullanilan_yontem = ", ".join(kullanilan_yontemler)

        # ── Sonuçları session_state'e kaydet ──────────
        st.session_state.sonuc_dolu = dolu
        st.session_state.sonuc_bos = bos
        st.session_state.sonuc_debug = tum_debug
        st.session_state.sonuc_yontem = kullanilan_yontem
        st.session_state.sonuc_gun = secilen_gun
        st.session_state.sonuc_saat = ", ".join(secilen_saatler)
        st.session_state.sonuc_pdf_adi = yuklenen_pdf.name

    elif yuklenen_pdf and not sorgu_butonu:
        # Gün/saat/PDF değişip değişmediğini kontrol et — değiştiyse sonuçları temizle
        pdf_degisti = (st.session_state.sonuc_pdf_adi != "" and
                       st.session_state.sonuc_pdf_adi != yuklenen_pdf.name)
        if pdf_degisti:
            st.session_state.sonuc_dolu = None
            st.session_state.sonuc_bos = None
            st.session_state.sonuc_debug = []
            st.session_state.sonuc_yontem = ""
            st.session_state.sonuc_gun = ""
            st.session_state.sonuc_saat = ""
            st.session_state.sonuc_pdf_adi = ""

    # ── Sonuçları Göster (session_state'den) ──────────────────────────
    if st.session_state.sonuc_dolu is not None and yuklenen_pdf is not None:
        dolu = st.session_state.sonuc_dolu
        bos = st.session_state.sonuc_bos
        tum_debug = st.session_state.sonuc_debug
        kullanilan_yontem = st.session_state.sonuc_yontem
        gosterilen_gun = st.session_state.sonuc_gun
        gosterilen_saat = st.session_state.sonuc_saat

        # Özet başlık
        st.markdown(f"""
        <div class="result-header">
            <h3>📊 Sorgu Sonucu</h3>
            <p>
                <span class="stat-badge stat-empty">✅ {len(bos)} Boş Derslik</span>
                <span class="stat-badge stat-occupied">🔴 {len(dolu)} Dolu Derslik</span>
                &nbsp;|&nbsp; Gün: <strong style="color:#60a5fa">{gosterilen_gun}</strong>
                &nbsp;|&nbsp; Saat: <strong style="color:#60a5fa">{gosterilen_saat}</strong>
                &nbsp;|&nbsp; Yöntem: <strong style="color:#94a3b8">{kullanilan_yontem}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)

        if not dolu and not bos:
            st.markdown("""
            <div class="warning-box">
                ⚠️ <strong>Veri çıkarılamadı.</strong> Lütfen aşağıdaki önerileri deneyin:<br>
                &bull; PDF'nin metin tabanlı (taranmış değil) olduğundan emin olun.<br>
                &bull; Farklı bir gün veya saat seçin.<br>
                &bull; Hata ayıklama günlüğünü açarak detayları inceleyin.
            </div>
            """, unsafe_allow_html=True)

        elif bos:
            # Boş derslikler
            st.markdown(f"""
            <div class="success-box">
                ✅ <strong>{gosterilen_gun} günü {gosterilen_saat} saatlerinde {len(bos)} boş derslik bulundu.</strong>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 🟢 Boş Derslikler")

            # Derslik kartlarını ızgara düzeninde göster
            sutun_sayisi = 6
            satirlar = [bos[i:i + sutun_sayisi] for i in range(0, len(bos), sutun_sayisi)]
            for satir in satirlar:
                kolonlar = st.columns(sutun_sayisi)
                for idx, derslik in enumerate(satir):
                    with kolonlar[idx]:
                        st.markdown(f"""
                        <div class="classroom-card-empty">
                            <div style="font-size:1.5rem;">🎓</div>
                            <div style="margin-top:0.4rem;">{derslik}</div>
                        </div>
                        """, unsafe_allow_html=True)

        else:
            st.markdown(f"""
            <div class="warning-box">
                ⚠️ Seçilen gün ve saatlerde tüm derslikler dolu görünüyor veya veri yetersiz.
            </div>
            """, unsafe_allow_html=True)

        # Dolu derslikler (ikincil bilgi)
        if dolu:
            with st.expander(f"🔴 Dolu Derslikler ({len(dolu)} adet)"):
                sutun_sayisi = 6
                satirlar = [dolu[i:i + sutun_sayisi] for i in range(0, len(dolu), sutun_sayisi)]
                for satir in satirlar:
                    kolonlar = st.columns(sutun_sayisi)
                    for idx, derslik in enumerate(satir):
                        with kolonlar[idx]:
                            st.markdown(f"""
                            <div class="classroom-card-occupied">
                                <div>❌</div>
                                <div style="margin-top:0.3rem; font-size:0.85rem;">{derslik}</div>
                            </div>
                            """, unsafe_allow_html=True)

        # Hata ayıklama günlüğü
        if debug_modu and tum_debug:
            with st.expander("🔧 Hata Ayıklama Günlüğü"):
                log_metni = "\n".join(tum_debug)
                st.markdown(f'<div class="debug-area">{log_metni}</div>', unsafe_allow_html=True)

    elif yuklenen_pdf and st.session_state.sonuc_dolu is None:
        # PDF yüklendi ama henüz sorgu yapılmadı
        dosya_bilgisi = f"{yuklenen_pdf.name} ({yuklenen_pdf.size / 1024:.1f} KB)"
        st.markdown(f"""
        <div class="success-box">
            📎 PDF hazır: <strong>{dosya_bilgisi}</strong><br>
            Gün ve saat seçtikten sonra <strong>"Boş Derslikleri Bul"</strong> butonuna tıklayın.
        </div>
        """, unsafe_allow_html=True)

        # Seçili filtreler özeti
        saatler_str = ", ".join(secilen_saatler)
        st.markdown(f"""
        <div class="info-box">
            Seçili filtreler: <strong style="color:#60a5fa">{secilen_gun}</strong> ·
            <strong style="color:#60a5fa">{saatler_str}</strong>
        </div>
        """, unsafe_allow_html=True)

# ── Alt Bilgi ───────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#475569; font-size:0.78rem; padding:0.5rem 0;">
    Çanakkale Onsekiz Mart Üniversitesi · Biga İİBF · Boş Derslik Bulucu v2.0
</div>
""", unsafe_allow_html=True)

