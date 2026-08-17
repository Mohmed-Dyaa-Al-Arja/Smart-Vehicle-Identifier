from pathlib import Path
import base64
import html

import streamlit as st

from utils.session import init_session
from utils.theme import init_theme, load_css
from utils.i18n import init_lang, t, is_rtl
from components.navigation import render_navbar


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Features | Vehicle Vision AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# INITIALIZATION
# ============================================================

init_session()
init_theme()
init_lang()

load_css("features")
render_navbar(active="nav_features")


# ============================================================
# IMAGE PATHS
# ============================================================

IMG_DIR = Path(__file__).resolve().parent.parent / "img"

LIGHT_IMAGE = IMG_DIR / "car_light_page4.png"
DARK_IMAGE = IMG_DIR / "car_dark_page4.png"


# ============================================================
# LOAD HERO IMAGE ACCORDING TO THEME
# ============================================================

current_theme = st.session_state.get("theme", "light")

if current_theme == "dark":
    HERO_IMAGE = DARK_IMAGE
else:
    HERO_IMAGE = LIGHT_IMAGE


# ============================================================
# CONVERT IMAGE TO BASE64
# This makes the image work reliably inside Streamlit CSS.
# ============================================================

def image_to_base64(image_path: Path) -> str:
    if not image_path.exists():
        return ""

    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


hero_base64 = image_to_base64(HERO_IMAGE)


# ============================================================
# HERO IMAGE STYLE
# ============================================================

if hero_base64:
    hero_image_style = f"""
<style>
.features-page {{
    --features-hero-image: url("data:image/png;base64,{hero_base64}");
}}
</style>
"""
else:
    hero_image_style = ""


# ============================================================
# TRANSLATED CONTENT
# ============================================================

