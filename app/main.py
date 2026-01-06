"""Hauptmodul für den Factory-X_Energy_Data_Visualizer.

Orchestriert die UI-Komponenten und Datenverarbeitung.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import streamlit as st

from app.config import APP_TITLE, LOGO_FILENAME, TAB_NAMES, TAB_ICONS
from app.data_manager import DataManager
from app.preprocessor import DataPreprocessor, PreprocessConfig
from app.ui.sidebar import render_sidebar
from app.ui.tabs import (
    data_processing,
    line_plots,
    bar_plots,
    box_plots,
    donut_plots,
    scatter_plots,
    histogram_plots,
    sankey_plots,
)


_APP_ROOT = Path(__file__).resolve().parents[1]
_LOGO_PATH = _APP_ROOT / "assets" / LOGO_FILENAME
_STYLE_PATH = _APP_ROOT / "assets" / "FX_style_top_right.svg"


def _get_base64(path: Path) -> str:
    """Lädt eine Datei als Base64-String."""
    if not path.exists():
        return ""
    import base64
    with path.open("rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _inject_styles() -> None:
    """Injiziert globale CSS-Styles."""
    style_base64 = _get_base64(_STYLE_PATH)
    
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

    st.markdown(f"""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
<style>
    {bg_style}
    .material-symbols-rounded {{
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        font-family: 'Material Symbols Rounded';
        vertical-align: middle;
        margin-right: 8px;
    }}
    /* Vergrößert das st.logo und passt den Container an, damit nichts abgeschnitten wird */
    [data-testid="stSidebarHeader"] {{
        height: 120px !important;
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }}
    [data-testid="stSidebarHeader"] img {{
        height: 100px !important;
        width: auto !important;
    }}
    /* Sicherstellen, dass der Content über dem Hintergrund liegt und Platz oben reduzieren */
    [data-testid="stMainBlockContainer"] {{
        position: relative;
        z-index: 1;
        padding-top: 2rem !important;
    }}
    /* Header und Toolbar transparent machen, damit das SVG durchscheint */
    header[data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    [data-testid="stToolbar"] {{
        background-color: transparent !important;
    }}
    /* Die Buttons selbst und das Design-Element (stDecoration) bleiben sichtbar */
    [data-testid="stDecoration"] {{
        visibility: visible !important;
    }}
</style>
""", unsafe_allow_html=True)


class PlottingApp:
    """Hauptanwendungsklasse."""
    
    def __init__(self, data_manager: DataManager | None = None) -> None:
        self.data_manager = data_manager or DataManager()
        self.preprocessor = DataPreprocessor()
    
    def run(self) -> None:
        """Startet die Anwendung."""
        st.set_page_config(layout="wide", page_title=APP_TITLE)
        
        # Initialisiere State ganz am Anfang
        from app.ui.state import initialize_state
        initialize_state()
        
        # Flag für den Export-Toast zurücksetzen (verhindert doppelte Toasts)
        st.session_state["export_toast_shown"] = False
        
        # Logo in die Sidebar setzen
        if _LOGO_PATH.exists():
            st.logo(str(_LOGO_PATH))
        
        self._render_header()
        _inject_styles()
        
        # Datei-Upload
        uploaded_files = st.file_uploader(
            "Laden Sie Ihre Excel- oder CSV-Dateien hoch",
            type=["xlsx", "xls", "csv"],
            accept_multiple_files=True,
        )
        
        # Toast und Reset bei erstem Import
        if uploaded_files and not st.session_state.get("files_imported_toast_shown"):
            st.session_state["files_imported_toast_shown"] = "pending"
            from app.ui.state import reset_ui_state
            reset_ui_state()
            st.rerun()

        if st.session_state.get("files_imported_toast_shown") == "pending":
            st.toast("Dateien erfolgreich importiert!", icon="✅")
            st.session_state["files_imported_toast_shown"] = True
        
        # Daten laden und verarbeiten
        processed = self.data_manager.load_files(uploaded_files or [])
        
        # Sidebar rendern und Optionen erhalten
        sidebar_options = render_sidebar(
            processed.combined_frame if processed.has_data else None
        )
        
        # Preprocessing
        preprocessed = self._preprocess_data(processed, sidebar_options)
        
        # Tabs rendern
        self._render_tabs(preprocessed, sidebar_options)
    
    def _render_header(self) -> None:
        """Rendert den App-Header."""
        st.markdown(
            f"""
            <div style='display:flex; align-items:center; gap:24px; margin-bottom:1rem;'>
                <span style='font-size:48px; font-weight:700; letter-spacing:0.8px;'>
                    {APP_TITLE}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    def _preprocess_data(self, processed, options: dict):
        """Wendet Preprocessing auf die Daten an."""
        aliases = options.get("component_aliases", {})
        start = options.get("time_range_start")
        end = options.get("time_range_end")
        time_range = None
        if start is not None or end is not None:
            time_range = (start, end)
        
        config = PreprocessConfig(
            component_aliases=aliases,
            time_range=time_range,
            time_column=options.get("time_column_name"),
        )
        return self.preprocessor.run(processed, config)
    
    def _render_tabs(self, processed, options: dict) -> None:
        """Rendert alle Tabs."""
        tabs = st.tabs(TAB_NAMES)
        
        # Tab-Module mapping
        tab_modules = [
            data_processing,
            line_plots,
            bar_plots,
            box_plots,
            donut_plots,
            scatter_plots,
            histogram_plots,
            sankey_plots,
        ]
        
        for i, (tab, module) in enumerate(zip(tabs, tab_modules)):
            with tab:
                # Tab-Header mit Icon
                icon = TAB_ICONS.get(TAB_NAMES[i], "")
                if icon:
                    st.markdown(
                        f'<span class="material-symbols-rounded">{icon}</span> {TAB_NAMES[i]}',
                        unsafe_allow_html=True
                    )
                
                # Tab-Inhalt rendern
                module.render(processed, options)


def run_app() -> None:
    """Einstiegspunkt für die Anwendung."""
    PlottingApp(data_manager=DataManager()).run()


if __name__ == "__main__":
    run_app()
