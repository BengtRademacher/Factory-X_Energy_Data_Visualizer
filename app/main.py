"""Main application module for the Factory-X Energy Data Visualizer."""

from __future__ import annotations

import streamlit as st

from app.config import APP_TITLE
from app.data_manager import DataManager, LoadDiagnostic
from app.ui.sidebar import render_sidebar
from app.ui.tabs import TAB_BY_TITLE, TAB_REGISTRY


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
        self._render_diagnostics(processed.diagnostics)
        sidebar_options = render_sidebar(processed)
        self._render_tab_selector()
        self._render_active_tab(processed, sidebar_options)

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

    def _render_tab_selector(self) -> None:
        """Render a single active-tab selector to avoid eager tab rendering."""
        available_titles = [tab.title for tab in TAB_REGISTRY]
        current = st.session_state.get("active_tab_name")
        if current not in available_titles:
            st.session_state["active_tab_name"] = available_titles[0]

        st.segmented_control(
            "Section",
            options=available_titles,
            key="active_tab_name",
            label_visibility="collapsed",
            format_func=lambda title: TAB_BY_TITLE[title].label,
            selection_mode="single",
            width="stretch",
        )

    def _render_active_tab(self, processed, options: dict) -> None:
        """Render only the selected tab."""
        active_title = st.session_state.get("active_tab_name")
        tab_definition = TAB_BY_TITLE.get(active_title) or TAB_REGISTRY[0]
        tab_definition.module.render(processed, options)

    def _render_diagnostics(self, diagnostics: list[LoadDiagnostic]) -> None:
        """Display diagnostics from the data pipeline."""
        for diagnostic in diagnostics:
            message = diagnostic.message
            if diagnostic.file_name:
                message = f"{message} ({diagnostic.file_name})"

            if diagnostic.level == "info":
                st.info(message)
            else:
                st.warning(message)


def run_app() -> None:
    """Application entry point."""
    PlottingApp(data_manager=DataManager()).run()


if __name__ == "__main__":
    run_app()
