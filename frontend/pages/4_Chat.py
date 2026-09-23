from datetime import datetime
from pathlib import Path
import base64

import streamlit as st

from api.chat_api import ask_question
from api.client import APIError
from components.navigation import render_navbar
from utils.i18n import init_lang, is_rtl, t
from utils.session import (
    clear_chat,
    get_detection,
    get_session_id,
    init_session,
)
from utils.theme import init_theme, load_css


# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="AI Assistant | Vehicle Vision AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================================
# INITIALIZATION
# ============================================================================

init_session()
init_theme()
init_lang()
load_css("chat")

render_navbar(active="nav_chat")


# ============================================================================
# HELPERS
# ============================================================================

IMG_DIR = Path(__file__).resolve().parent.parent / "img"

SUGGESTED_ICONS = [
    "⛽",
    "⚡",
    "🛠",
    "✓",
    "💲",
    "🔀",
]


def get_theme() -> str:
    return st.session_state.get("theme", "light")


def get_language() -> str:
    return st.session_state.get("lang", "en")


def get_image_path(filename: str) -> Path:
    return IMG_DIR / filename


def get_image_data_uri(filename: str) -> str:

    image_path = get_image_path(filename)

    if not image_path.exists():
        return ""

    suffix = image_path.suffix.lower()

    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }

    mime = mime_types.get(suffix, "image/png")

    encoded = base64.b64encode(
        image_path.read_bytes()
    ).decode("utf-8")

    return f"data:{mime};base64,{encoded}"


def get_robot_image() -> str:

    if get_theme() == "dark":
        return get_image_data_uri("robot_dark_page3.png")

    return get_image_data_uri("robot_light_page3.png")


def get_banner_image() -> str:

    if get_theme() == "dark":
        return get_image_data_uri("car_banner_dark_page3.png")

    return get_image_data_uri("car_banner_light_page3.png")


def get_small_car_image() -> str:

    if get_theme() == "dark":
        return get_image_data_uri("car_small_dark_page3.png")

    return get_image_data_uri("car_small_light_page3.png")


def get_vehicle_context(
    detection: dict | None,
) -> str | None:

    if not detection:
        return None

    parts = [
        detection.get("make", ""),
        detection.get("model", ""),
        str(detection.get("year", "")),
    ]

    context = " ".join(
        str(part).strip()
        for part in parts
        if str(part).strip()
    ).strip()

    if not context and detection.get("vehicle_name"):
        context = str(
            detection["vehicle_name"]
        ).replace("_", " ")

    return context or None


def safe_confidence(value) -> float:

    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0.0

    return max(
        0.0,
        min(value, 100.0),
    )


def get_hero_copy(
    lang: str,
) -> tuple[str, str]:

    if lang == "ar":
        return (
            "مرحبًا!",
            "أنا مساعدك الذكي للمركبات. اسألني عن أي حاجة تخص "
            "السيارات، المواصفات، المميزات، أو التوصيات.",
        )

    return (
        "Hello!",
        "I'm your AI vehicle assistant. Ask me anything about "
        "cars, specifications, features, or recommendations.",
    )


def format_timestamp() -> str:

    return datetime.now().strftime(
        "%I:%M %p"
    ).lstrip("0")


# ============================================================================
# MESSAGE RENDERING
# ============================================================================

def render_message(
    role: str,
    content: str,
) -> None:

    is_user = role == "user"

    safe_content = (
        str(content)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )

    timestamp = format_timestamp()

    if is_user:

        st.html(
            f"""
            <div class="vv-msg vv-msg-user">

                <div class="vv-msg-body">

                    <div class="vv-msg-time">
                        {timestamp}
                    </div>

                    <div class="vv-bubble">
                        {safe_content}
                    </div>

                </div>

            </div>
            """
        )

    else:

        avatar = get_robot_image()

        st.html(
            f"""
            <div class="vv-msg vv-msg-ai">

                <div class="vv-msg-avatar">
                    <img src="{avatar}" alt="AI" />
                </div>

                <div class="vv-msg-body">

                    <div class="vv-msg-time">
                        {timestamp}
                    </div>

                    <div class="vv-bubble">
                        {safe_content}
                    </div>

                    <div class="vv-msg-tools">

                        <span title="{t("chat_copy")}">
                            ⧉
                        </span>

                        <span title="{t("chat_like")}">
                            ♡
                        </span>

                        <span title="{t("chat_more")}">
                            ⋯
                        </span>

                    </div>

                </div>

            </div>
            """
        )


