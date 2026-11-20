import math
import time
import streamlit as st

# Konfigurasi Halaman
st.set_page_config(
    page_title="Sistem Pakar Diagnosis DBD - CBR Cosine Similarity",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ================= DATA & BASIS KASUS =================
GEJALA = [
    {"id": "G1", "name": "Demam"},
    {"id": "G2", "name": "Mual"},
    {"id": "G3", "name": "Muntah"},
    {"id": "G4", "name": "Lemas"},
    {"id": "G5", "name": "Mencret"},
    {"id": "G6", "name": "Kejang"},
    {"id": "G7", "name": "Tenggorokan Sakit"},
    {"id": "G8", "name": "Bintik Merah"},
    {"id": "G9", "name": "Mimisan"},
    {"id": "G10", "name": "Nyeri Sendi"},
    {"id": "G11", "name": "Pusing"},
    {"id": "G12", "name": "Leukosit Turun / Abnormal"},
    {"id": "G13", "name": "Hematokrit Meningkat"},
    {"id": "G14", "name": "Trombosit Turun (<100.000 / mm³)"},
]

GEJALA_IDS = [g["id"] for g in GEJALA]

CASE_BASE = [
    {
        "id": "Kasus 1",
        "grade": "I",
        "disease": "Demam Berdarah Grade I (DHF-I)",
        "gejala": ["G1", "G8", "G12", "G13", "G14"],
        "description": (
            "Demam Dengue Grade I (Uji Tourniquet Positif / Bintik Merah tanpa "
            "perdarahan spontan)."
        ),
        "solution": (
            "Tirah baring (bed rest), minum air putih minimal 2 liter/hari, "
            "konsumsi paracetamol untuk demam (hindari ibuprofen/aspirin), dan "
            "pantau trombosit harian di faskes primer."
        ),
    },
    {
        "id": "Kasus 2",
        "grade": "II",
        "disease": "Demam Berdarah Grade II (DHF-II)",
        "gejala": ["G1", "G8", "G9", "G12", "G13", "G14"],
        "description": (
            "Demam Dengue Grade II (Disertai perdarahan spontan seperti "
            "mimisan/gusi berdarah/bintik merah rapat)."
        ),
        "solution": (
            "Segera konsultasi ke fasilitas kesehatan/RS, pemberian cairan infus "
            "kristaloid jika ada tanda dehidrasi, pengawasan ketat kadar trombosit "
            "dan hematokrit setiap 12 jam."
        ),
    },
    {
        "id": "Kasus 3",
        "grade": "III",
        "disease": "Demam Berdarah Grade III (DHF-III)",
        "gejala": ["G1", "G8", "G9", "G10", "G12", "G13", "G14"],
        "description": (
            "Demam Dengue Grade III (Kondisi Kegawatdaruratan / Dengue Shock "
            "Syndrome awal dengan nadi cepat & lemah, akral dingin)."
        ),
        "solution": (
            "SEGERA KE IGD RUMAH SAKIT. Membutuhkan resusitasi cairan intravena "
            "cepat dan pemantauan ketat di ruang rawat inap/ICU."
        ),
    },
    {
        "id": "Kasus 4",
        "grade": "IV",
        "disease": "Demam Berdarah Grade IV (DHF-IV)",
        "gejala": ["G1", "G6", "G10", "G12", "G13", "G14"],
        "description": (
            "Demam Dengue Grade IV (Profound Shock / Syok Berat, tekanan darah "
            "tidak terukur dan nadi tidak teraba)."
        ),
        "solution": (
            "EMERGENCY / DARURAT MEDIS TINGGI. Rujukan langsung ke ICU, penanganan "
            "syok berat, bantuan oksigenasi, dan penanganan komplikasi pendarahan "
            "organ dalam."
        ),
    },
]

GRADE_THEME = {
    "I": {
        "banner": "linear-gradient(135deg, #0a9c8a 0%, #0c7c70 60%, #0e514b 100%)",
        "pill_bg": "#059669",
        "bar": "#ffffff",
        "status_label": "Tingkat Risiko Ringan – Sedang",
    },
    "II": {
        "banner": "linear-gradient(135deg, #f59e0b 0%, #ea580c 60%, #c2410c 100%)",
        "pill_bg": "#c2410c",
        "bar": "#ffffff",
        "status_label": "Perlu Pengawasan Medis Ketat",
    },
    "III": {
        "banner": "linear-gradient(135deg, #ef4444 0%, #dc2626 55%, #991b1b 100%)",
        "pill_bg": "#991b1b",
        "bar": "#ffffff",
        "status_label": "Kegawatdaruratan Awal (Pre-Shock)",
    },
    "IV": {
        "banner": "linear-gradient(135deg, #7f1d1d 0%, #b91c1c 50%, #450a0a 100%)",
        "pill_bg": "#0f172a",
        "bar": "#fca5a5",
        "status_label": "Darurat Medis Tinggi (Profound Shock)",
    },
}

# ================= FUNGSI PERHITUNGAN (MATH ONLY) =================
def build_vector(gejala_ids):
    return [1 if gid in gejala_ids else 0 for gid in GEJALA_IDS]


def dot_product(x, y):
    return sum(a * b for a, b in zip(x, y))


def norm(vector):
    return math.sqrt(sum(v * v for v in vector))


# ================= STATE & CALLBACKS =================
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "Beranda"

if "show_creator" not in st.session_state:
    st.session_state.show_creator = False

if "step" not in st.session_state:
    st.session_state.step = 1

if "pasien" not in st.session_state:
    st.session_state.pasien = {
        "nama": "",
        "usia": 20,
        "jenis_kelamin": "Laki-laki",
        "alamat": "",
    }

if "diagnosed_gejala" not in st.session_state:
    st.session_state.diagnosed_gejala = None

if "diagnosis_count" not in st.session_state:
    st.session_state.diagnosis_count = 0

if "trigger_loading" not in st.session_state:
    st.session_state.trigger_loading = False


def set_menu(menu_name):
    st.session_state.active_menu = menu_name


def toggle_creator():
    st.session_state.show_creator = not st.session_state.show_creator


def ke_step_identitas():
    st.session_state.step = 1


def mulai_diagnosis():
    st.session_state.diagnosed_gejala = [
        g["id"] for g in GEJALA if st.session_state.get(f"chk_{g['id']}", False)
    ]
    st.session_state.diagnosis_count += 1
    st.session_state.trigger_loading = True


def reset_gejala():
    for g in GEJALA:
        st.session_state[f"chk_{g['id']}"] = False
    st.session_state.diagnosed_gejala = None
    st.session_state.diagnosis_count = 0
    st.session_state.trigger_loading = False


def reset_semua():
    reset_gejala()
    st.session_state.pasien = {
        "nama": "",
        "usia": 20,
        "jenis_kelamin": "Laki-laki",
        "alamat": "",
    }
    st.session_state.step = 1


# ================= CUSTOM DESIGN SYSTEM CSS =================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        --primary-600: #1b6ef5;
        --primary-700: #1457e1;
        --primary-900: #142857;
        --teal-600: #0a9c8a;
        --teal-700: #0c7c70;
        --surface-bg: #f4f7fb;
        --card-bg: #ffffff;
        --border-subtle: #e2e8f0;
        --text-main: #0f172a;
        --text-muted: #64748b;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
        scroll-behavior: smooth;
    }

    .stApp {
        background-color: var(--surface-bg);
        color: var(--text-main);
    }

    header[data-testid="stHeader"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    .block-container {
        max-width: 1120px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 3.5rem !important;
    }

    /* ================= KEYFRAMES ANIMATIONS ================= */
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-10px) scale(0.985); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    @keyframes floatOrb {
        0%, 100% { transform: translate(0, 0) scale(1); }
        50% { transform: translate(14px, -16px) scale(1.08); }
    }

    @keyframes fillBar {
        from { width: 0%; }
    }

    @keyframes popIn {
        0% { opacity: 0; transform: scale(0.75); }
        70% { transform: scale(1.07); }
        100% { opacity: 1; transform: scale(1); }
    }

    @keyframes spinLoader {
        to { transform: rotate(360deg); }
    }

    @keyframes shakeError {
        0%, 100% { transform: translateX(0); }
        20%, 60% { transform: translateX(-6px); }
        40%, 80% { transform: translateX(6px); }
    }

    /* ================= CARD CONTAINER STREAMLIT ================= */
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .nav-brand),
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"][style*="border"] {
        background-color: var(--card-bg) !important;
        border: 1px solid rgba(226, 232, 240, 0.75) !important;
        border-radius: 1.35rem !important;
        padding: 1.35rem 1.5rem !important;
        box-shadow: 0 4px 20px -6px rgba(15, 23, 42, 0.05) !important;
        transition: box-shadow 0.25s ease, border-color 0.25s ease !important;
    }

    /* Hilangkan border ganda bawaan Emotion CSS Streamlit versi terbaru di dalam container */
    div[data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"] {
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }

    /* ================= TOP NAVIGATION BAR (SEJAJAR & RAPAT) ================= */
    .nav-brand {
        font-size: 1.05rem;
        font-weight: 800;
        color: var(--primary-900);
        display: flex;
        align-items: center;
        gap: 0.65rem;
        min-height: 36px;
        letter-spacing: -0.01em;
    }
    .nav-logo-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        flex-shrink: 0;
        border-radius: 0.65rem;
        background: linear-gradient(135deg, #1b6ef5, #0a9c8a);
        color: #ffffff;
        font-size: 1rem;
        box-shadow: 0 4px 10px -2px rgba(27, 110, 245, 0.4);
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type div.stButton > button,
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .nav-brand) div.stButton > button {
        height: 36px !important;
        min-height: 36px !important;
        max-height: 36px !important;
        padding: 0 1rem !important;
        font-size: 0.86rem !important;
        border-radius: 0.7rem !important;
        white-space: nowrap !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* ================= FIELD INPUT (100% IDENTIK & SINGLE BORDER) ================= */
    [data-testid="stTextInput"] label p,
    [data-testid="stNumberInput"] label p,
    [data-testid="stSelectbox"] label p {
        color: #1e293b !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        margin-bottom: 0.3rem !important;
    }

    [data-testid="stTextInput"] [data-baseweb="input"],
    [data-testid="stNumberInputContainer"] {
        background-color: #f8fafc !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 0.85rem !important;
        min-height: 44px !important;
        height: 44px !important;
        overflow: hidden !important;
        box-shadow: none !important;
        outline: none !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stTextInput"] [data-baseweb="input"]:hover,
    [data-testid="stNumberInputContainer"]:hover {
        border-color: #94a3b8 !important;
    }

    [data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
    [data-testid="stNumberInputContainer"]:focus-within {
        background-color: #ffffff !important;
        border-color: var(--primary-600) !important;
        box-shadow: 0 0 0 3px rgba(27, 110, 245, 0.15) !important;
        outline: none !important;
    }

    [data-testid="stNumberInputContainer"] *,
    [data-testid="stTextInput"] [data-baseweb="input"] * {
        border-radius: 0 !important;
        box-shadow: none !important;
        outline: none !important;
    }

    [data-testid="stNumberInputContainer"] [data-baseweb="input"],
    [data-testid="stNumberInputContainer"] [data-baseweb="base-input"],
    [data-testid="stNumberInputContainer"] [data-baseweb="base-input"] > div,
    [data-testid="stTextInput"] [data-baseweb="base-input"],
    [data-testid="stTextInput"] [data-baseweb="base-input"] > div {
        background-color: transparent !important;
        border: none !important;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input {
        background-color: transparent !important;
        color: #0f172a !important;
        border: none !important;
        padding: 0 0.9rem !important;
        height: 100% !important;
        font-size: 0.92rem !important;
        caret-color: #1b6ef5 !important;
    }

    [data-testid="stTextInput"] input::placeholder {
        color: #94a3b8 !important;
        opacity: 1 !important;
    }

    [data-testid="stNumberInputContainer"] > div:last-child {
        background-color: #f1f5f9 !important;
        border: none !important;
        border-left: 1px solid #cbd5e1 !important;
        display: flex !important;
        align-items: center !important;
    }
    [data-testid="stNumberInputContainer"] button {
        background-color: transparent !important;
        color: #334155 !important;
        border: none !important;
        height: 100% !important;
    }
    [data-testid="stNumberInputContainer"] button:hover {
        background-color: #e2e8f0 !important;
        color: #0f172a !important;
    }
    [data-testid="stNumberInputContainer"] button svg {
        fill: #334155 !important;
    }

    /* Selectbox (Jenis Kelamin) */
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 0.85rem !important;
        min-height: 44px !important;
        height: auto !important;
        padding-top: 0.15rem !important;
        padding-bottom: 0.15rem !important;
        display: flex !important;
        align-items: center !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div:hover {
        border-color: #94a3b8 !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {
        border-color: var(--primary-600) !important;
        background-color: #ffffff !important;
        box-shadow: 0 0 0 3px rgba(27, 110, 245, 0.15) !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] span,
    [data-testid="stSelectbox"] [data-baseweb="select"] div {
        color: #0f172a !important;
        font-size: 0.92rem !important;
        line-height: 1.4 !important;
        overflow: visible !important;
    }
    ul[role="listbox"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 0.75rem !important;
    }
    ul[role="listbox"] li {
        color: #0f172a !important;
    }
    ul[role="listbox"] li:hover,
    ul[role="listbox"] li[aria-selected="true"] {
        background-color: #eff6ff !important;
        color: #1d4ed8 !important;
    }
    [data-testid="stSelectbox"] svg {
        fill: #334155 !important;
    }

    /* ================= HERO BANNER ================= */
    .hero-banner {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #16377d 0%, #1747b6 48%, #0a8778 100%);
        color: #ffffff;
        border-radius: 1.5rem;
        padding: 2.6rem 2.4rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 18px 36px -14px rgba(20, 40, 87, 0.38);
        animation: fadeUp 0.55s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .hero-banner::before {
        content: "";
        position: absolute;
        top: -70px;
        right: -50px;
        width: 250px;
        height: 250px;
        border-radius: 9999px;
        background: radial-gradient(circle, rgba(94, 234, 212, 0.3) 0%, transparent 70%);
        pointer-events: none;
        animation: floatOrb 6s ease-in-out infinite;
    }
    .hero-banner::after {
        content: "";
        position: absolute;
        bottom: -85px;
        left: -45px;
        width: 230px;
        height: 230px;
        border-radius: 9999px;
        background: radial-gradient(circle, rgba(142, 205, 255, 0.24) 0%, transparent 70%);
        pointer-events: none;
        animation: floatOrb 7.5s ease-in-out infinite reverse;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        border: 1px solid rgba(255,255,255,0.28);
        background: rgba(255,255,255,0.14);
        padding: 0.35rem 0.9rem;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 600;
        color: #ccfbf1;
        margin-bottom: 0.95rem;
        backdrop-filter: blur(6px);
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.25;
        margin: 0;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        display: block;
        color: #5eead4;
        margin-top: 0.15rem;
    }
    .hero-desc {
        margin-top: 0.9rem;
        font-size: 0.96rem;
        line-height: 1.65;
        color: #e0f2fe;
        max-width: 820px;
    }
    .hero-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem;
        margin-top: 1.4rem;
    }
    .hero-pill {
        background: rgba(255,255,255,0.13);
        border: 1px solid rgba(255,255,255,0.24);
        padding: 0.4rem 0.85rem;
        border-radius: 0.6rem;
        font-size: 0.8rem;
        font-weight: 500;
        transition: all 0.25s ease;
    }
    .hero-pill:hover {
        background: rgba(255,255,255,0.24);
        transform: translateY(-2px);
    }

    /* ================= CARD CARA KERJA + ::after ================= */
    .how-card {
        position: relative;
        overflow: hidden;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 1.25rem;
        padding: 1.4rem;
        height: 100%;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .how-card::after {
        content: "";
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #1b6ef5, #0a9c8a);
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .how-card:hover {
        background: #ffffff;
        transform: translateY(-5px);
        border-color: #bce0ff;
        box-shadow: 0 14px 28px -10px rgba(27, 110, 245, 0.2);
    }
    .how-card:hover::after {
        transform: scaleX(1);
    }
    .how-step-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 2.2rem;
        height: 2.2rem;
        border-radius: 0.7rem;
        background: #dbeafe;
        color: #1d4ed8;
        font-weight: 800;
        font-size: 0.92rem;
        margin-bottom: 0.85rem;
        transition: all 0.3s ease;
    }
    .how-card:hover .how-step-num {
        background: linear-gradient(135deg, #1b6ef5, #0a9c8a);
        color: #ffffff;
        transform: rotate(-6deg) scale(1.08);
    }

    /* ================= CARD IDENTITAS PEMBUAT ================= */
    .creator-card {
        background: linear-gradient(135deg, #f8fafc 0%, #eef7ff 100%);
        border: 1px solid #cbd5e1;
        border-left: 5px solid #1b6ef5;
        border-radius: 1.15rem;
        padding: 1.4rem 1.6rem;
        margin-top: 0.85rem;
        animation: slideDown 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        transition: all 0.25s ease;
    }
    .creator-card:hover {
        transform: translateY(-2px);
        border-left-color: #0a9c8a;
        box-shadow: 0 12px 24px -10px rgba(15, 23, 42, 0.1);
    }

    /* Sejajarkan tombol Tampilkan/Sembunyikan Profil mentok kanan lurus dengan card profil */
    div[data-testid="stHorizontalBlock"]:has(.creator-header-anchor) {
        gap: 0 !important;
        justify-content: space-between !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.creator-header-anchor) > div[data-testid="stColumn"]:last-child {
        display: flex !important;
        justify-content: flex-end !important;
        padding-right: 0 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.creator-header-anchor) > div[data-testid="stColumn"]:last-child div.stButton {
        width: 225px !important;
        max-width: 100% !important;
    }

    /* ================= STEPPER INDICATOR ================= */
    .stepper-bar {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin-bottom: 1.25rem;
        padding: 0.9rem 1.35rem;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 1.1rem;
        box-shadow: 0 2px 10px -4px rgba(15, 23, 42, 0.04);
        animation: fadeUp 0.4s ease;
    }
    .step-badge-active {
        background: linear-gradient(135deg, #1b6ef5, #1457e1);
        color: #ffffff;
        padding: 0.38rem 0.95rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        box-shadow: 0 4px 12px -4px rgba(27, 110, 245, 0.5);
    }
    .step-badge-done {
        background: #0a9c8a;
        color: #ffffff;
        padding: 0.38rem 0.95rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .step-badge-inactive {
        background: #f1f5f9;
        color: #64748b;
        padding: 0.38rem 0.95rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* ================= KARTU RINGKASAN IDENTITAS PASIEN ================= */
    .patient-summary-card {
        background: linear-gradient(135deg, #eef7ff 0%, #edfdfa 100%);
        border: 1px solid #bae6fd;
        border-left: 5px solid #0a9c8a;
        border-radius: 1.1rem;
        padding: 1.05rem 1.35rem;
        animation: fadeUp 0.4s ease;
        transition: all 0.25s ease;
    }
    .patient-summary-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px -8px rgba(10, 156, 138, 0.22);
    }

    /* ================= KARTU GEJALA SERAGAM + KOTAK CHECKBOX HIJAU ================= */
    div[data-testid="stCheckbox"] {
        position: relative;
        overflow: hidden;
        background-color: #f8fafc;
        border: 1.5px solid #e2e8f0;
        border-radius: 0.95rem;
        padding: 0.75rem 0.95rem;
        min-height: 68px;
        display: flex;
        align-items: center;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div[data-testid="stCheckbox"]::after {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: #0a9c8a;
        transform: scaleY(0);
        transition: transform 0.2s ease;
    }
    div[data-testid="stCheckbox"]:hover {
        border-color: #7dd3fc;
        background-color: #f0f9ff;
        transform: translateY(-3px);
        box-shadow: 0 10px 20px -8px rgba(27, 110, 245, 0.28);
    }
    div[data-testid="stCheckbox"]:has(input:checked) {
        border-color: #0a9c8a;
        background-color: #ecfdf5;
        box-shadow: 0 6px 16px -8px rgba(10, 156, 138, 0.4);
    }
    div[data-testid="stCheckbox"]:has(input:checked)::after {
        transform: scaleY(1);
    }

    div[data-testid="stCheckbox"] label > span:first-of-type {
        background-color: #f8fafc !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 0.35rem !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stCheckbox"]:hover label > span:first-of-type {
        border-color: #0a9c8a !important;
        background-color: #ffffff !important;
    }
    div[data-testid="stCheckbox"]:has(input:checked) label > span:first-of-type {
        background-color: #0a9c8a !important;
        border-color: #0a9c8a !important;
    }
    div[data-testid="stCheckbox"]:has(input:checked) label > span:first-of-type svg {
        fill: #ffffff !important;
        color: #ffffff !important;
    }

    div[data-testid="stCheckbox"] label p {
        font-size: 0.86rem !important;
        font-weight: 500 !important;
        line-height: 1.35 !important;
        color: #1e293b !important;
    }

    /* ================= TOMBOL UTAMA & SEKUNDER ================= */
    div.stButton > button[kind="primary"] {
        width: 100%;
        border-radius: 0.95rem !important;
        border: none !important;
        padding: 0.68rem 1.4rem !important;
        font-weight: 600 !important;
        font-size: 0.94rem !important;
        color: #ffffff !important;
        background: linear-gradient(135deg, #1b6ef5 0%, #1457e1 52%, #0a9c8a 100%) !important;
        box-shadow: 0 10px 22px -10px rgba(20, 87, 225, 0.65) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 28px -10px rgba(20, 87, 225, 0.78) !important;
        filter: brightness(1.06);
    }
    div.stButton > button[kind="primary"]:active {
        transform: translateY(0) scale(0.99);
    }

    div.stButton > button[kind="secondary"] {
        width: 100%;
        border-radius: 0.95rem !important;
        border: 1.5px solid #cbd5e1 !important;
        padding: 0.65rem 1.15rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        background-color: #ffffff !important;
        color: #334155 !important;
        transition: all 0.22s ease !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        transform: translateY(-2px);
        border-color: #60a5fa !important;
        background-color: #eff6ff !important;
        color: #1d4ed8 !important;
        box-shadow: 0 8px 18px -8px rgba(29, 78, 216, 0.22) !important;
    }

    /* Tombol CTA Mulai Diagnosis (Sedikit digeser ke kanan) */
    div[data-testid="stHorizontalBlock"]:has(.cta-center-anchor) {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        padding-left: 2.5rem !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.cta-center-anchor) > div[data-testid="stColumn"] {
        width: 280px !important;
        max-width: 100% !important;
        flex: 0 0 auto !important;
    }

    /* Counter Pill */
    .counter-pill {
        display: inline-block;
        background-color: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        padding: 0.42rem 1rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
    }

    /* ================= ALERT LOADING, ERROR, & SUCCESS ================= */
    .loading-card {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.85rem;
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1e40af;
        border-radius: 1rem;
        padding: 1.15rem 1.5rem;
        margin-top: 1rem;
        font-weight: 600;
        font-size: 0.92rem;
        animation: fadeUp 0.3s ease;
    }
    .spinner-ring {
        width: 1.35rem;
        height: 1.35rem;
        border: 3px solid #bfdbfe;
        border-top-color: #1b6ef5;
        border-radius: 9999px;
        animation: spinLoader 0.75s linear infinite;
    }

    .error-alert {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-left: 5px solid #dc2626;
        color: #991b1b;
        border-radius: 0.95rem;
        padding: 0.95rem 1.25rem;
        margin-top: 1rem;
        font-size: 0.9rem;
        font-weight: 600;
        animation: shakeError 0.4s ease;
    }

    .success-alert {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        border-left: 5px solid #059669;
        color: #065f46;
        border-radius: 0.95rem;
        padding: 0.85rem 1.25rem;
        margin-bottom: 1rem;
        font-size: 0.88rem;
        font-weight: 600;
        animation: slideDown 0.35s ease;
    }

    /* ================= HASIL DIAGNOSIS ================= */
    .result-wrapper {
        animation: fadeUp 0.55s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .result-banner {
        position: relative;
        overflow: hidden;
        border-radius: 1.25rem;
        padding: 1.85rem 2rem;
        color: #ffffff;
    }
    .result-banner::after {
        content: "";
        position: absolute;
        top: -50px;
        right: -50px;
        width: 210px;
        height: 210px;
        border-radius: 9999px;
        background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
        pointer-events: none;
    }
    .progress-track {
        width: 100%;
        height: 0.8rem;
        background: rgba(255,255,255,0.25);
        border-radius: 9999px;
        overflow: hidden;
        margin-top: 0.65rem;
    }
    .progress-fill {
        height: 100%;
        border-radius: 9999px;
        animation: fillBar 1.1s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .info-card-teal {
        background: #f0fdfa;
        border: 1px solid #ccfbf1;
        border-radius: 1.15rem;
        padding: 1.4rem;
        height: 100%;
        animation: fadeUp 0.65s cubic-bezier(0.16, 1, 0.3, 1);
        transition: all 0.25s ease;
    }
    .info-card-teal:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 24px -10px rgba(10, 156, 138, 0.22);
    }

    .info-card-blue {
        background: #eff6ff;
        border: 1px solid #dbeafe;
        border-radius: 1.15rem;
        padding: 1.4rem;
        height: 100%;
        animation: fadeUp 0.75s cubic-bezier(0.16, 1, 0.3, 1);
        transition: all 0.25s ease;
    }
    .info-card-blue:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 24px -10px rgba(27, 110, 245, 0.22);
    }

    .rank-item {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .rank-item:hover {
        transform: translateX(4px);
    }

    .chip-gejala {
        display: inline-block;
        background-color: #0a9c8a;
        color: #ffffff;
        padding: 0.3rem 0.7rem;
        border-radius: 0.55rem;
        font-size: 0.76rem;
        font-weight: 600;
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
        animation: popIn 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        transition: transform 0.2s ease, background-color 0.2s ease;
    }
    .chip-gejala:hover {
        transform: scale(1.07);
        background-color: #0c7c70;
    }

    /* Disclaimer */
    .disclaimer-box {
        border-radius: 1.25rem;
        border: 1px solid #fde68a;
        border-left: 5px solid #f59e0b;
        background-color: #fffbeb;
        padding: 1.25rem 1.5rem;
        color: #78350f;
        font-size: 0.875rem;
        line-height: 1.65;
        animation: fadeUp 0.6s ease;
        transition: all 0.25s ease;
    }
    .disclaimer-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -10px rgba(217, 119, 6, 0.2);
    }

    /* ================= RESPONSIVITAS MOBILE (<= 768px) ================= */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.85rem !important;
            padding-right: 0.85rem !important;
            padding-top: 1rem !important;
            padding-bottom: 2.2rem !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .nav-brand),
        div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"][style*="border"] {
            padding: 1rem 1rem !important;
            border-radius: 1.1rem !important;
        }

        /* Navbar Mobile: tombol Beranda & Diagnosis tetap sejajar berdampingan 50%-50% */
        div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type div[data-testid="stHorizontalBlock"],
        div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .nav-brand) div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.5rem !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child,
        div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .nav-brand) div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child {
            width: 100% !important;
            flex: 1 1 100% !important;
            margin-bottom: 0.25rem !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2),
        div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .nav-brand) div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) {
            display: none !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3),
        div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(4),
        div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .nav-brand) div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3),
        div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .nav-brand) div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(4) {
            width: calc(50% - 0.25rem) !important;
            flex: 1 1 calc(50% - 0.25rem) !important;
        }

        .nav-brand {
            font-size: 0.95rem;
        }
        .nav-brand span span {
            display: none;
        }

        /* Hero Banner Mobile */
        .hero-banner {
            padding: 1.65rem 1.25rem;
            border-radius: 1.2rem;
        }
        .hero-title {
            font-size: 1.42rem;
            line-height: 1.3;
        }
        .hero-desc {
            font-size: 0.88rem;
            line-height: 1.55;
        }
        .hero-pills {
            gap: 0.45rem;
            margin-top: 1rem;
        }
        .hero-pill {
            font-size: 0.74rem;
            padding: 0.32rem 0.65rem;
        }

        /* How Card Mobile */
        .how-card {
            padding: 1.1rem;
            margin-bottom: 0.6rem;
        }

        /* CTA Center di Mobile */
        div[data-testid="stHorizontalBlock"]:has(.cta-center-anchor) {
            padding-left: 0 !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.cta-center-anchor) > div[data-testid="stColumn"] {
            width: 100% !important;
        }

        /* Tombol Profil di Mobile */
        div[data-testid="stHorizontalBlock"]:has(.creator-header-anchor) > div[data-testid="stColumn"]:last-child div.stButton {
            width: 100% !important;
        }

        /* Stepper Mobile */
        .stepper-bar {
            padding: 0.75rem 0.95rem;
            gap: 0.45rem;
        }
        .step-badge-active,
        .step-badge-done,
        .step-badge-inactive {
            font-size: 0.74rem;
            padding: 0.32rem 0.75rem;
        }

        /* Checkbox Gejala Mobile: 2 kolom rapi agar tidak terlalu panjang */
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stCheckbox"]) {
            flex-wrap: wrap !important;
            gap: 0.5rem !important;
        }
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stCheckbox"]) > div[data-testid="stColumn"] {
            width: calc(50% - 0.25rem) !important;
            flex: 1 1 calc(50% - 0.25rem) !important;
        }
        div[data-testid="stCheckbox"] {
            padding: 0.6rem 0.65rem;
            min-height: 60px;
        }
        div[data-testid="stCheckbox"] label p {
            font-size: 0.78rem !important;
        }

        /* Result Banner Mobile */
        .result-banner {
            padding: 1.35rem 1.15rem;
        }
        .result-banner h2 {
            font-size: 1.15rem !important;
        }
        .info-card-teal,
        .info-card-blue {
            padding: 1.1rem;
            margin-bottom: 0.6rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ================= TOP NAVIGATION BAR =================
with st.container(border=True):
    nav_brand, nav_spacer, nav_btn1, nav_btn2 = st.columns(
        [4.2, 1.0, 1.1, 1.1],
        gap="small",
        vertical_alignment="center",
    )
    with nav_brand:
        st.markdown(
            '<div class="nav-brand">'
            '<span class="nav-logo-badge">✚</span>'
            '<span>Sistem Pakar DBD <span style="color:#64748b; font-weight:500;">• CBR Cosine Similarity</span></span>'
            '</div>',
            unsafe_allow_html=True,
        )
    with nav_btn1:
        st.button(
            "Beranda",
            type="primary" if st.session_state.active_menu == "Beranda" else "secondary",
            on_click=set_menu,
            args=("Beranda",),
        )
    with nav_btn2:
        st.button(
            "Diagnosis",
            type="primary" if st.session_state.active_menu == "Diagnosis" else "secondary",
            on_click=set_menu,
            args=("Diagnosis",),
        )

st.write("")

# ==============================================================================
# MENU 1: BERANDA
# ==============================================================================
if st.session_state.active_menu == "Beranda":
    # 1. Card Judul & Deskripsi Sistem
    st.markdown(
        """
        <div class="hero-banner">
            <span class="hero-badge">✦ Case-Based Reasoning (CBR)</span>
            <h1 class="hero-title">
                Sistem Pakar Diagnosis Tingkat Keparahan DBD
                <span class="hero-subtitle">Metode Cosine Similarity</span>
            </h1>
            <p class="hero-desc">
                Sistem pakar berbasis web ini dirancang untuk membantu mendeteksi dan mengklasifikasikan
                tingkat keparahan penyakit <strong>Demam Berdarah Dengue (DHF Grade I – IV)</strong> berdasarkan
                gejala klinis dan hasil pemeriksaan laboratorium pasien. Sistem membandingkan vektor gejala pasien
                baru dengan basis kasus historis menggunakan perhitungan matematis <strong>Cosine Similarity</strong>.
            </p>
            <div class="hero-pills">
                <span class="hero-pill">14 Parameter Gejala (G1–G14)</span>
                <span class="hero-pill">4 Basis Kasus (DHF Grade I–IV)</span>
                <span class="hero-pill">Cosine Similarity Vector Space</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Card Cara Kerja Sistem
    with st.container(border=True):
        st.markdown("### Cara Kerja Sistem (Case-Based Reasoning)")
        st.caption("Alur pemrosesan diagnosis dari input pasien hingga penentuan tingkat keparahan DBD:")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                """
                <div class="how-card">
                    <div class="how-step-num">1</div>
                    <h4 style="margin:0 0 0.45rem 0; font-size:1rem; font-weight:700; color:#0f172a;">
                        Input Identitas & Gejala
                    </h4>
                    <p style="margin:0; font-size:0.87rem; line-height:1.6; color:#475569;">
                        Pengguna mengisi identitas pasien lalu memilih gejala yang dialami dari 14 daftar gejala (G1–G14),
                        yang direpresentasikan menjadi vektor biner (<code>1</code> = dialami, <code>0</code> = tidak).
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                """
                <div class="how-card">
                    <div class="how-step-num">2</div>
                    <h4 style="margin:0 0 0.45rem 0; font-size:1rem; font-weight:700; color:#0f172a;">
                        Perhitungan Cosine Similarity
                    </h4>
                    <p style="margin:0; font-size:0.87rem; line-height:1.6; color:#475569;">
                        Sistem menghitung tingkat kemiripan sudut antara vektor gejala pasien baru (<i>x</i>) dan setiap kasus
                        pada basis pengetahuan (<i>y</i>) menggunakan rumus: <code>(x · y) / (||x|| × ||y||)</code>.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                """
                <div class="how-card">
                    <div class="how-step-num">3</div>
                    <h4 style="margin:0 0 0.45rem 0; font-size:1rem; font-weight:700; color:#0f172a;">
                        Hasil Diagnosis & Solusi Medis
                    </h4>
                    <p style="margin:0; font-size:0.87rem; line-height:1.6; color:#475569;">
                        Kasus dengan nilai persentase kemiripan tertinggi (<i>Retrieve & Reuse</i>) ditetapkan sebagai hasil
                        diagnosis paling mendekati beserta saran penanganan medisnya.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")
        (col_cta_center,) = st.columns(1)
        with col_cta_center:
            st.markdown('<span class="cta-center-anchor"></span>', unsafe_allow_html=True)
            st.button(
                "Mulai Diagnosis Sekarang ➔",
                type="primary",
                on_click=set_menu,
                args=("Diagnosis",),
            )

    st.write("")

    # 3. Card Identitas Pembuat Sistem (Show / Hide)
    with st.container(border=True):
        col_cr_title, col_cr_btn = st.columns([3.5, 1.3], vertical_alignment="center")
        with col_cr_title:
            st.markdown('<span class="creator-header-anchor"></span>', unsafe_allow_html=True)
            st.markdown("### Identitas Pembuat Sistem")
            st.caption("Informasi pengembang aplikasi Sistem Pakar Diagnosis DBD.")
        with col_cr_btn:
            btn_label = "Sembunyikan Profil ▲" if st.session_state.show_creator else "Tampilkan Profil ▼"
            st.button(btn_label, type="secondary", on_click=toggle_creator)

        if st.session_state.show_creator:
            # SILAKAN SESUAIKAN DATA DIRI ANDA DI BAWAH INI
            st.markdown(
                """
                <div class="creator-card">
                    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:1.1rem;">
                        <div>
                            <div style="font-size:0.74rem; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; color:#64748b;">Nama Lengkap</div>
                            <div style="font-size:1rem; font-weight:700; color:#0f172a; margin-top:0.2rem;">Nama Lengkap Anda</div>
                        </div>
                        <div>
                            <div style="font-size:0.74rem; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; color:#64748b;">NIM / Nomor Induk</div>
                            <div style="font-size:1rem; font-weight:700; color:#0f172a; margin-top:0.2rem;">21241010XXXX</div>
                        </div>
                        <div>
                            <div style="font-size:0.74rem; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; color:#64748b;">Program Studi</div>
                            <div style="font-size:0.95rem; font-weight:600; color:#1e293b; margin-top:0.2rem;">Informatika / Sistem Informasi</div>
                        </div>
                        <div>
                            <div style="font-size:0.74rem; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; color:#64748b;">Mata Kuliah / Proyek</div>
                            <div style="font-size:0.95rem; font-weight:600; color:#1e293b; margin-top:0.2rem;">Sistem Pakar / Kecerdasan Buatan</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    # 4. Card Disclaimer Medis
    st.markdown(
        """
        <div class="disclaimer-box">
            <strong>⚠️ Disclaimer Medis</strong><br/>
            Hasil diagnosis dari sistem ini bersifat <strong>edukatif dan skrining awal</strong>, bukan pengganti
            pemeriksaan maupun diagnosis resmi oleh dokter profesional. Segera kunjungi fasilitas kesehatan atau
            IGD terdekat apabila pasien mengalami tanda bahaya DBD (seperti perdarahan spontan, nyeri perut hebat,
            muntah terus-menerus, lemas berat, atau tanda-tanda syok).
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==============================================================================
# MENU 2: DIAGNOSIS
# ==============================================================================
elif st.session_state.active_menu == "Diagnosis":
    # Stepper Indicator
    if st.session_state.step == 1:
        st.markdown(
            """
            <div class="stepper-bar">
                <span class="step-badge-active">Langkah 1: Identitas Pasien</span>
                <span style="color:#94a3b8; font-weight:700;">➔</span>
                <span class="step-badge-inactive">Langkah 2: Input Gejala & Hasil Diagnosis</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="stepper-bar">
                <span class="step-badge-done">✔ Langkah 1: Identitas Pasien</span>
                <span style="color:#0a9c8a; font-weight:700;">➔</span>
                <span class="step-badge-active">Langkah 2: Input Gejala & Hasil Diagnosis</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---------------- LANGKAH 1: INPUT IDENTITAS PASIEN ----------------
    if st.session_state.step == 1:
        with st.container(border=True):
            st.markdown("### Form Identitas Pasien")
            st.caption("Silakan lengkapi data identitas pasien terlebih dahulu sebelum memilih gejala.")
            st.write("")

            col_id1, col_id2 = st.columns(2, gap="large")
            with col_id1:
                nama = st.text_input(
                    "Nama Lengkap Pasien *",
                    value=st.session_state.pasien["nama"],
                    placeholder="Contoh: Budi Santoso",
                )
                st.write("")
                jenis_kelamin = st.selectbox(
                    "Jenis Kelamin *",
                    options=["Laki-laki", "Perempuan"],
                    index=0 if st.session_state.pasien["jenis_kelamin"] == "Laki-laki" else 1,
                )

            with col_id2:
                usia = st.number_input(
                    "Usia (Tahun) *",
                    min_value=0,
                    max_value=120,
                    value=int(st.session_state.pasien["usia"]),
                    step=1,
                )
                st.write("")
                alamat = st.text_input(
                    "Alamat / Domisili (Opsional)",
                    value=st.session_state.pasien["alamat"],
                    placeholder="Contoh: Jl. Kalimantan No. 10, Jember",
                )

            st.write("")
            btn_next_col, _ = st.columns([1.4, 2.6])
            with btn_next_col:
                submit_identitas = st.button("Lanjut ke Input Gejala ➔", type="primary")

            if submit_identitas:
                if not nama.strip():
                    st.markdown(
                        '<div class="error-alert">⚠️ Nama lengkap pasien wajib diisi sebelum melanjutkan.</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.session_state.pasien = {
                        "nama": nama.strip(),
                        "usia": usia,
                        "jenis_kelamin": jenis_kelamin,
                        "alamat": alamat.strip() if alamat.strip() else "-",
                    }
                    st.session_state.step = 2
                    st.rerun()

    # ---------------- LANGKAH 2: INPUT GEJALA & HASIL DIAGNOSIS ----------------
    elif st.session_state.step == 2:
        p = st.session_state.pasien

        # Ringkasan Identitas Pasien Sejajar dengan Tombol Ubah Identitas
        col_p_info, col_p_btn = st.columns([4.2, 1.1], vertical_alignment="center")
        with col_p_info:
            st.markdown(
                f"""
                <div class="patient-summary-card">
                    <div style="font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:#0c7c70;">
                        Data Identitas Pasien
                    </div>
                    <div style="font-size:1.08rem; font-weight:700; color:#0f172a; margin-top:0.2rem;">
                        {p['nama']} <span style="font-weight:500; color:#475569;">({p['jenis_kelamin']}, {p['usia']} Tahun)</span>
                    </div>
                    <div style="font-size:0.84rem; color:#475569; margin-top:0.2rem;">
                        Alamat: <strong>{p['alamat']}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_p_btn:
            st.button("✎ Ubah Identitas", type="secondary", on_click=ke_step_identitas)

        st.write("")

        # Form Input Gejala
        with st.container(border=True):
            selected_gejala_now = [
                g["id"] for g in GEJALA if st.session_state.get(f"chk_{g['id']}", False)
            ]

            col_head_1, col_head_2 = st.columns([3, 1], vertical_alignment="center")
            with col_head_1:
                st.markdown("### Form Input Gejala Pasien")
                st.caption("Pilih semua gejala yang dialami pasien (G1 – G14).")
            with col_head_2:
                st.markdown(
                    f'<div style="text-align:right;">'
                    f'<span class="counter-pill">{len(selected_gejala_now)} <span style="color:#93c5fd;">/</span> 14 gejala dipilih</span>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

            st.write("")
            cols = st.columns(4)
            for idx, gejala in enumerate(GEJALA):
                with cols[idx % 4]:
                    st.checkbox(
                        f"**{gejala['id']}** — {gejala['name']}",
                        key=f"chk_{gejala['id']}",
                    )

            st.write("")
            btn_col1, btn_col2, btn_col3 = st.columns([3, 1.1, 1.1])
            with btn_col1:
                st.button("✔ Mulai Diagnosis", type="primary", on_click=mulai_diagnosis)
            with btn_col2:
                st.button("↻ Reset Gejala", type="secondary", on_click=reset_gejala)
            with btn_col3:
                st.button("✚ Pasien Baru", type="secondary", on_click=reset_semua)

        # ================= HASIL DIAGNOSIS =================
        if st.session_state.diagnosed_gejala is not None:
            selected_gejala = st.session_state.diagnosed_gejala

            if not selected_gejala:
                st.session_state.trigger_loading = False
                st.markdown(
                    '<div class="error-alert">⚠️ Pilih minimal satu gejala (G1 – G14) terlebih dahulu untuk memulai diagnosis.</div>',
                    unsafe_allow_html=True,
                )
            else:
                if st.session_state.trigger_loading:
                    loading_placeholder = st.empty()
                    loading_placeholder.markdown(
                        """
                        <div class="loading-card">
                            <div class="spinner-ring"></div>
                            <span>Menghitung kemiripan vektor gejala dengan basis kasus CBR...</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    time.sleep(0.45)
                    loading_placeholder.empty()
                    st.session_state.trigger_loading = False

                new_vector = build_vector(selected_gejala)
                results = []

                for case in CASE_BASE:
                    case_vector = build_vector(case["gejala"])
                    dp = dot_product(new_vector, case_vector)
                    n_input = norm(new_vector)
                    n_case = norm(case_vector)
                    sim = dp / (n_input * n_case) if n_input and n_case else 0.0
                    results.append(
                        {
                            "case": case,
                            "case_vector": case_vector,
                            "dot_product": dp,
                            "norm_input": n_input,
                            "norm_case": n_case,
                            "similarity": sim,
                        }
                    )

                ranking = sorted(results, key=lambda r: r["similarity"], reverse=True)
                best = ranking[0]
                best_case = best["case"]
                percentage = round(best["similarity"] * 100, 2)
                percentage_text = f"{percentage:.2f}%"
                theme = GRADE_THEME.get(best_case["grade"], GRADE_THEME["I"])
                matched_gejala = [g for g in best_case["gejala"] if g in selected_gejala]

                st.write("")
                st.markdown(
                    f'<div class="success-alert">✔ Analisis selesai! Ditemukan kecocokan tertinggi dengan <strong>{best_case["disease"]}</strong> ({percentage_text}).</div>',
                    unsafe_allow_html=True,
                )

                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div class="result-wrapper" data-run="{st.session_state.diagnosis_count}">
                            <div class="result-banner" style="background: {theme['banner']};">
                                <div style="display:flex; flex-wrap:wrap; gap:0.6rem; align-items:center; justify-content:space-between;">
                                    <div style="display:flex; flex-wrap:wrap; gap:0.6rem; align-items:center;">
                                        <span style="background:{theme['pill_bg']}; padding:0.38rem 0.95rem; border-radius:9999px; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em;">
                                            Tingkat Keparahan Grade {best_case['grade']}
                                        </span>
                                        <span style="border:1px solid rgba(255,255,255,0.4); padding:0.32rem 0.85rem; border-radius:9999px; font-size:0.75rem; font-weight:600;">
                                            {best_case['id']} • Similarity {best['similarity']:.4f}
                                        </span>
                                    </div>
                                    <span style="background:rgba(0,0,0,0.22); padding:0.35rem 0.9rem; border-radius:9999px; font-size:0.78rem; font-weight:600;">
                                        Pasien: {p['nama']} ({p['usia']} Thn)
                                    </span>
                                </div>
                                <div style="margin-top:1.35rem;">
                                    <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                                        <span style="font-size:0.88rem; opacity:0.92;">Tingkat Kemiripan (Cosine Similarity) — {theme['status_label']}</span>
                                        <span style="font-size:2.1rem; font-weight:800; line-height:1;">{percentage_text}</span>
                                    </div>
                                    <div class="progress-track">
                                        <div class="progress-fill" style="width:{min(percentage, 100)}%; background:{theme['bar']};"></div>
                                    </div>
                                </div>
                                <h2 style="margin-top:1.3rem; font-size:1.4rem; font-weight:700; color:#ffffff;">
                                    {percentage_text} Terdiagnosis {best_case['disease']}
                                </h2>
                                <p style="margin-top:0.45rem; font-size:0.93rem; opacity:0.94; line-height:1.6;">
                                    {best_case['description']}
                                </p>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.write("")
                    col_sol, col_rank = st.columns(2, gap="medium")

                    with col_sol:
                        chips_html = (
                            "".join([f'<span class="chip-gejala">{gid}</span>' for gid in matched_gejala])
                            if matched_gejala
                            else '<span style="font-size:0.8rem; font-style:italic; color:#64748b;">Tidak ada gejala kasus yang cocok.</span>'
                        )
                        st.markdown(
                            f"""
                            <div class="info-card-teal">
                                <div style="font-size:0.8rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:#0e625a;">
                                    ✔ Saran & Solusi Penanganan Medis
                                </div>
                                <p style="margin-top:0.8rem; font-size:0.9rem; line-height:1.65; color:#334155;">
                                    {best_case['solution']}
                                </p>
                                <div style="margin-top:1.1rem; background:#ffffff; padding:0.9rem; border-radius:0.85rem; border:1px solid #ccfbf1;">
                                    <div style="font-size:0.72rem; font-weight:700; text-transform:uppercase; color:#0c7c70; margin-bottom:0.5rem;">
                                        Gejala yang Cocok dengan Basis Kasus
                                    </div>
                                    {chips_html}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    with col_rank:
                        rank_items_html = ""
                        for i, r in enumerate(ranking):
                            is_top = i == 0
                            bg = "linear-gradient(135deg, #1b6ef5, #1457e1)" if is_top else "#ffffff"
                            txt = "#ffffff" if is_top else "#334155"
                            border = "none" if is_top else "1px solid #dbeafe"
                            badge_bg = "rgba(255,255,255,0.22)" if is_top else "#eff6ff"
                            badge_txt = "#ffffff" if is_top else "#1d4ed8"
                            pct_r = f"{round(r['similarity'] * 100, 2):.2f}%"

                            rank_items_html += f"""
                            <div class="rank-item" style="display:flex; justify-content:space-between; align-items:center; background:{bg}; color:{txt}; border:{border}; padding:0.7rem 0.9rem; border-radius:0.8rem; margin-bottom:0.55rem; font-size:0.875rem;">
                                <span style="display:flex; align-items:center; gap:0.65rem;">
                                    <span style="display:inline-flex; width:1.6rem; height:1.6rem; align-items:center; justify-content:center; border-radius:0.45rem; background:{badge_bg}; color:{badge_txt}; font-size:0.75rem; font-weight:700;">
                                        {i + 1}
                                    </span>
                                    <span style="font-weight:600;">{r['case']['disease']}</span>
                                </span>
                                <span style="font-family:monospace; font-weight:700;">{pct_r}</span>
                            </div>
                            """

                        st.markdown(
                            f"""
                            <div class="info-card-blue">
                                <div style="font-size:0.8rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:#1747b6; margin-bottom:0.8rem;">
                                    ⚖ Peringkat Kemiripan Seluruh Kasus
                                </div>
                                {rank_items_html}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

# ================= FOOTER =================
st.markdown(
    """
    <p style="text-align:center; font-size:0.78rem; color:#64748b; margin-top:2.5rem;">
        Sistem Pakar Diagnosis Tingkat Keparahan DBD — Case-Based Reasoning dengan Cosine Similarity.
        Gejala berdasarkan Jurnal Telkom University & rekam medis.
    </p>
    """,
    unsafe_allow_html=True,
)