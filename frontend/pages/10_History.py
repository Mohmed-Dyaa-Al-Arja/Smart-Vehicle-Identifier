"""
Vehicle Vision AI — Detection History.

Rebuilt to match the approved reference design:
sidebar rail | hero with detection HUD | timeline list | quick-stats rail.

Functionality preserved from the previous version: backend history load with
demo fallback, search, type filter, date filter, pagination, View Result,
PDF Report, Delete, theme, language, RTL.
"""

from datetime import datetime, timedelta
from pathlib import Path
import base64
import html
import re

import streamlit as st

from utils.session import (
    init_session,
    set_detection,
    clear_pending_image,
)
from utils.theme import init_theme, load_css
from utils.i18n import init_lang, is_rtl, t
from components.navigation import render_navbar
from api.client import APIError


# ============================================================
# DEFENSIVE BACKEND IMPORTS
# ============================================================

try:
    from api.vehicle_api import get_detection_history
except ImportError:
    get_detection_history = None

try:
    from api.vehicle_api import delete_detection
except ImportError:
    delete_detection = None


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="History | Vehicle Vision AI",
    page_icon="🚘",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# INITIALIZATION
# ============================================================

init_session()
init_theme()
init_lang()
load_css("history")

render_navbar(active="nav_history")

language = st.session_state.get("lang", "en")
rtl = is_rtl()

PAGE_SIZE = 5


# ============================================================
# IMAGE ASSETS
# ------------------------------------------------------------
# Assets live in:  frontend/img/   (flat, same folder as every
# other page's car/robot art — NOT assets/img/history).
#
# The loader tries .webp .jpg .jpeg .png .svg for each base name,
# so dropping a real photo named e.g. "history_toyota.png" is
# picked up automatically, no code change needed.
#
# It also checks a short list of folder names/locations and matches
# file names case-insensitively, so a slightly different folder or
# a "History_Toyota.PNG" vs "history_toyota.png" mismatch on Windows
# still resolves instead of silently falling back to empty.
# ============================================================

_PAGE_DIR = Path(__file__).resolve().parent.parent
_CANDIDATE_DIRS = [
    _PAGE_DIR / "img",
    _PAGE_DIR / "image",
    _PAGE_DIR / "images",
    _PAGE_DIR / "assets" / "img" / "history",
    _PAGE_DIR / "assets" / "img",
]
IMG_DIR = _CANDIDATE_DIRS[0]

_MIME = {
    ".webp": "image/webp",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".svg": "image/svg+xml",
}


@st.cache_data(show_spinner=False)
def load_asset(base_name: str) -> str:
    """Return a data: URI for the asset, or '' when nothing is found."""
    stem = Path(base_name).stem.lower()
    exts = (".webp", ".jpg", ".jpeg", ".png", ".svg")

    for folder in _CANDIDATE_DIRS:
        if not folder.is_dir():
            continue
        # Exact-name fast path first.
        for ext in exts:
            path = folder / f"{stem}{ext}"
            if path.is_file():
                return _to_data_uri(path, ext)
        # Case-insensitive fallback, also tolerating a browser/Windows
        # duplicate-download suffix such as "history_toyota (1).png".
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
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{_MIME[ext]};base64,{b64}"


def img_tag(base_name: str, css_class: str = "") -> str:
    src = load_asset(base_name)
    if not src:
        return ""
    return f'<img class="{css_class}" src="{src}" alt="" />'


# Which artwork represents which kind of record / body type.
THUMB_BY_TYPE = {
    "plate": "history_license_plate",
    "vqa": "history_red_car",
}

THUMB_BY_BODY = {
    "motorcycle": "history_honda",
    "suv": "history_range_rover",
    "truck": "history_range_rover",
    "coupe": "history_red_car",
    "sedan": "history_toyota",
}


def thumb_for(item: dict) -> str:
    type_key = item.get("type_key", "vehicle_recognition")
    if type_key in THUMB_BY_TYPE:
        return THUMB_BY_TYPE[type_key]

    body = str(item.get("body_type", "")).lower()
    for token, name in THUMB_BY_BODY.items():
        if token in body:
            return name
    return "history_toyota"


