"""Entry point for the Factory-X_Energy_Data_Visualizer.

Start the application with:
    streamlit run app.py
"""

import streamlit as st
import base64
from pathlib import Path
from app.main import run_app
from app.config import APP_TITLE, LOGO_FILENAME, COLOR_PALETTE

# --- Styling & Branding (Consistent with Audit-App) ---

def _get_base64(path: Path) -> str:
    """Lädt eine Datei als Base64-String."""
    if not path.exists():
        return ""
    with path.open("rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def inject_custom_styles():
    """Injiziert globale CSS-Styles für Branding und Layout-Verbesserungen."""
    logo_path = Path("assets") / LOGO_FILENAME
    style_path = Path("assets/FX_style_top_right.svg")
    
    # Hintergrundkonfiguration (Blau mit Transparenz)
    bg_color_hex = COLOR_PALETTE.get("Blau", "#006DB9")
    bg_opacity = 0.25
    
    # Hex zu RGB Konvertierung für die Nutzung in rgba()
    h = bg_color_hex.lstrip('#')
    r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    rgba_bg = f"rgba({r}, {g}, {b}, {bg_opacity})"
    
    # Base64 für das Hintergrund-SVG laden
    style_base64 = _get_base64(style_path)
    
    # CSS für das Hintergrund-SVG
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

    # Gesamtes Styling-Paket injizieren
    st.markdown(f"""
    <!-- Google Material Symbols -->
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0" />
    
    <style>
        /* 1. Globaler Hintergrund */
        /* --- START BACKGROUND FADE SNIPPET --- */
        /* Haupt-Hintergrund mit Radial Gradient (Fokus oben links, Rest transparent) */
        [data-testid="stAppViewContainer"] {{
            background: radial-gradient(
                circle at top left, 
                {rgba_bg} 0%, 
                rgba(255, 255, 255, 0) 70%
            ) !important;
            background-attachment: fixed !important;
        }}
        /* --- END BACKGROUND FADE SNIPPET --- */
        
        /* 2. Hintergrund-SVG */
        {bg_style}
        
        /* 3. Sidebar Header & Logo */
        [data-testid="stSidebarHeader"] {{
            height: 120px !important;
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }}
        [data-testid="stSidebarHeader"] img {{
            height: 100px !important;
            width: auto !important;
        }}
        
        /* 4. Main Container Adjustments */
        [data-testid="stMainBlockContainer"] {{
            position: relative;
            z-index: 1;
            padding-top: 2rem !important;
        }}
        
        /* 5. Transparent Header/Toolbar */
        header[data-testid="stHeader"], [data-testid="stToolbar"] {{
            background-color: transparent !important;
        }}
        
        /* 6. Material Icons Integration */
        .material-symbols-rounded {{
            font-family: 'Material Symbols Rounded';
            vertical-align: middle;
            margin-right: 8px;
            font-variation-settings: 'opsz' 24;
        }}

        /* stDecoration sichtbar lassen */
        [data-testid="stDecoration"] {{
            visibility: visible !important;
        }}
    </style>
    """, unsafe_allow_html=True)

    # Logo in die Sidebar setzen
    if logo_path.exists():
        st.logo(str(logo_path))


if __name__ == "__main__":
    # Page Config initialisieren
    st.set_page_config(
        page_title=APP_TITLE,
        layout="wide"
    )
    
    # Branding & Styling
    inject_custom_styles()
    
    # App starten
    run_app()
