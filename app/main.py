"""Main application module for the Factory-X Energy Data Visualizer."""

from __future__ import annotations

import streamlit as st

from app.config import APP_TITLE, TAB_SPECS
from app.data_manager import DataManager
from app.ui.sidebar import render_sidebar
from app.ui.tabs import (
    bar_plots,
    box_plots,
    data_processing,
    donut_plots,
    histogram_plots,
    line_plots,
    sankey_plots,
    scatter_plots,
)


class PlottingApp:
    """Top-level Streamlit application wrapper."""

    def __init__(self, data_manager: DataManager | None = None) -> None:
        self.data_manager = data_manager or DataManager()

    def run(self) -> None:
        """Run the application."""
        from app.ui.state import initialize_state, reset_ui_state

        initialize_state()
        st.session_state["export_toast_shown"] = False
        self._render_header()

        uploaded_files = st.file_uploader(
            "File Upload",
            type=["xlsx", "xls", "csv"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        if uploaded_files and not st.session_state.get("files_imported_toast_shown"):
            st.session_state["files_imported_toast_shown"] = "pending"
            reset_ui_state()
            st.rerun()

        if st.session_state.get("files_imported_toast_shown") == "pending":
            st.toast("Files imported successfully.", icon=":material/check_circle:")
            st.session_state["files_imported_toast_shown"] = True

        processed = self.data_manager.load_files(uploaded_files or [])
        sidebar_options = render_sidebar(processed)
        self._render_tabs(processed, sidebar_options)

    def _render_header(self) -> None:
        """Render the app header."""
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

    def _render_tabs(self, processed, options: dict) -> None:
        """Render all application tabs."""
        tabs = st.tabs([tab.label for tab in TAB_SPECS])
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

        for tab, module in zip(tabs, tab_modules):
            with tab:
                module.render(processed, options)


def run_app() -> None:
    """Application entry point."""
    PlottingApp(data_manager=DataManager()).run()


if __name__ == "__main__":
    run_app()