# ============================================================
# TRANSLATIONS
# ============================================================

def get_copy(lang: str) -> dict:

    if lang == "ar":
        return {
            "kicker": "السجل",
            "title_1": "سجل",
            "title_2": "الفحوصات",
            "subtitle": "تابع وراجع كل عمليات التعرف على المركبات في مكان واحد.",
            "detected": "تم اكتشاف مركبة",
            "search": "ابحث بالمركبة أو اللوحة أو التاريخ أو السؤال...",
            "all_types": "كل الأنواع",
            "all_time": "كل الأوقات",
            "last_7": "آخر 7 أيام",
            "last_30": "آخر 30 يوم",
            "last_90": "آخر 90 يوم",
            "completed": "مكتمل",
            "quick_stats": "إحصائيات سريعة",
            "total": "إجمالي الفحوصات",
            "vehicle_rec": "التعرف على المركبات",
            "vqa": "أسئلة بصرية",
            "plate": "قراءة اللوحات",
            "recent_activity": "النشاط الأخير",
            "recognized": "تم التعرف عليها",
            "answered": "تمت الإجابة على سؤال",
            "plate_detected": "تم اكتشاف لوحة",
            "ai_title": "الذكاء الاصطناعي يتعلم باستمرار",
            "ai_desc": "كل عملية فحص تجعل النظام أذكى وأكثر دقة.",
            "history": "السجل",
            "saved": "النتائج المحفوظة",
            "settings": "الإعدادات",
            "promo": "رؤية أذكى<br>لطرق أكثر أمانًا",
            "empty": "لا توجد نتائج مطابقة.",
            "empty_hint": "جرّب تغيير كلمة البحث أو الفلاتر.",
            "start": "ابدأ فحص جديد",
            "view": "عرض النتيجة",
            "pdf": "تقرير PDF",
            "delete": "حذف",
            "deleted": "تم حذف عملية الكشف.",
            "soon": "هذه الميزة قيد التطوير",
            "soon_desc": "نعمل عليها حاليًا، ترقّبها قريبًا.",
            "today": "اليوم",
            "more": "خيارات",
        }

    return {
        "kicker": "HISTORY",
        "title_1": "Your Detection",
        "title_2": "History",
        "subtitle": "Track and revisit all your vehicle recognition experiences in one place.",
        "detected": "Vehicle Detected",
        "search": "Search by vehicle, plate, date or question...",
        "all_types": "All Types",
        "all_time": "All Time",
        "last_7": "Last 7 Days",
        "last_30": "Last 30 Days",
        "last_90": "Last 90 Days",
        "completed": "Completed",
        "quick_stats": "Quick Stats",
        "total": "Total Detections",
        "vehicle_rec": "Vehicle Recognition",
        "vqa": "VQA Questions",
        "plate": "License Plate Reads",
        "recent_activity": "Recent Activity",
        "recognized": "recognized",
        "answered": "Question answered:",
        "plate_detected": "License plate detected:",
        "ai_title": "AI Keeps Learning",
        "ai_desc": "Every detection makes our system smarter and more accurate.",
        "history": "History",
        "saved": "Saved Results",
        "settings": "Settings",
        "promo": "Smarter Vision<br>for Safer Roads",
        "empty": "No matching detections found.",
        "empty_hint": "Try changing your search or filters.",
        "start": "Start New Detection",
        "view": "View Result",
        "pdf": "PDF Report",
        "delete": "Delete",
        "deleted": "Detection removed.",
        "soon": "Coming Soon",
        "soon_desc": "We're still building this. Check back soon.",
        "today": "today",
        "more": "More",
    }


copy = get_copy(language)

TYPE_LABELS = {
    "en": {
        "vehicle_recognition": "Vehicle Recognition",
        "vqa": "Visual Question Answering",
        "plate": "License Plate Recognition",
    },
    "ar": {
        "vehicle_recognition": "التعرف على المركبات",
        "vqa": "الإجابة على الأسئلة البصرية",
        "plate": "التعرف على لوحة المركبة",
    },
}


