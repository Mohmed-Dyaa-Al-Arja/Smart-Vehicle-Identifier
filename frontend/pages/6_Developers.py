import base64
from pathlib import Path

import streamlit as st

from utils.session import init_session
from utils.theme import init_theme, load_css
from utils.i18n import init_lang, t
from utils.developers import DEVELOPERS
from components.navigation import render_navbar


# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Developers | Vehicle Vision AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================================
# INITIALIZATION
# ============================================================================

init_session()
init_theme()
init_lang()
load_css("developers")

render_navbar(active="nav_developers")

language = st.session_state.get("lang", "en")

_PAGES_DIR = Path(__file__).resolve().parent


def display_name(dev: dict) -> str:
    """Arabic name when the UI language is Arabic and one is set,
    otherwise fall back to the English name."""

    if language == "ar" and dev.get("name_ar"):
        return dev["name_ar"]

    return dev["name"]


def get_photo_data_uri(photo_path: Path) -> str:
    """Base64-encode a local photo so it can render as a plain <img> tag
    inside the fixed-size avatar circle (same approach as the profile
    page), instead of st.image() which doesn't fit a fixed CSS box."""

    if not photo_path.exists():
        return ""

    suffix = photo_path.suffix.lower()

    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }

    mime = mime_types.get(suffix, "image/png")

    encoded = base64.b64encode(
        photo_path.read_bytes()
    ).decode("utf-8")

    return f"data:{mime};base64,{encoded}"


# ============================================================================
# HEADER
# ============================================================================

st.html(
    f"""
    <div class="vv-dev-badge">
        <span class="vv-dev-badge-icon">✦</span>
        {t("nav_developers")}
    </div>

    <div class="vv-dev-header">

        <h1 class="vv-dev-title">
            Our <span class="vv-dev-title-gradient">Developers</span>
        </h1>

        <p class="vv-dev-desc">
            {t("developers_subtitle")}
        </p>

    </div>
    """
)


# ============================================================================
# DEVELOPERS GRID
# ============================================================================

cols = st.columns(4, gap="medium")


MAX_VISIBLE_SKILLS = 6


for i, (col, dev) in enumerate(zip(cols, DEVELOPERS)):

    with col:

        with st.container(key=f"vv-dev-card-{i}"):

            name = display_name(dev)

            photo_file = (
                _PAGES_DIR / "img" / Path(dev.get("photo", "")).name
            )

            has_photo = (
                bool(dev.get("photo"))
                and photo_file.exists()
            )

            if has_photo:

                photo_uri = get_photo_data_uri(photo_file)

                avatar_inner = (
                    f'<img src="{photo_uri}" alt="{name}" />'
                )

                avatar_class = "vv-dev-avatar vv-dev-avatar-photo"

            else:

                avatar_inner = name[0].upper()
                avatar_class = "vv-dev-avatar"

            visible_skills = dev["skills"][:MAX_VISIBLE_SKILLS]
            extra_count = len(dev["skills"]) - len(visible_skills)

            skills_html = "".join(
                f'<span class="vv-dev-skill">{skill}</span>'
                for skill in visible_skills
            )

            if extra_count > 0:
                skills_html += (
                    f'<span class="vv-dev-skill '
                    f'vv-dev-skill-more">+{extra_count}</span>'
                )

            st.html(
                f"""
                <div class="{avatar_class}">
                    {avatar_inner}
                </div>

                <div class="vv-dev-name">
                    {name}
                </div>

                <div class="vv-dev-role" title="{dev["role"]}">
                    {dev["role"]}
                </div>

                <div class="vv-dev-bio">
                    {dev["bio"]}
                </div>

                <div class="vv-dev-skills">
                    {skills_html}
                </div>
                """
            )

            if st.button(
                f"👤  {t('view_profile')}",
                key=f"developer_{i}",
                use_container_width=True,
            ):
                st.session_state.selected_developer = i
                st.switch_page("pages/7_Developer_Profile.py")



# ============================================================================
# BOTTOM TEAM BANNER
# ============================================================================

st.html(
    f"""
    <div class="vv-dev-banner">

        <div class="vv-dev-banner-icon">
            🚀
        </div>

        <div class="vv-dev-banner-content">

            <h3>
                {t("team_tagline_title")}
            </h3>

            <p>
                {t("team_tagline_desc")}
            </p>

        </div>

    </div>
    """
)