# ============================================================================
# CONTEXT
# ============================================================================

detection = get_detection()

vehicle_context = get_vehicle_context(
    detection
)

language = get_language()

rtl = is_rtl()

rtl_class = (
    "vv-chat-page-rtl"
    if rtl
    else "vv-chat-page-ltr"
)


st.html(
    f'<div class="vv-chat-page {rtl_class}"></div>'
)


# ============================================================================
# SIDE PANEL STATE
# ============================================================================

if "vv_active_side_panel" not in st.session_state:
    st.session_state.vv_active_side_panel = None


active_panel = st.session_state.vv_active_side_panel

side_is_open = active_panel is not None


# ============================================================================
# RTL
# ============================================================================

if rtl:

    st.html(
        """
        <style>

        .st-key-vv-chat-main-shell,
        .st-key-vv-side-panel,
        .st-key-vv-side-rail {
            direction: rtl;
            text-align: right;
        }

        .vv-chat-hero-inline,
        .vv-msg-ai {
            flex-direction: row-reverse;
        }

        .vv-msg-user {
            margin-right: auto;
            margin-left: 0;
        }

        .vv-msg-time {
            text-align: right;
        }

        .vv-bubble {
            border-left: 1px solid #DCE6F5 !important;
            border-right: 3px solid #2563EB !important;
            border-radius: 14px 4px 4px 14px !important;
        }

        [data-theme="dark"] .vv-bubble {
            border-right-color: #3B82F6 !important;
        }

        .vv-msg-user .vv-bubble {
            border: none !important;
        }

        </style>
        """
    )


# ============================================================================
# MAIN TWO-COLUMN LAYOUT
# ============================================================================

if side_is_open:

    main_col, side_col = st.columns(
        [5.7, 1.55],
        gap="small",
    )

else:

    main_col, side_col = st.columns(
        [7.85, 0.42],
        gap="small",
    )


# ============================================================================
# MAIN CHAT COLUMN
# ============================================================================

with main_col:

    with st.container(
        key="vv-chat-main-shell"
    ):

        robot_image = get_robot_image()
        banner_image = get_banner_image()

        hero_title, hero_desc = get_hero_copy(
            language
        )

        # --------------------------------------------------------------------
        # HERO
        # --------------------------------------------------------------------

        st.html(
            f"""
            <div class="vv-chat-badge">

                <span class="vv-online-dot"></span>

                {t("chat_online")}

            </div>


            <div class="vv-chat-hero-inline">

                <div class="vv-hero-left">

                    <div class="vv-hero-avatar">

                        <img
                            src="{robot_image}"
                            alt="AI"
                        />

                    </div>


                    <div class="vv-hero-text">

                        <h2>

                            👋

                            <span class="vv-hero-gradient">
                                {hero_title}
                            </span>

                        </h2>


                        <p>
                            {hero_desc}
                        </p>

                    </div>

                </div>


                <div class="vv-hero-banner-wrap">

                    <div class="vv-hero-ring"></div>

                    <div class="vv-hero-banner">

                        <!-- DO NOT REMOVE:
                             ORIGINAL CAR SHINE EFFECT -->

                        <div class="vv-banner-scan"></div>

                        <div class="vv-banner-glow"></div>

                        <img
                            src="{banner_image}"
                            alt="Vehicle"
                        />

                    </div>

                </div>

            </div>
            """
        )


        # --------------------------------------------------------------------
        # CHAT AREA
        # --------------------------------------------------------------------

        messages = st.session_state.get(
            "chat_messages",
            []
        )

        scroll_height = (
            460
            if messages
            else 260
        )

        with st.container(
            height=scroll_height,
            key="vv-chat-scroll",
        ):

            for message in messages:

                render_message(
                    message["role"],
                    message["content"],
                )

            prompt = st.chat_input(
                t("chat_placeholder"),
                key="vehicle_chat_input",
            )


        st.html(
            f"""
            <div class="vv-chat-input-note">
                {t("chat_input_note")}
            </div>
            """
        )


        # --------------------------------------------------------------------
        # NEW CHAT
        # --------------------------------------------------------------------

        _, reset_col = st.columns(
            [6, 1]
        )

        with reset_col:

            if st.button(
                "↻",
                key="new_chat",
                help=t("chat_new_chat"),
                use_container_width=True,
            ):

                clear_chat()

                st.session_state.chat_messages = []

                st.rerun()


        # --------------------------------------------------------------------
        # HANDLE PROMPT
        # --------------------------------------------------------------------

        pending_prompt = st.session_state.pop(
            "_pending_prompt",
            None,
        )

        final_prompt = (
            prompt
            or pending_prompt
        )

        if final_prompt:

            st.session_state.chat_messages.append(
                {
                    "role": "user",
                    "content": final_prompt,
                }
            )

            try:

                response = ask_question(
                    question=final_prompt,
                    session_id=get_session_id(),
                    vehicle_context=vehicle_context,
                    language=language,
                )

                reply = (
                    response.get("answer")
                    or response.get("reply")
                    or response.get("response")
                    or response.get("message")
                    or str(response)
                )

            except APIError as exc:

                reply = (
                    f"{t('chat_demo_notice')} "
                    f"({exc})"
                )

            st.session_state.chat_messages.append(
                {
                    "role": "assistant",
                    "content": reply,
                }
            )

            st.rerun()