def type_label(type_key: str) -> str:
    return TYPE_LABELS.get(language, TYPE_LABELS["en"]).get(type_key, type_key)


# ============================================================
# DEMO / FALLBACK DATA
# (used only when the backend is unavailable — same policy as before)
# ============================================================

def _demo_date(days_ago: int) -> str:
    return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")


DEMO_HISTORY = [
    {
        "detection_id": "VVA-DEMO-0001",
        "make": "Toyota", "model": "Corolla", "year": 2020,
        "body_type": "Sedan", "color": "White", "confidence": 96.4,
        "date": _demo_date(2), "time": "14:32",
        "type_key": "vehicle_recognition",
    },
    {
        "detection_id": "VVA-DEMO-0002",
        "make": "Range Rover", "model": "", "year": 2021,
        "body_type": "SUV", "color": "Black", "confidence": 94.1,
        "date": _demo_date(3), "time": "11:20",
        "type_key": "vehicle_recognition",
    },
    {
        "detection_id": "VVA-DEMO-0003",
        "make": "Mazda", "model": "CX-5", "year": 2022,
        "body_type": "SUV", "color": "Red", "confidence": 91.7,
        "date": _demo_date(4), "time": "16:45",
        "type_key": "vqa",
        "question": "What color is the car?",
    },
    {
        "detection_id": "VVA-DEMO-0004",
        "make": "Chevrolet", "model": "Malibu", "year": 2019,
        "body_type": "Sedan", "color": "Blue", "confidence": 89.9,
        "date": _demo_date(6), "time": "10:18",
        "type_key": "plate",
        "plate": "ABC-123",
    },
    {
        "detection_id": "VVA-DEMO-0005",
        "make": "Honda", "model": "CBR", "year": 2019,
        "body_type": "Motorcycle", "color": "Black", "confidence": 93.2,
        "date": _demo_date(9), "time": "09:05",
        "type_key": "vehicle_recognition",
    },
]

_LEGACY_TYPE_MAP = {
    "vehicle recognition": "vehicle_recognition",
    "visual question answering": "vqa",
    "license plate recognition": "plate",
}


def normalize_type_key(item: dict) -> str:
    """Backend rows may only carry a display string; map it to a stable key."""
    if item.get("type_key"):
        return item["type_key"]
    if item.get("plate"):
        return "plate"
    if item.get("question"):
        return "vqa"
    legacy = str(item.get("type", "")).strip().lower()
    return _LEGACY_TYPE_MAP.get(legacy, "vehicle_recognition")


# ============================================================
# LOAD HISTORY
# ============================================================

if st.session_state.get("history_cache") is None:
    if get_detection_history is not None:
        try:
            response = get_detection_history()
            st.session_state.history_cache = response.get("items", []) or DEMO_HISTORY
        except APIError:
            st.session_state.history_cache = DEMO_HISTORY
        except Exception:
            st.session_state.history_cache = DEMO_HISTORY
    else:
        st.session_state.history_cache = DEMO_HISTORY

items = st.session_state.history_cache or []

for _item in items:
    _item["type_key"] = normalize_type_key(_item)


# ============================================================
# HELPERS
# ============================================================

MONTHS_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

MONTHS_AR = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
             "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]


def pretty_date(date_str: str) -> str:
    """'2025-08-15' -> 'Aug 15, 2025' (or the Arabic equivalent)."""
    try:
        parsed = datetime.strptime(str(date_str), "%Y-%m-%d")
    except (ValueError, TypeError):
        return str(date_str or "-")

    months = MONTHS_AR if language == "ar" else MONTHS_EN
    month = months[parsed.month - 1]

    if language == "ar":
        return f"{parsed.day} {month} {parsed.year}"
    return f"{month} {parsed.day}, {parsed.year}"


def relative_time(date_str: str) -> str:
    try:
        parsed = datetime.strptime(str(date_str), "%Y-%m-%d")
    except (ValueError, TypeError):
        return str(date_str or "-")

    delta = (datetime.now() - parsed).days
    if delta <= 0:
        return copy["today"]
    if language == "ar":
        return f"منذ {delta} يوم"
    return f"{delta} day{'s' if delta != 1 else ''} ago"


