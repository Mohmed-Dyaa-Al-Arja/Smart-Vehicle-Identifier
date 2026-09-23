"""
About page — Smart Vehicle Identifier
Layout: hero (title + description + feature pills + hero photo) →
"Our Vision" video-style card + "About Our Platform" 2x2 feature grid.
Built the same way as pages/10_History.py: a self-contained get_copy()
dict for EN/AR text, a resilient multi-folder image loader, and a
dedicated about.css stylesheet.
"""

from pathlib import Path
import base64
import html
import re

import streamlit as st

from utils.session import init_session
from utils.theme import init_theme, load_css
from utils.i18n import init_lang, is_rtl
from components.navigation import render_navbar

st.set_page_config(
    page_title="About | Smart Vehicle Identifier",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_session()
init_theme()
init_lang()
load_css("about")
render_navbar(active="nav_about")

rtl = is_rtl()
lang = "ar" if rtl else "en"


# ============================================================
# IMAGE ASSETS — same resilient loader as the History page:
# tries several likely folders and matches file names loosely
# (case-insensitive, tolerates a "(1)" duplicate-download suffix).
# ============================================================

_PAGE_DIR = Path(__file__).resolve().parent.parent
_CANDIDATE_DIRS = [
    _PAGE_DIR / "img",
    _PAGE_DIR / "image",
    _PAGE_DIR / "images",
    _PAGE_DIR / "assets" / "img" / "about",
    _PAGE_DIR / "assets" / "img",
]

_MIME = {
    ".webp": "image/webp", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".svg": "image/svg+xml",
}


@st.cache_data(show_spinner=False)
def load_asset(base_name: str) -> str:
    stem = Path(base_name).stem.lower()
    exts = (".webp", ".jpg", ".jpeg", ".png", ".svg")
    for folder in _CANDIDATE_DIRS:
        if not folder.is_dir():
            continue
        for ext in exts:
            path = folder / f"{stem}{ext}"
            if path.is_file():
                return _to_data_uri(path, ext)
        try:
            for entry in folder.iterdir():
                if not entry.is_file() or entry.suffix.lower() not in exts:
                    continue
                entry_stem = re.sub(r"\s*\(\d+\)$", "", entry.stem.lower())
                if entry_stem == stem:
                    return _to_data_uri(entry, entry.suffix.lower())
        except OSError:
            continue
    return ""


def _to_data_uri(path: Path, ext: str) -> str:
    b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{_MIME[ext]};base64,{b64}"


# ============================================================
# COPY (EN / AR)
# ============================================================

def get_copy(lang: str) -> dict:
    if lang == "ar":
        return {
            "badge": "من نحن",
            "title_1": "نحوّل الصور إلى",
            "title_2": "رؤى ذكية",
            "desc": (
                "منصة \"محدد المركبات الذكي\" تستخدم الذكاء الاصطناعي لمساعدتك في "
                "التعرف على المركبات، والحصول على معلومات تفصيلية، واستكشاف القيمة "
                "السوقية — كل ذلك في مكان واحد. نجمع بين رؤية الحاسوب، واستخراج "
                "البيانات من الويب، وتقنية RAG، ونماذج الذكاء الاصطناعي الحديثة "
                "لتقديم نتائج دقيقة وموثوقة ومحدثة."
            ),
            "pills": [
                ("🧠", "تعرف مدعوم بالذكاء الاصطناعي"),
                ("⏱", "معلومات لحظية"),
                ("🛡", "مصادر موثوقة"),
                ("🪄", "سهل الاستخدام"),
            ],
            "vision_title": "رؤيتنا",
            "vision_desc": "طريقة أذكى وأسهل وأكثر شفافية للتعرف على المركبات وفهمها باستخدام قوة الذكاء الاصطناعي.",
            "platform_kicker": "عن منصتنا",
            "platform_title": "أكثر من مجرد أداة تعرّف على المركبات",
            "platform_desc": (
                "بنينا هذه المنصة لإتاحة التعرف على المركبات والمعلومات الخاصة بها "
                "للجميع — سواء كنت مشتريًا أو بائعًا أو باحثًا أو مجرد فضولي. باستخدام "
                "نماذج الذكاء الاصطناعي المتقدمة واستخراج بيانات الويب وتقنية RAG، "
                "نقدّم تفاصيل دقيقة وبيانات لحظية ورؤى قيّمة عن أي مركبة من صورة واحدة."
            ),
            "cards": [
                ("🎯", "تعرف ذكي", "تحديد المركبات بدقة عالية باستخدام الذكاء الاصطناعي."),
                ("🗂", "بيانات شاملة", "احصل على المواصفات والأسعار ورؤى السوق."),
                ("🛡", "مصادر موثوقة", "معلومات من مصادر موثوقة ومُتحقق منها."),
                ("⚡", "سريع وفعّال", "احصل على النتائج في ثوانٍ، لا دقائق."),
            ],
        }
    return {
        "badge": "About Us",
        "title_1": "Turning Images into",
        "title_2": "Smart Insights",
        "desc": (
            "Smart Vehicle Identifier is an AI-powered platform that helps you "
            "identify vehicles, get detailed information, and explore the market "
            "value — all in one place. We combine computer vision, web scraping, "
            "RAG, and modern AI models to deliver accurate, reliable, and "
            "up-to-date results."
        ),
        "pills": [
            ("🧠", "AI-Powered Recognition"),
            ("⏱", "Real-Time Information"),
            ("🛡", "Trusted Sources"),
            ("🪄", "Easy to Use"),
        ],
        "vision_title": "Our Vision",
        "vision_desc": "A smarter, easier, and more transparent way to identify and understand vehicles using the power of AI.",
        "platform_kicker": "About Our Platform",
        "platform_title": "More Than Just a Vehicle Identifier",
        "platform_desc": (
            "We built this platform to make vehicle recognition and information "
            "accessible to everyone — whether you're a buyer, a seller, a "
            "researcher, or simply curious. Using advanced AI models, web "
            "scraping, and RAG technology, we provide accurate details, "
            "real-time data, and valuable insights about any vehicle from a "
            "single image."
        ),
        "cards": [
            ("🎯", "Smart Recognition", "Identify vehicles with high accuracy using AI."),
            ("🗂", "Comprehensive Data", "Get specs, prices, and market insights."),
            ("🛡", "Reliable Sources", "Information from trusted and verified sources."),
            ("⚡", "Fast & Efficient", "Get results in seconds, not minutes."),
        ],
    }


copy = get_copy(lang)


# ============================================================
# HERO — title/description/pills on one side, photo on the other
# ============================================================

st.markdown('<span class="vv-abt-scope"></span>', unsafe_allow_html=True)

hero_dark = load_asset("about_hero_dark")
hero_light = load_asset("about_hero_light")

pills_html = "".join(
    f"""<div class="abt-pill">
            <div class="abt-pill-icon">{icon}</div>
            <div class="abt-pill-label">{html.escape(label)}</div>
        </div>"""
    for icon, label in copy["pills"]
)

hero_img_html = ""
if hero_dark:
    hero_img_html += f'<img class="abt-hero-img abt-hero-dark" src="{hero_dark}">'
if hero_light:
    hero_img_html += f'<img class="abt-hero-img abt-hero-light" src="{hero_light}">'

left, right = st.columns([1, 1.35], gap="large")

with left:
    st.html(
        f"""
        <div class="abt-section">
            <span class="abt-badge">📘 {copy["badge"]}</span>
            <h1 class="abt-title">{copy["title_1"]} <span>{copy["title_2"]}</span></h1>
            <p class="abt-desc">{copy["desc"]}</p>
            <div class="abt-pills">{pills_html}</div>
        </div>
        """
    )

with right:
    if hero_img_html:
        st.html(hero_img_html)
    else:
        st.info("Drop about_hero_dark.png / about_hero_light.png into frontend/img/")

st.markdown("<div style='height:34px'></div>", unsafe_allow_html=True)


# ============================================================
# "OUR VISION" CARD + "ABOUT OUR PLATFORM" GRID
# ============================================================

_vision_suffix = "ar" if lang == "ar" else "en"
vision_dark = load_asset(f"about_vision_{_vision_suffix}_dark")
vision_light = load_asset(f"about_vision_{_vision_suffix}_light")

vision_layers = ""
if vision_dark:
    vision_layers += f'<img class="abt-vision-img abt-vision-img--dark" src="{vision_dark}">'
if vision_light:
    vision_layers += f'<img class="abt-vision-img abt-vision-img--light" src="{vision_light}">'
vision_fallback = ""
if not vision_dark:
    vision_fallback += (
        f'<div class="abt-vision-missing abt-vision-missing--dark">🖼 '
        f'about_vision_{_vision_suffix}_dark.png not found in frontend/img/</div>'
    )
if not vision_light:
    vision_fallback += (
        f'<div class="abt-vision-missing abt-vision-missing--light">🖼 '
        f'about_vision_{_vision_suffix}_light.png not found in frontend/img/</div>'
    )

cards_html = "".join(
    f"""<div class="abt-card">
            <div class="abt-card-icon">{icon}</div>
            <div class="abt-card-title">{html.escape(title)}</div>
            <div class="abt-card-desc">{html.escape(desc)}</div>
        </div>"""
    for icon, title, desc in copy["cards"]
)

v_col, p_col = st.columns([1, 1.15], gap="large")

with v_col:
    st.html(
        f"""
        <div class="abt-vision">
            {vision_layers}
            {vision_fallback}
        </div>
        """
    )

with p_col:
    st.html(
        f"""
        <div class="abt-platform">
            <div class="abt-kicker">{copy["platform_kicker"]}</div>
            <h3 class="abt-platform-title">{copy["platform_title"]}</h3>
            <p class="abt-platform-desc">{copy["platform_desc"]}</p>
            <div class="abt-grid">{cards_html}</div>
        </div>
        """
    )