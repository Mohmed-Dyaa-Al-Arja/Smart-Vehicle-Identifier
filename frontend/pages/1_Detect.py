import base64
from pathlib import Path

import streamlit as st

from utils.session import (
    init_session,
    set_pending_image,
    set_detection,
)

from utils.theme import (
    init_theme,
    load_css,
)

from utils.i18n import (
    init_lang,
    t,
    is_rtl,
)

from components.navigation import render_navbar
from components.upload_zone import render_upload_zone


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Detect Vehicle | Vehicle Vision AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# INITIALIZATION
# ============================================================

init_session()
init_theme()
init_lang()

load_css("detect")

render_navbar(active="nav_detect")


# ============================================================
# PATHS
# ============================================================

APP_DIR = Path(__file__).resolve().parent.parent
IMG_DIR = APP_DIR / "img"


# ============================================================
# IMAGE LOADER
# ============================================================

@st.cache_data(show_spinner=False)
def load_image_as_data_uri(path_str: str) -> str:

    path = Path(path_str)

    if not path.exists():
        return ""

    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }

    mime = mime_types.get(
        path.suffix.lower(),
        "image/png",
    )

    encoded = base64.b64encode(
        path.read_bytes()
    ).decode("ascii")

    return f"data:{mime};base64,{encoded}"


# ============================================================
# HERO IMAGE
# ============================================================

theme = st.session_state.get(
    "theme",
    "light",
)


if theme == "dark":

    car_path = (
        IMG_DIR /
        "car_dark_page2.png"
    )

else:

    car_path = (
        IMG_DIR /
        "car_light_page2.png"
    )


car_uri = load_image_as_data_uri(
    str(car_path)
)


# ============================================================
# DIRECTION
# ============================================================

direction_class = (
    "vv-detect-rtl"
    if is_rtl()
    else "vv-detect-ltr"
)


# ============================================================
# HERO CAR
# ============================================================

if car_uri:

    hero_car_html = f"""
    <div class="vv-detect-car-wrapper">

        <img
            class="vv-detect-car"
            src="{car_uri}"
            alt="Vehicle"
        >

    </div>
    """

else:

    hero_car_html = ""


# ============================================================
# TITLE
# ============================================================

detect_title = t(
    "detect_title"
)


if not is_rtl() and "Vehicle" in detect_title:

    detect_title_html = detect_title.replace(
        "Vehicle",
        '<span class="vv-vehicle-word">Vehicle</span>',
    )

else:

    detect_title_html = detect_title


# ============================================================
# HERO
# ============================================================

hero_html = f"""
<div class="vv-detect-hero {direction_class}">

    <div class="vv-detect-hero-content">

        <h1 class="vv-detect-title">
            {detect_title_html}
        </h1>

        <p class="vv-detect-subtitle">
            {t("detect_subtitle")}
        </p>

    </div>

    {hero_car_html}

</div>
"""

st.html(hero_html)


# ============================================================
# MAIN AREA
# ============================================================

col_upload, col_tips = st.columns(
    [2.1, 1],
    gap="large",
)


# ============================================================
# LEFT SIDE
# ============================================================

with col_upload:

    # --------------------------------------------------------
    # UPLOAD
    # --------------------------------------------------------

    uploaded = render_upload_zone()


    # --------------------------------------------------------
    # SPACE
    # --------------------------------------------------------

    st.markdown(
        '<div class="vv-detect-upload-gap"></div>',
        unsafe_allow_html=True,
    )


    # ========================================================
    # START + SECURITY
    # ========================================================

    btn_col, notice_col = st.columns(
        [1, 1.7],
        gap="medium",
    )


    # ========================================================
    # START DETECTION
    # ========================================================

    with btn_col:

        start_clicked = st.button(
            f"✨ {t('start_detection')}  →",

            type="primary",

            use_container_width=True,
        )


    # ========================================================
    # SECURITY NOTICE
    # ========================================================

    with notice_col:

        secure_html = f"""
        <div class="vv-secure-notice">

            <div class="vv-secure-icon">
                🛡️
            </div>

            <div class="vv-secure-content">

                <strong>
                    {t("secure_title")}
                </strong>

                <span class="vv-secure-desc">
                    {t("secure_desc")}
                </span>

            </div>

        </div>
        """

        st.html(secure_html)


    # ========================================================
    # DETECTION LOGIC
    # ========================================================

    if start_clicked:

        if uploaded is None:

            st.warning(
                t("please_upload_first")
            )

        else:

            set_pending_image(
                uploaded.getvalue(),
                uploaded.name,
                uploaded.type or "image/jpeg",
            )

            set_detection(None)

            st.switch_page(
                "pages/2_Loading.py"
            )


# ============================================================
# RIGHT SIDE — TIPS
# ============================================================

with col_tips:

    tips = [
        ("HD", "tip_1"),
        ("🚗", "tip_2"),
        ("☀️", "tip_3"),
        ("📷", "tip_4"),
    ]

    rows_html = ""

    for icon, key in tips:

        rows_html += f"""
        <div class="vv-tip-row">

            <div class="vv-tip-icon">
                {icon}
            </div>

            <span>
                {t(key)}
            </span>

        </div>
        """


    tips_html = f"""
    <div class="vv-tips-card">

        <div class="vv-tips-title">

            <span class="vv-tips-title-icon">
                ✨
            </span>

            <strong>
                {t("tips_title")}
            </strong>

        </div>

        <div class="vv-tips-list">
            {rows_html}
        </div>

    </div>
    """

    st.html(tips_html)