def vehicle_name(item: dict) -> str:
    parts = [str(item.get("make", "")).strip(), str(item.get("model", "")).strip()]
    return " ".join(p for p in parts if p) or "Vehicle"


st.html('<div class="vv-history-root"></div>')


# ============================================================
# SIDEBAR NAV STATE
# ============================================================

if "vvh_nav" not in st.session_state:
    st.session_state.vvh_nav = "history"

if "vvh_page" not in st.session_state:
    st.session_state.vvh_page = 1

active_nav = st.session_state.vvh_nav


# ============================================================
# LAYOUT SHELL
# ============================================================

st.markdown('<span class="vv-hist-scope"></span>', unsafe_allow_html=True)

if "vvh_sidebar_open" not in st.session_state:
    st.session_state.vvh_sidebar_open = True
sidebar_open = st.session_state.vvh_sidebar_open

side_w, content_w = (1.45, 6.55) if sidebar_open else (0.62, 7.38)

if rtl:
    content_col, side_col = st.columns([content_w, side_w], gap="small")
else:
    side_col, content_col = st.columns([side_w, content_w], gap="small")


# ------------------------------------------------------------
# LEFT SIDEBAR
# ------------------------------------------------------------

with side_col:

    if not sidebar_open:
        st.markdown('<span class="vvh-collapsed-mark"></span>', unsafe_allow_html=True)

    with st.container(key="vvh-sidebar-toggle"):
        if rtl:
            toggle_icon = "»" if sidebar_open else "«"
        else:
            toggle_icon = "«" if sidebar_open else "»"
        if st.button(toggle_icon, key="vvh_sidebar_toggle_btn"):
            st.session_state.vvh_sidebar_open = not sidebar_open
            st.rerun()

    NAV = [
        ("history", "▤", copy["history"]),
        ("saved", "🔖", copy["saved"]),
        ("settings", "⚙", copy["settings"]),
    ]

    for name, icon, label in NAV:
        container_key = f"vvh-nav-{name}" + ("-on" if active_nav == name else "")
        with st.container(key=container_key):
            btn_label = icon if not sidebar_open else f"{icon}   {label}"
            if st.button(btn_label,
                         key=f"vvh_navbtn_{name}",
                         use_container_width=True):
                st.session_state.vvh_nav = name
                st.rerun()

    if sidebar_open:
        promo_icon = img_tag("history_sidebar_car") or "🚘"
        st.html(
            f"""
            <div class="hist-side-promo">
                <div class="hist-side-promo-icon">{promo_icon}</div>
                <b>{copy["promo"]}</b>
                <div class="hist-side-promo-rule"></div>
            </div>
            """
        )


# ------------------------------------------------------------
# CONTENT
# ------------------------------------------------------------

