"""Entry point for the Factory-X Energy Data Visualizer.

Start the application with:
    streamlit run app.py
"""

import base64
from pathlib import Path

import streamlit as st

from app.config import APP_TITLE, COLOR_PALETTE, LOGO_FILENAME
from app.main import run_app


def _get_base64(path: Path) -> str:
    """Load one file as a Base64 string."""
    if not path.exists():
        return ""
    with path.open("rb") as file_handle:
        return base64.b64encode(file_handle.read()).decode("utf-8")


def inject_custom_styles() -> None:
    """Inject global CSS styles for branding and layout refinement."""
    logo_path = Path("assets") / LOGO_FILENAME
    style_path = Path("assets/FX_style_top_right.svg")

    bg_color_hex = COLOR_PALETTE.get("Blue", "#006DB9")
    bg_opacity = 0.25

    hex_value = bg_color_hex.lstrip("#")
    red, green, blue = tuple(int(hex_value[index:index + 2], 16) for index in (0, 2, 4))
    rgba_bg = f"rgba({red}, {green}, {blue}, {bg_opacity})"

    style_base64 = _get_base64(style_path)

    bg_style = ""
    if style_base64:
        bg_style = f"""
        [data-testid="stAppViewContainer"]::before {{
            content: "";
            position: fixed;
            top: -5px;
            right: -5px;
            width: 400px;
            height: 400px;
            background-image: url('data:image/svg+xml;base64,{style_base64}');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: top right;
            opacity: 0.4;
            transform: rotate(180deg);
            pointer-events: none;
            z-index: 0;
        }}
        """

    st.markdown(
        f"""
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0" />

        <style>
            :root {{
                --fx-surface: rgba(255, 255, 255, 0.9);
                --fx-surface-strong: rgba(255, 255, 255, 0.96);
                --fx-surface-muted: #f6f8fb;
                --fx-surface-subtle: #fbfcfe;
                --fx-border: #d8e1eb;
                --fx-border-strong: #c6d1dc;
                --fx-text-soft: #506070;
                --fx-text-muted: #6e7d8d;
                --fx-accent-soft: rgba({red}, {green}, {blue}, 0.1);
                --fx-shadow: 0 14px 36px rgba(24, 39, 75, 0.08);
            }}

            [data-testid="stAppViewContainer"] {{
                background: radial-gradient(
                    circle at top left,
                    {rgba_bg} 0%,
                    rgba(255, 255, 255, 0) 70%
                ) !important;
                background-attachment: fixed !important;
            }}

            html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
            [data-testid="stMainBlockContainer"], button, input, textarea, select,
            label, p, h1, h2, h3, h4, h5, h6, li, a, div {{
                font-family: "Aptos", "Segoe UI", sans-serif !important;
            }}

            {bg_style}

            [data-testid="stSidebarHeader"] {{
                height: 120px !important;
                padding-top: 1rem !important;
                padding-bottom: 1rem !important;
            }}

            [data-testid="stSidebarHeader"] img {{
                height: 100px !important;
                width: auto !important;
            }}

            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3 {{
                font-size: calc(1rem + 2pt) !important;
            }}

            [data-testid="stSidebar"] [data-testid="stExpander"] summary,
            [data-testid="stSidebar"] [data-testid="stExpander"] summary p,
            [data-testid="stSidebar"] [data-testid="stExpander"] summary span {{
                font-size: calc(1rem + 2pt) !important;
                line-height: 1.2 !important;
            }}

            [data-testid="stSidebar"] [data-testid="stExpander"] {{
                background: var(--fx-surface-strong) !important;
                border: 1px solid var(--fx-border) !important;
                border-radius: 16px !important;
                overflow: hidden !important;
                margin-bottom: 1rem !important;
                box-shadow: 0 10px 24px rgba(24, 39, 75, 0.04) !important;
            }}

            [data-testid="stSidebar"] [data-testid="stExpander"] details {{
                background: var(--fx-surface-strong) !important;
                border: none !important;
                border-radius: 16px !important;
            }}

            [data-testid="stSidebar"] [data-testid="stExpander"] summary {{
                background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(246,248,251,0.98)) !important;
                padding: 0.65rem 0.8rem !important;
            }}

            [data-testid="stSidebar"] [data-testid="stExpanderDetails"] {{
                background: var(--fx-surface-strong) !important;
                padding: 0 0.8rem 0.8rem !important;
            }}

            [data-testid="stMainBlockContainer"] {{
                position: relative;
                z-index: 1;
                padding-top: 2rem !important;
            }}

            [data-testid="stVerticalBlockBorderWrapper"] {{
                border-radius: 18px !important;
                border: 1px solid var(--fx-border) !important;
                background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,253,0.95)) !important;
                box-shadow: var(--fx-shadow) !important;
            }}

            [data-testid="stVerticalBlockBorderWrapper"] > div {{
                padding: 0.15rem 0.2rem !important;
            }}

            header[data-testid="stHeader"], [data-testid="stToolbar"] {{
                background-color: transparent !important;
            }}

            .material-symbols-rounded {{
                font-family: "Material Symbols Rounded";
                vertical-align: middle;
                margin-right: 8px;
                font-variation-settings: "opsz" 24;
            }}

            [data-baseweb="tab"] {{
                font-size: calc(1rem + 4pt) !important;
            }}

            [data-baseweb="tab"] p {{
                font-size: calc(1rem + 4pt) !important;
                line-height: 1.2 !important;
            }}

            [data-testid="stTabs"]::after {{
                content: none !important;
                display: none !important;
                background: transparent !important;
                box-shadow: none !important;
            }}

            [data-testid="stFileUploaderDropzone"] {{
                position: relative;
                overflow: visible;
            }}

            [data-testid="stFileUploaderDropzoneInstructions"] small {{
                visibility: hidden;
                position: relative;
            }}

            [data-testid="stFileUploaderDropzoneInstructions"] small::after {{
                content: "Maximum 200 MB - supported formats: csv, xlsx, xls";
                visibility: visible;
                position: absolute;
                top: 0;
                left: 0;
                color: inherit;
                font-size: 0.875rem;
                line-height: 1.4;
                white-space: nowrap;
            }}

            [data-testid="stSidebar"] .st-key-export_png_button button,
            [data-testid="stSidebar"] .st-key-export_pdf_button button,
            [data-testid="stSidebar"] .st-key-export_svg_button button,
            [data-testid="stSidebar"] .st-key-export_eps_button button {{
                min-height: 4.75rem !important;
                padding: 0.75rem !important;
                white-space: pre-line !important;
                text-align: center !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                line-height: 1.25 !important;
                border-radius: 14px !important;
                border: 1px solid var(--fx-border-strong) !important;
                background: linear-gradient(180deg, #ffffff 0%, #f4f7fb 100%) !important;
            }}

            [data-testid="stDecoration"] {{
                visibility: visible !important;
            }}

            .fx-panel-header {{
                display: flex;
                flex-direction: column;
                gap: 0.45rem;
                margin-bottom: 1rem;
            }}

            .fx-panel-eyebrow {{
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: {bg_color_hex};
            }}

            .fx-panel-title {{
                font-size: 1.2rem;
                font-weight: 700;
                line-height: 1.2;
                color: #152231;
            }}

            .fx-panel-copy {{
                margin: 0;
                color: var(--fx-text-soft);
                line-height: 1.45;
                font-size: 0.95rem;
            }}

            .fx-kpi-row {{
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
                margin-top: 0.15rem;
            }}

            .fx-kpi-chip {{
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                padding: 0.42rem 0.7rem;
                border-radius: 999px;
                border: 1px solid var(--fx-border);
                background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(241,246,252,0.98));
                color: #1d2a39;
                font-size: 0.85rem;
                line-height: 1.2;
            }}

            .fx-kpi-chip__label {{
                color: var(--fx-text-muted);
                font-weight: 600;
            }}

            .fx-kpi-chip__value {{
                font-weight: 700;
            }}

            .fx-sidebar-group {{
                margin: 0.2rem 0 0.75rem;
                padding: 0.8rem 0.9rem;
                border-radius: 14px;
                border: 1px solid var(--fx-border);
                background: linear-gradient(180deg, rgba(250,252,255,0.98), rgba(243,247,251,0.98));
            }}

            .fx-sidebar-group--advanced {{
                background: linear-gradient(180deg, rgba(252,253,255,0.98), rgba(247,249,252,0.98));
                border-style: dashed;
            }}

            .fx-sidebar-group-title {{
                font-size: 0.98rem;
                font-weight: 700;
                color: #152231;
                margin-bottom: 0.2rem;
            }}

            .fx-sidebar-group-copy {{
                margin: 0;
                color: var(--fx-text-soft);
                line-height: 1.4;
                font-size: 0.87rem;
            }}

            .fx-inline-note {{
                margin: 0.2rem 0 0.85rem;
                color: var(--fx-text-soft);
                font-size: 0.9rem;
                line-height: 1.45;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    if logo_path.exists():
        st.logo(str(logo_path))


if __name__ == "__main__":
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    inject_custom_styles()
    run_app()