# ============================================================================
# COMPACT FUTURISTIC SIDE DOCK
# ============================================================================

with side_col:

    with st.container(
        key="vv-side-rail"
    ):

        # --------------------------------------------------------------------
        # DARK MODE: keep the currently-open panel's icon baby-blue
        # --------------------------------------------------------------------
        # Streamlit re-renders the button on every click, so the browser's
        # native :focus / :active state never "sticks" - it resets on each
        # rerun. To make the selected icon stay baby-blue while its panel
        # is open (instead of just flashing on click), we target it
        # directly by key based on `active_panel`. Light mode is untouched.

        if get_theme() == "dark" and active_panel:

            rail_position = {
                "suggested": 1,
                "history": 2,
                "upload": 3,
            }.get(active_panel)

            if rail_position:

                st.html(
                    f"""
                    <style>
                    [data-theme="dark"]
                    .st-key-vv-side-rail
                    .stButton:nth-of-type({rail_position})
                    > button {{
                        background: #BFEAFF !important;
                        border-color: #7DD3FC !important;
                        color: #123B63 !important;
                        box-shadow:
                            0 0 0 3px rgba(125,211,252,0.10),
                            0 0 30px rgba(56,189,248,0.35) !important;
                    }}
                    </style>
                    """
                )

        # --------------------------------------------------------------------
        # SUGGESTED
        # --------------------------------------------------------------------

        if st.button(
            "✦",
            key="vv_side_suggest",
            help="Suggested Questions",
            use_container_width=True,
        ):

            if (
                st.session_state.vv_active_side_panel
                == "suggested"
            ):

                st.session_state.vv_active_side_panel = None

            else:

                st.session_state.vv_active_side_panel = "suggested"

            st.rerun()


        # --------------------------------------------------------------------
        # HISTORY
        # --------------------------------------------------------------------

        if st.button(
            "◷",
            key="vv_side_history",
            help="History",
            use_container_width=True,
        ):

            if (
                st.session_state.vv_active_side_panel
                == "history"
            ):

                st.session_state.vv_active_side_panel = None

            else:

                st.session_state.vv_active_side_panel = "history"

            st.rerun()


        # --------------------------------------------------------------------
        # UPLOAD VEHICLE
        # --------------------------------------------------------------------

        if st.button(
            "🚗",
            key="vv_side_upload",
            help="Upload Vehicle",
            use_container_width=True,
        ):

            if (
                st.session_state.vv_active_side_panel
                == "upload"
            ):

                st.session_state.vv_active_side_panel = None

            else:

                st.session_state.vv_active_side_panel = "upload"

            st.rerun()


# ============================================================================
# OPEN SIDE PANEL
# ============================================================================