features = [
    {
        "title": t("f_detect_t"),
        "description": t("f_detect_d"),
        "icon": """
<svg viewBox="0 0 24 24"
     fill="none"
     stroke="currentColor"
     stroke-width="1.65"
     stroke-linecap="round"
     stroke-linejoin="round">
    <path d="M4 9V5a1 1 0 0 1 1-1h4"/>
    <path d="M20 9V5a1 1 0 0 0-1-1h-4"/>
    <path d="M4 15v4a1 1 0 0 0 1 1h4"/>
    <path d="M20 15v4a1 1 0 0 1-1 1h-4"/>
    <circle cx="12" cy="12" r="3"/>
</svg>
""",
    },
    {
        "title": t("f_instant_t"),
        "description": t("f_instant_d"),
        "icon": """
<svg viewBox="0 0 24 24"
     fill="none"
     stroke="currentColor"
     stroke-width="1.65"
     stroke-linecap="round"
     stroke-linejoin="round">
    <path d="M4 15a8 8 0 1 1 16 0"/>
    <path d="M12 12l4-4"/>
    <path d="M7 18h10"/>
    <path d="M8 21h8"/>
</svg>
""",
    },
    {
        "title": t("f_specs_t"),
        "description": t("f_specs_d"),
        "icon": """
<svg viewBox="0 0 24 24"
     fill="none"
     stroke="currentColor"
     stroke-width="1.65"
     stroke-linecap="round"
     stroke-linejoin="round">
    <rect x="5" y="3" width="14" height="18" rx="2"/>
    <path d="M9 7h6"/>
    <path d="M9 11h6"/>
    <path d="M9 15h4"/>
</svg>
""",
    },
    {
        "title": t("f_assistant_t"),
        "description": t("f_assistant_d"),
        "icon": """
<svg viewBox="0 0 24 24"
     fill="none"
     stroke="currentColor"
     stroke-width="1.65"
     stroke-linecap="round"
     stroke-linejoin="round">
    <rect x="5" y="4" width="14" height="16" rx="4"/>
    <circle cx="9" cy="10" r="1"/>
    <circle cx="15" cy="10" r="1"/>
    <path d="M9 15h6"/>
    <path d="M5 9H2"/>
    <path d="M22 9h-3"/>
    <path d="M8 4V2"/>
    <path d="M16 4V2"/>
</svg>
""",
    },
    {
        "title": t("f_market_t"),
        "description": t("f_market_d"),
        "icon": """
<svg viewBox="0 0 24 24"
     fill="none"
     stroke="currentColor"
     stroke-width="1.65"
     stroke-linecap="round"
     stroke-linejoin="round">
    <circle cx="12" cy="12" r="9"/>
    <path d="M12 7v10"/>
    <path d="M15 9c0-1.2-1.3-2-3-2s-3 .8-3 2 1.3 2 3 2 3 .8 3 2-1.3 2-3 2-3-.8-3-2"/>
</svg>
""",
    },
    {
        "title": t("f_sources_t"),
        "description": t("f_sources_d"),
        "icon": """
<svg viewBox="0 0 24 24"
     fill="none"
     stroke="currentColor"
     stroke-width="1.65"
     stroke-linecap="round"
     stroke-linejoin="round">
    <circle cx="12" cy="12" r="9"/>
    <path d="M3 12h18"/>
    <path d="M12 3c3 3 3 15 0 18"/>
    <path d="M12 3c-3 3-3 15 0 18"/>
</svg>
""",
    },
    {
        "title": t("f_export_t"),
        "description": t("f_export_d"),
        "icon": """
<svg viewBox="0 0 24 24"
     fill="none"
     stroke="currentColor"
     stroke-width="1.65"
     stroke-linecap="round"
     stroke-linejoin="round">
    <path d="M12 3v12"/>
    <path d="M7 10l5 5 5-5"/>
    <path d="M5 20h14"/>
</svg>
""",
    },
    {
        "title": t("f_secure_t"),
        "description": t("f_secure_d"),
        "icon": """
<svg viewBox="0 0 24 24"
     fill="none"
     stroke="currentColor"
     stroke-width="1.65"
     stroke-linecap="round"
     stroke-linejoin="round">
    <path d="M12 3l8 3v5c0 5-3.2 8.2-8 10-4.8-1.8-8-5-8-10V6z"/>
    <path d="M9 12l2 2 4-4"/>
</svg>
""",
    },
]


# ============================================================
# FEATURE CARDS HTML
# ============================================================

cards_html = ""

for item in features:

    title = html.escape(item["title"])
    description = html.escape(item["description"])

    cards_html += f"""
<div class="features-card">

    <div class="features-card-header">

        <div class="features-card-icon">
            {item["icon"]}
        </div>

        <div class="features-card-title">
            {title}
        </div>

    </div>

    <div class="features-card-description">
        {description}
    </div>

    <div class="features-card-link">
        {html.escape(t("learn_more"))}
        <span>→</span>
    </div>

</div>
"""


# ============================================================
# RTL / LTR
# ============================================================

direction_class = "features-rtl" if is_rtl() else "features-ltr"


# ============================================================
# PAGE TITLE
# ============================================================

if is_rtl():
    title_prefix = "مميزات"
    title_highlight = "قوية"
else:
    title_prefix = "Powerful"
    title_highlight = "Features"


# ============================================================
# HERO IMAGE STYLE
# ============================================================

st.markdown(
    hero_image_style,
    unsafe_allow_html=True,
)


# ============================================================
# PAGE HTML
# ============================================================

