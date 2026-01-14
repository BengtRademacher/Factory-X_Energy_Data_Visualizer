"""Hauptmodul für den Factory-X_Energy_Data_Visualizer.

Orchestriert die UI-Komponenten und Datenverarbeitung.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import streamlit as st

from app.config import APP_TITLE, TAB_NAMES, TAB_ICONS
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


class PlottingApp:
    """Hauptanwendungsklasse."""
    
    def __init__(self, data_manager: DataManager | None = None) -> None:
        self.data_manager = data_manager or DataManager()
        self.preprocessor = DataPreprocessor()
    
    def run(self) -> None:
        """Startet die Anwendung."""
        # Initialisiere State ganz am Anfang
        from app.ui.state import initialize_state
        initialize_state()
        
        # Flag für den Export-Toast zurücksetzen (verhindert doppelte Toasts)
        st.session_state["export_toast_shown"] = False
        
        self._render_header()
        
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
            <div style='display:flex; align-items:center; gap:16px; margin-bottom:1rem;'>
                <span class="material-symbols-rounded" style="font-size:54px; color:black;">bolt</span>
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