if side_is_open:

    with side_col:

        with st.container(
            key="vv-side-panel"
        ):

            # ----------------------------------------------------------------
            # PANEL HEADER
            # ----------------------------------------------------------------

            panel_titles = {
                "suggested": "Suggested",
                "history": "History",
                "upload": "Upload",
            }

            panel_icons = {
                "suggested": "✦",
                "history": "◷",
                "upload": "🚗",
            }

            st.html(
                f"""
                <div class="vv-panel-heading">

                    <div class="vv-panel-title">

                        <span class="vv-panel-title-icon">
                            {panel_icons[active_panel]}
                        </span>

                        <span>
                            {panel_titles[active_panel]}
                        </span>

                    </div>

                    <span class="vv-panel-status">
                        LIVE
                    </span>

                </div>
                """
            )


            # ----------------------------------------------------------------
            # SUGGESTED QUESTIONS
            # ----------------------------------------------------------------

            if active_panel == "suggested":

                st.html(
                    f"""
                    <p class="vv-side-description">
                        {t("chat_suggested_desc")}
                    </p>
                    """
                )

                suggested_keys = [
                    "sugg_fuel",
                    "sugg_hp",
                    "sugg_maintenance",
                    "sugg_reliability",
                    "sugg_price",
                    "sugg_alternatives",
                ]

                for icon, key in zip(
                    SUGGESTED_ICONS,
                    suggested_keys,
                ):

                    if st.button(
                        t(key),
                        icon=icon,
                        key=f"chat_suggest_{key}",
                        use_container_width=True,
                    ):

                        st.session_state[
                            "_pending_prompt"
                        ] = t(key)

                        st.session_state[
                            "vv_active_side_panel"
                        ] = None

                        st.rerun()


            # ----------------------------------------------------------------
            # HISTORY
            # ----------------------------------------------------------------

            elif active_panel == "history":

                messages = st.session_state.get(
                    "chat_messages",
                    [],
                )

                if messages:

                    st.html(
                        f"""
                        <div class="vv-history-count">

                            <span>
                                Conversation
                            </span>

                            <strong>
                                {len(messages)}
                            </strong>

                        </div>
                        """
                    )

                    for index, message in enumerate(
                        messages[-6:]
                    ):

                        role = message.get(
                            "role",
                            "",
                        )

                        content = str(
                            message.get(
                                "content",
                                "",
                            )
                        )

                        preview = content[:70]

                        if len(content) > 70:
                            preview += "..."

                        role_icon = (
                            "◉"
                            if role == "user"
                            else "✦"
                        )

                        st.html(
                            f"""
                            <div class="vv-history-item">

                                <div class="vv-history-icon">
                                    {role_icon}
                                </div>

                                <div class="vv-history-text">
                                    {preview}
                                </div>

                            </div>
                            """
                        )

                else:

                    st.html(
                        """
                        <div class="vv-empty-history">

                            <div class="vv-empty-history-icon">
                                ◷
                            </div>

                            <strong>
                                No conversations yet
                            </strong>

                            <span>
                                Your recent questions will appear here.
                            </span>

                        </div>
                        """
                    )


            # ----------------------------------------------------------------
            # UPLOAD
            # ----------------------------------------------------------------

            elif active_panel == "upload":

                st.html(
                    """
                    <div class="vv-cosmic-upload">

                        <div class="vv-upload-orbit">

                            <span></span>
                            <span></span>
                            <span></span>

                            <div class="vv-upload-core">
                                🚗
                            </div>

                        </div>


                        <strong>
                            Vehicle Scanner
                        </strong>


                        <span>
                            Drop a vehicle image into the AI zone.
                        </span>

                    </div>
                    """
                )

                uploaded_file = st.file_uploader(
                    "Upload vehicle image",
                    type=[
                        "png",
                        "jpg",
                        "jpeg",
                        "webp",
                    ],
                    key="vv_vehicle_upload",
                    label_visibility="collapsed",
                )

                if uploaded_file:

                    st.image(
                        uploaded_file,
                        use_container_width=True,
                    )

                    st.html(
                        """
                        <div class="vv-upload-ready">

                            <span class="vv-upload-ready-dot"></span>

                            Image loaded successfully

                        </div>
                        """
                    )


            # ----------------------------------------------------------------
            # CLOSE
            # ----------------------------------------------------------------

            if st.button(
                "×",
                key="vv_close_panel",
                help="Close panel",
                use_container_width=True,
            ):

                st.session_state.vv_active_side_panel = None

                st.rerun()