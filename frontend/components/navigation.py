"""Shared navigation bar."""

import streamlit as st

from utils.theme import toggle_theme
from utils.i18n import t, toggle_lang

NAV_ITEMS = [
    ("nav_home", "app.py"),
    ("nav_detect", "pages/1_Detect.py"),
    ("nav_chat", "pages/4_Chat.py"),
    ("nav_features", "pages/5_Features.py"),
    ("nav_developers", "pages/6_Developers.py"),
    ("nav_history", "pages/10_History.py"),
    ("nav_about", "pages/9_About.py"),
]


def get_brand_copy(lang: str) -> tuple[str, str]:
    """
    Brand name / subtitle shown in the navbar logo.

    Hardcoded per-language (not routed through t("brand_name") /
    t("brand_suffix")) because the requested wording doesn't match what
    those translation keys currently resolve to. If proper translation
    keys are added later for this exact wording, switch this back to t(...).
    """

    if lang == "ar":
        return ("محدد المركبات الذكي", "مساعد المركبات بالذكاء الاصطناعي")

    return ("Smart Vehicle Identifier", "AI Vehicle Assistant")


def render_navbar(active: str = "nav_home") -> None:
    st.markdown('<span class="vv-navbar-marker"></span>', unsafe_allow_html=True)

    cols = st.columns([1.72] + [.84] * len(NAV_ITEMS) + [.50, .68, .72], gap="small")

    with cols[0]:
        lang = st.session_state.get("lang", "en")
        brand_name, brand_sub = get_brand_copy(lang)

        st.markdown(
            f'<div class="vv-logo">'
            f'<div class="vv-logo-icon">V</div>'
            f'<div class="vv-logo-title" style="display:flex;flex-direction:column;'
            f'line-height:1.25;">'
            f'<span style="font-weight:800;">{brand_name}</span>'
            f'<span style="font-size:0.65rem;font-weight:500;'
            f'color:#94A3B8;margin-top:2px;">{brand_sub}</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    for i, (key, page) in enumerate(NAV_ITEMS):
        with cols[i + 1]:
            st.page_link(
                page,
                label=t(key),
                use_container_width=True,
                disabled=(key == active),
            )

    with cols[-3]:
        dark = st.session_state.get("theme", "light") == "dark"
        if st.button("☀" if dark else "☾", key="nav_theme", use_container_width=True):
            toggle_theme()
            st.rerun()

    with cols[-2]:
        lang = st.session_state.get("lang", "en")
        if st.button("ع" if lang == "en" else "EN", key="nav_lang", use_container_width=True):
            toggle_lang()
            st.rerun()

    with cols[-1]:
        if st.button(t("login"), key="nav_login", use_container_width=True):
            st.session_state["login_requested"] = True

    if st.session_state.pop("login_requested", False):
        st.info(t("login_notice"))