with content_col:

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    # The hero background is the actual supplied artwork (road + city
    # skyline + car + detection frame, already baked into one photo) —
    # one file per theme, swapped purely with CSS. No CSS-drawn shapes.
    hero_bg_light = img_tag("history_hero_bg_light", "hist-hero-bg hist-hero-bg--light")
    hero_bg_dark = img_tag("history_hero_bg_dark", "hist-hero-bg hist-hero-bg--dark")

    # Falls back to the old car-only cutout / SVG if the new background
    # pair hasn't been dropped into frontend/img yet.
    if not hero_bg_light and not hero_bg_dark:
        hero_bg_light = (
            img_tag("history_hero_car_light", "hist-hero-bg hist-hero-bg--light")
            or img_tag("history_hero_car", "hist-hero-bg hist-hero-bg--light")
        )
        hero_bg_dark = img_tag("history_hero_car_dark", "hist-hero-bg hist-hero-bg--dark")

    sparkles = "".join(
        f'<span class="hist-spark" style="--x:{4 + i * 5.4:.1f}%;--sd:{2.6 + (i % 5) * 0.5:.1f}s;--sdel:{i * 0.22:.2f}s;--sz:{2 + (i % 3)}px"></span>'
        for i in range(18)
    )

    st.html(
        f"""
        <section class="hist-hero">
            <div class="hist-hero-stage">
                {hero_bg_light}{hero_bg_dark}
                <div class="hist-hero-tint"></div>
                <div class="hist-hero-scan"></div>
                <div class="hist-hero-pulse"></div>
                <div class="hist-hero-sparkles">{sparkles}</div>
            </div>

            <div class="hist-hero-content">
                <div class="hist-kicker">{copy["kicker"]}</div>
                <h1>{copy["title_1"]} <span>{copy["title_2"]}</span></h1>
                <p>{copy["subtitle"]}</p>
            </div>
        </section>
        """
    )

    # --------------------------------------------------------
    # "COMING SOON" PANELS (Saved Results / Settings)
    # --------------------------------------------------------

    if active_nav != "history":
        title = copy["saved"] if active_nav == "saved" else copy["settings"]
        st.html(
            f"""
            <div class="hist-body">
                <div class="hist-empty">
                    <div class="hist-empty-icon">✦</div>
                    <h3>{title} — {copy["soon"]}</h3>
                    <p>{copy["soon_desc"]}</p>
                </div>
            </div>
            """
        )
        st.stop()

    # --------------------------------------------------------
    # BODY: list + right rail
    # --------------------------------------------------------

    st.markdown('<div class="hist-body">', unsafe_allow_html=True)
    st.markdown('<span class="vvh-split"></span>', unsafe_allow_html=True)

    if rtl:
        rail_col, list_col = st.columns([2.35, 5.65], gap="medium")
    else:
        list_col, rail_col = st.columns([5.65, 2.35], gap="medium")

    # ========================================================
    # LIST COLUMN
    # ========================================================

    with list_col:

        f1, f2, f3 = st.columns([4.2, 1.7, 1.9], gap="small")

        with f1:
            with st.container(key="vvh-search"):
                query = st.text_input(
                    "search",
                    placeholder=copy["search"],
                    label_visibility="collapsed",
                    key="vvh_query",
                )

        type_keys = sorted({i.get("type_key", "vehicle_recognition") for i in items})

        with f2:
            with st.container(key="vvh-filter-type"):
                type_filter = st.selectbox(
                    "type",
                    options=["__all__"] + type_keys,
                    format_func=lambda k: copy["all_types"] if k == "__all__" else type_label(k),
                    label_visibility="collapsed",
                    key="vvh_type",
                )

        with f3:
            with st.container(key="vvh-filter-date"):
                date_filter = st.selectbox(
                    "date",
                    options=[copy["last_30"], copy["last_7"],
                             copy["last_90"], copy["all_time"]],
                    label_visibility="collapsed",
                    key="vvh_date",
                )

        # ----- filtering -----

        filtered = list(items)

        if query:
            q = query.lower().strip()
            filtered = [
                i for i in filtered
                if q in (
                    f"{i.get('make','')} {i.get('model','')} {i.get('year','')} "
                    f"{i.get('color','')} {i.get('body_type','')} "
                    f"{i.get('detection_id','')} {i.get('plate','')} "
                    f"{i.get('question','')} {i.get('date','')}"
                ).lower()
            ]

        if type_filter != "__all__":
            filtered = [i for i in filtered if i.get("type_key") == type_filter]

        date_map = {copy["last_7"]: 7, copy["last_30"]: 30, copy["last_90"]: 90}

        if date_filter in date_map:
            cutoff = datetime.now() - timedelta(days=date_map[date_filter])
            kept = []
            for i in filtered:
                try:
                    if datetime.strptime(str(i.get("date", "")), "%Y-%m-%d") >= cutoff:
                        kept.append(i)
                except (ValueError, TypeError):
                    kept.append(i)          # undated rows are never hidden
            filtered = kept

        # ----- empty state -----

        if not filtered:
            st.html(
                f"""
                <div class="hist-empty">
                    <div class="hist-empty-icon">◌</div>
                    <h3>{copy["empty"]}</h3>
                    <p>{copy["empty_hint"]}</p>
                </div>
                """
            )
            if st.button(copy["start"], type="primary", key="vvh_start_empty"):
                st.switch_page("pages/1_Detect.py")

        else:
            # ----- pagination window -----

            total_pages = max(1, (len(filtered) + PAGE_SIZE - 1) // PAGE_SIZE)
            page = min(max(1, st.session_state.vvh_page), total_pages)
            st.session_state.vvh_page = page

            start = (page - 1) * PAGE_SIZE
            page_items = filtered[start:start + PAGE_SIZE]

            st.markdown('<div class="hist-rows">', unsafe_allow_html=True)

            for offset, item in enumerate(page_items):

                did = str(item.get("detection_id", f"row-{start + offset}"))
                safe_id = "".join(ch if ch.isalnum() else "-" for ch in did)

                type_key = item.get("type_key", "vehicle_recognition")
                name = html.escape(vehicle_name(item))
                year = html.escape(str(item.get("year", "")))
                date_txt = html.escape(pretty_date(item.get("date", "")))
                time_txt = html.escape(str(item.get("time", "")))

                when = f"{date_txt}" + (f" · {time_txt}" if time_txt else "")

                if type_key == "vqa":
                    detail = f'<em>💬</em> "{html.escape(str(item.get("question", "")))}"'
                    # The supplied VQA artwork already carries the chat chip,
                    # so only draw our own when the image lacks it (SVG fallback).
                    chip = "" if load_asset("history_red_car").startswith("data:image/png") \
                        else '<div class="hist-thumb-chip">💬</div>'
                elif type_key == "plate":
                    detail = f'<em>🔖</em> {html.escape(str(item.get("plate", "-")))}'
                    chip = ""
                else:
                    label = f"{name} - {year}" if year else name
                    detail = f'<em>🚗</em> {label}'
                    chip = ""

                thumb = img_tag(thumb_for(item))

                with st.container(key=f"vvh-item-{safe_id}"):

                    st.html('<div class="hist-node"></div>')

                    with st.container(key=f"vvh-row-{safe_id}"):

                        r_info, r_status, r_go, r_more = st.columns(
                            [6.0, 2.0, 0.7, 0.6], gap="small"
                        )

                        with r_info:
                            st.html(
                                f"""
                                <div class="hist-row" style="grid-template-columns:96px 1fr;">
                                    <div class="hist-thumb">{thumb}{chip}</div>
                                    <div class="hist-info">
                                        <div class="hist-info-title">{html.escape(type_label(type_key))}</div>
                                        <div class="hist-meta">{detail}</div>
                                        <div class="hist-meta"><em>📅</em> {when}</div>
                                    </div>
                                </div>
                                """
                            )

                        with r_status:
                            st.html(
                                f'<div class="hist-status"><i>✓</i>{copy["completed"]}</div>'
                            )

                        with r_go:
                            with st.container(key=f"vvh-go-{safe_id}"):
                                if st.button("‹" if rtl else "›",
                                             key=f"vvh_view_{safe_id}",
                                             help=copy["view"],
                                             use_container_width=True):
                                    set_detection(item)
                                    clear_pending_image()
                                    st.switch_page("pages/3_Result.py")

                        with r_more:
                            with st.container(key=f"vvh-more-{safe_id}"):
                                with st.popover("⋯", use_container_width=True):

                                    if st.button(f"▣  {copy['pdf']}",
                                                 key=f"vvh_pdf_{safe_id}",
                                                 use_container_width=True):
                                        set_detection(item)
                                        st.switch_page("pages/11_PDF_Report.py")

                                    if st.button(f"🗑  {copy['delete']}",
                                                 key=f"vvh_del_{safe_id}",
                                                 use_container_width=True):
                                        if delete_detection is not None:
                                            try:
                                                delete_detection(did)
                                            except APIError:
                                                pass
                                            except Exception:
                                                pass

                                        st.session_state.history_cache = [
                                            x for x in st.session_state.history_cache
                                            if str(x.get("detection_id")) != did
                                        ]
                                        st.toast(copy["deleted"])
                                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

            # ----- pagination controls -----

            if total_pages > 1:
                st.markdown('<div class="hist-pager">', unsafe_allow_html=True)

                slots = st.columns([1] * (total_pages + 2) + [6], gap="small")

                with slots[0]:
                    with st.container(key="vvh-pg-prev"):
                        if st.button("›" if rtl else "‹",
                                     key="vvh_pg_prev",
                                     disabled=(page <= 1)):
                            st.session_state.vvh_page = page - 1
                            st.rerun()

                for n in range(1, total_pages + 1):
                    with slots[n]:
                        k = f"vvh-pg-{n}" + ("-on" if n == page else "")
                        with st.container(key=k):
                            if st.button(str(n), key=f"vvh_pg_{n}"):
                                st.session_state.vvh_page = n
                                st.rerun()

                with slots[total_pages + 1]:
                    with st.container(key="vvh-pg-next"):
                        if st.button("‹" if rtl else "›",
                                     key="vvh_pg_next",
                                     disabled=(page >= total_pages)):
                            st.session_state.vvh_page = page + 1
                            st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

    # ========================================================
    # RIGHT RAIL
    # ========================================================

    with rail_col:

        n_total = len(items)
        n_vr = len([i for i in items if i.get("type_key") == "vehicle_recognition"])
        n_vqa = len([i for i in items if i.get("type_key") == "vqa"])
        n_plate = len([i for i in items if i.get("type_key") == "plate"])

        st.html(
            f"""
            <div class="hist-rail-title">{copy["quick_stats"]}</div>
            <div class="hist-stat-grid">
                <div class="hist-stat">
                    <div class="hist-stat-icon">◱</div>
                    <div class="hist-stat-value">{n_total}</div>
                    <div class="hist-stat-label">{copy["total"]}</div>
                </div>
                <div class="hist-stat">
                    <div class="hist-stat-icon">🚘</div>
                    <div class="hist-stat-value">{n_vr}</div>
                    <div class="hist-stat-label">{copy["vehicle_rec"]}</div>
                </div>
                <div class="hist-stat">
                    <div class="hist-stat-icon">💬</div>
                    <div class="hist-stat-value">{n_vqa}</div>
                    <div class="hist-stat-label">{copy["vqa"]}</div>
                </div>
                <div class="hist-stat">
                    <div class="hist-stat-icon">🔖</div>
                    <div class="hist-stat-value">{n_plate}</div>
                    <div class="hist-stat-label">{copy["plate"]}</div>
                </div>
            </div>
            """
        )

        # ----- recent activity -----

        rows = ""
        for item in items[:3]:
            key = item.get("type_key", "vehicle_recognition")
            when = relative_time(item.get("date", ""))

            if key == "vqa":
                icon = "💬"
                text = f'{copy["answered"]} "{html.escape(str(item.get("question", "")))}"'
            elif key == "plate":
                icon = "🔖"
                text = f'{copy["plate_detected"]} {html.escape(str(item.get("plate", "")))}'
            else:
                icon = "🚘"
                text = f'{html.escape(vehicle_name(item))} {copy["recognized"]}'

            rows += f"""
                <div class="hist-act">
                    <div class="hist-act-icon">{icon}</div>
                    <div>
                        <div class="hist-act-text">{text}</div>
                        <div class="hist-act-time">{when}</div>
                    </div>
                </div>
            """

        st.html(
            f"""
            <div class="hist-activity">
                <div class="hist-rail-title">{copy["recent_activity"]}</div>
                {rows}
            </div>
            """
        )

        # ----- AI keeps learning -----

        st.html(
            f"""
            <div class="hist-ai">
                <div class="hist-ai-orb">✦</div>
                <div class="hist-ai-body">
                    <h3>{copy["ai_title"]}</h3>
                    <p>{copy["ai_desc"]}</p>
                </div>
                <svg class="hist-ai-spark" viewBox="0 0 56 26">
                    <path d="M2,22 L14,15 L24,18 L36,8 L46,11 L54,3"/>
                </svg>
            </div>
            """
        )

    st.markdown("</div>", unsafe_allow_html=True)