import base64
from pathlib import Path

import streamlit as st

from utils.i18n import t, is_rtl


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
# GET ROBOT IMAGE
# (4 modes: dark/light x ar/en)
# ============================================================

def get_upload_robot_image() -> str:

    frontend_dir = Path(__file__).resolve().parent.parent
    img_dir = frontend_dir / "img"

    theme = st.session_state.get(
        "theme",
        "light",
    )

    language = st.session_state.get(
        "lang",
        "en",
    )

    if theme == "dark":
        if language == "ar":
            filename = "robot_dark_AR_page2.png"
        else:
            filename = "robot_dark_EN_page2.png"

    else:
        if language == "ar":
            filename = "robot_light_AR_page2.png"
        else:
            filename = "robot_light_EN_page2.png"

    image_path = img_dir / filename

    return load_image_as_data_uri(
        str(image_path)
    )


# ============================================================
# UPLOAD ZONE
# ============================================================

def render_upload_zone():

    robot_uri = get_upload_robot_image()

    theme = st.session_state.get("theme", "light")

    if theme == "dark":
        box_bg = "#0D1323"
        box_border = "#1D2940"
        box_border_hover = "#3B82F6"
    else:
        box_bg = "#FFFFFF"
        box_border = "#BAE6FD"
        box_border_hover = "#60A5FA"

    # ========================================================
    # CSS
    # NOTE: the real element is a <section>, not a <div>,
    # in this Streamlit version. Selectors below target
    # section[data-testid="stFileUploaderDropzone"].
    # ========================================================

    st.markdown(
        f"""
        <style>

        /* ====================================================
           OUTER WRAPPER
           ==================================================== */

        div[data-testid="stFileUploader"] {{
            width: 100% !important;
            max-width: 100% !important;

            margin: 0 !important;
            padding: 0 !important;

            box-sizing: border-box !important;
        }}


        /* ====================================================
           DROPZONE (now a <section>)
           ==================================================== */

        section[data-testid="stFileUploaderDropzone"] {{
            position: relative !important;

            width: 100% !important;
            height: 330px !important;
            min-height: 330px !important;

            margin: 0 !important;
            padding: 0 !important;

            box-sizing: border-box !important;

            overflow: hidden !important;

            display: block !important;

            border: 2px dashed {box_border} !important;

            border-radius: 20px !important;

            background-color: {box_bg} !important;

            background-image: none !important;

            box-shadow: none !important;

            transition: border-color 0.2s ease !important;
        }}


        /* ====================================================
           ROBOT IMAGE
           ==================================================== */

        section[data-testid="stFileUploaderDropzone"]::after {{
            content: "" !important;

            position: absolute !important;

            left: 50% !important;
            top: 50% !important;

            width: 94% !important;
            height: 90% !important;

            transform: translate(-50%, -50%) !important;

            background-image: url("{robot_uri}") !important;

            background-repeat: no-repeat !important;

            background-position: center center !important;

            background-size: contain !important;

            display: block !important;

            pointer-events: none !important;

            z-index: 2 !important;
        }}


        /* ====================================================
           HIDE STREAMLIT DEFAULT TEXT / SUBTEXT
           ==================================================== */

        section[data-testid="stFileUploaderDropzone"]
        div[data-testid="stFileUploaderDropzoneInstructions"] {{
            display: none !important;
        }}


        /* ====================================================
           REMOVE INTERNAL BACKGROUNDS
           ==================================================== */

        section[data-testid="stFileUploaderDropzone"] > * {{
            background: transparent !important;
            background-color: transparent !important;
            box-shadow: none !important;
        }}


        /* ====================================================
           REAL UPLOAD BUTTON
           MAKE IT COVER THE WHOLE DROPZONE SO THE ENTIRE
           ROBOT IMAGE IS CLICKABLE
           ==================================================== */

        section[data-testid="stFileUploaderDropzone"]
        button[data-testid="stBaseButton-secondary"] {{
            position: absolute !important;

            inset: 0 !important;

            width: 100% !important;
            height: 100% !important;

            min-width: 100% !important;
            min-height: 100% !important;

            max-width: 100% !important;
            max-height: 100% !important;

            margin: 0 !important;
            padding: 0 !important;

            border: none !important;

            border-radius: 20px !important;

            background: transparent !important;
            background-color: transparent !important;

            color: transparent !important;

            box-shadow: none !important;

            cursor: pointer !important;

            z-index: 20 !important;
        }}


        /* hide the button's icon + "Upload" label text */

        section[data-testid="stFileUploaderDropzone"]
        button[data-testid="stBaseButton-secondary"] * {{
            opacity: 0 !important;
            visibility: hidden !important;
        }}


        /* ====================================================
           HOVER
           ==================================================== */

        section[data-testid="stFileUploaderDropzone"]:hover {{
            border-color: {box_border_hover} !important;
            background-color: {box_bg} !important;
        }}


        /* ====================================================
           FILE AFTER UPLOAD
           ==================================================== */

        div[data-testid="stFileUploaderFile"] {{
            margin-top: 8px !important;
        }}


        /* ====================================================
           TABLET
           ==================================================== */

        @media (max-width: 900px) {{

            section[data-testid="stFileUploaderDropzone"] {{
                height: 290px !important;
                min-height: 290px !important;
            }}

        }}


        /* ====================================================
           MOBILE
           ==================================================== */

        @media (max-width: 700px) {{

            section[data-testid="stFileUploaderDropzone"] {{
                height: 240px !important;
                min-height: 240px !important;

                border-radius: 16px !important;
            }}

            section[data-testid="stFileUploaderDropzone"]
            button[data-testid="stBaseButton-secondary"] {{
                border-radius: 16px !important;
            }}

        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


    # ========================================================
    # REAL STREAMLIT FILE UPLOADER
    # ========================================================

    uploaded = st.file_uploader(
        label=t("upload_title"),

        type=[
            "jpg",
            "jpeg",
            "png",
            "webp",
        ],

        label_visibility="collapsed",

        key="vehicle_image_uploader",
    )


    # ========================================================
    # RETURN FILE
    # ========================================================

    return uploaded