page_html = f"""
<div class="features-page {direction_class}">

    <!-- ==================================================
         HERO
         ================================================== -->

    <section class="features-hero">

        <div class="features-hero-content">

            <h1 class="features-title">
                <span>{html.escape(title_prefix)}</span>
                <strong>{html.escape(title_highlight)}</strong>
            </h1>

            <p class="features-subtitle">
                {html.escape(t("features_subtitle"))}
            </p>

        </div>

    </section>


    <!-- ==================================================
         FEATURES GRID
         ================================================== -->

    <section class="features-grid">

        {cards_html}

    </section>


    <!-- ==================================================
         STATISTICS
         ================================================== -->

    <section class="features-stats">


        <!-- ACCURACY -->

        <div class="features-stat">

            <div class="features-stat-icon">

                <svg viewBox="0 0 24 24"
                     fill="none"
                     stroke="currentColor"
                     stroke-width="1.65"
                     stroke-linecap="round"
                     stroke-linejoin="round">

                    <circle cx="12" cy="12" r="8"/>
                    <circle cx="12" cy="12" r="3"/>
                    <path d="M12 12l6-6"/>

                </svg>

            </div>

            <div>

                <div class="features-stat-value">
                    98%+
                </div>

                <div class="features-stat-label">
                    {html.escape(t("stat_accuracy"))}
                </div>

            </div>

        </div>


        <div class="features-stat-divider"></div>


        <!-- IMAGES -->

        <div class="features-stat">

            <div class="features-stat-icon">

                <svg viewBox="0 0 24 24"
                     fill="none"
                     stroke="currentColor"
                     stroke-width="1.65"
                     stroke-linecap="round"
                     stroke-linejoin="round">

                    <rect x="4" y="5" width="16" height="14" rx="2"/>
                    <circle cx="9" cy="10" r="1.5"/>
                    <path d="M4 16l5-5 4 4 2-2 5 4"/>

                </svg>

            </div>

            <div>

                <div class="features-stat-value">
                    50K+
                </div>

                <div class="features-stat-label">
                    {html.escape(t("stat_images"))}
                </div>

            </div>

        </div>


        <div class="features-stat-divider"></div>


        <!-- AI POWERED -->

        <div class="features-stat">

            <div class="features-stat-icon">

                <svg viewBox="0 0 24 24"
                     fill="none"
                     stroke="currentColor"
                     stroke-width="1.65"
                     stroke-linecap="round"
                     stroke-linejoin="round">

                    <rect x="7" y="7" width="10" height="10" rx="2"/>

                    <path d="M9 1v4"/>
                    <path d="M15 1v4"/>
                    <path d="M9 19v4"/>
                    <path d="M15 19v4"/>

                    <path d="M1 9h4"/>
                    <path d="M1 15h4"/>
                    <path d="M19 9h4"/>
                    <path d="M19 15h4"/>

                </svg>

            </div>

            <div>

                <div class="features-stat-value">
                    100%
                </div>

                <div class="features-stat-label">
                    {html.escape(t("stat_ai_powered"))}
                </div>

            </div>

        </div>


        <div class="features-stat-divider"></div>


        <!-- SUPPORT -->

        <div class="features-stat">

            <div class="features-stat-icon">

                <svg viewBox="0 0 24 24"
                     fill="none"
                     stroke="currentColor"
                     stroke-width="1.65"
                     stroke-linecap="round"
                     stroke-linejoin="round">

                    <path d="M4 14v-2a8 8 0 0 1 16 0v2"/>
                    <path d="M4 14h3v5H5a1 1 0 0 1-1-1z"/>
                    <path d="M20 14h-3v5h2a1 1 0 0 1-1-1z"/>
                    <path d="M17 19c0 2-2 3-5 3"/>

                </svg>

            </div>

            <div>

                <div class="features-stat-value">
                    24/7
                </div>

                <div class="features-stat-label">
                    {html.escape(t("stat_support"))}
                </div>

            </div>

        </div>


    </section>

</div>
"""


# ============================================================
# REMOVE LEADING INDENTATION
#
# IMPORTANT:
# Streamlit Markdown can interpret indented HTML as code.
# We remove the indentation from every line before rendering.
# ============================================================

page_html = "\n".join(
    line.lstrip()
    for line in page_html.splitlines()
)


# ============================================================
# RENDER PAGE
# ============================================================

st.markdown(
    page_html,
    unsafe_allow_html=True,
)