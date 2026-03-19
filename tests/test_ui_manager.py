"""Tests for the shared UI manager behavior."""

from __future__ import annotations

from contextlib import nullcontext
from unittest.mock import Mock, patch

import pandas as pd
import streamlit as st

from app.config import TAB_SPECS
from app.data_manager import ProcessedData
from app.ui import sidebar as sidebar_module
from app.ui.sidebar import render_sidebar
from app.ui.state import initialize_state, reset_ui_state


@patch("streamlit.sidebar")
@patch("streamlit.expander")
@patch("streamlit.warning")
def test_render_sidebar(mock_warning, mock_expander, mock_sidebar):
    """Sidebar rendering should return data-driven options."""
    mock_expander.return_value.__enter__ = Mock(return_value=None)
    mock_expander.return_value.__exit__ = Mock(return_value=None)

    processed = ProcessedData(
        combined_frame=pd.DataFrame(
            {
                "elapsedTime": pd.to_timedelta([0, 1], unit="s"),
                "power": [1.0, 2.0],
                "status": ["on", "off"],
            }
        ),
        file_boundaries=[],
        frames_by_file={},
    )
    st.session_state["x_source_column"] = None

    options = render_sidebar(processed)

    assert isinstance(options, dict)
    assert "plot_width" in options
    assert options["all_available_columns"] == ["power", "status"]
    assert options["numeric_plot_columns"] == ["power"]
    assert options["x_source_columns"] == ["elapsedTime", "power", "status"]
    assert options["x_source_column"] == "elapsedTime"
    assert st.session_state["x_source_auto_selected"] is True
    assert "component_aliases" not in options
    assert "time_column_name" not in options
    assert [call.args[0] for call in mock_expander.call_args_list] == ["Display", "Set X Range", "Set Y Range", "Export"]
    mock_warning.assert_called_once_with('Column "elapsedTime" was automatically selected as the X source.')


def test_initialize_state():
    """State initialization should populate shared session values."""
    st.session_state.clear()
    initialize_state()
    assert "plot_width" in st.session_state
    assert "line_selected_components" in st.session_state
    assert "line_stacked_enabled" in st.session_state
    assert isinstance(st.session_state["plot_width"], int)
    assert isinstance(st.session_state["plot_height"], int)
    assert st.session_state["x_source_column"] is None
    assert st.session_state["x_source_auto_selected"] is False
    assert st.session_state["line_stacked_enabled"] is False
    assert "component_aliases" not in st.session_state
    assert "time_column_name" not in st.session_state


def test_reset_ui_state_clears_data_selections():
    """Reset should remove data-driven selection fields."""
    initialize_state()
    st.session_state["line_selected_components"] = ["power"]
    st.session_state["scatter_x_select"] = "power"
    st.session_state["scatter_point_type"] = "Square"
    st.session_state["scatter_color_min"] = "1"
    st.session_state["scatter_color_max"] = "10"
    st.session_state["scatter_color_tick_step"] = "2"
    st.session_state["preview_plot_columns_demo.csv"] = ["power"]
    st.session_state["x_source_column"] = "power"
    st.session_state["x_source_column_select"] = "power"
    st.session_state["x_source_auto_selected"] = True

    reset_ui_state()

    assert "line_selected_components" not in st.session_state
    assert "scatter_x_select" not in st.session_state
    assert "scatter_point_type" not in st.session_state
    assert "scatter_color_min" not in st.session_state
    assert "scatter_color_max" not in st.session_state
    assert "scatter_color_tick_step" not in st.session_state
    assert "preview_plot_columns_demo.csv" not in st.session_state
    assert "x_source_column" not in st.session_state
    assert "x_source_column_select" not in st.session_state
    assert "x_source_auto_selected" not in st.session_state


def test_tab_specs_have_material_labels():
    """Each tab should expose an internal title and a Material label."""
    assert len(TAB_SPECS) == 8
    assert TAB_SPECS[0].title == "Data Processing"
    assert TAB_SPECS[1].title == "Line Plots"
    assert TAB_SPECS[2].title == "Bar Charts"
    assert TAB_SPECS[-1].title == "Sankey"
    assert all(tab.label.startswith(":material/") for tab in TAB_SPECS)


def test_display_section_uses_blank_ranges_for_auto(monkeypatch):
    recorded = {"captions": [], "expanders": []}

    class DummyColumn:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def text_input(self, label, key=None, value="", **kwargs):
            current = st.session_state.get(key, value)
            st.session_state[key] = current
            return current

    def fake_expander(label, **kwargs):
        recorded["expanders"].append(label)
        return nullcontext()

    def fake_selectbox(label, options, index=0, key=None, **kwargs):
        value = st.session_state.get(key, options[index])
        st.session_state[key] = value
        return value

    def fake_slider(label, min_value=None, max_value=None, step=None, key=None, **kwargs):
        current = st.session_state.get(key, min_value)
        st.session_state[key] = current
        return current

    def fake_text_input(label, key=None, value="", **kwargs):
        current = st.session_state.get(key, value)
        st.session_state[key] = current
        return current

    monkeypatch.setattr(sidebar_module.st, "expander", fake_expander)
    monkeypatch.setattr(sidebar_module.st, "caption", lambda text, **kwargs: recorded["captions"].append(text))
    monkeypatch.setattr(sidebar_module.st, "selectbox", fake_selectbox)
    monkeypatch.setattr(sidebar_module.st, "slider", fake_slider)
    monkeypatch.setattr(sidebar_module.st, "text_input", fake_text_input)
    monkeypatch.setattr(sidebar_module.st, "columns", lambda spec: [DummyColumn(), DummyColumn()])
    monkeypatch.setattr(sidebar_module.st, "divider", lambda *args, **kwargs: None)
    monkeypatch.setattr(sidebar_module.st, "warning", lambda *args, **kwargs: None)
    monkeypatch.setattr(sidebar_module.st, "info", lambda *args, **kwargs: None)

    st.session_state.clear()
    st.session_state["x_source_column"] = "elapsedTime"
    st.session_state["x_source_column_select"] = "elapsedTime"
    st.session_state["x_min_ui"] = ""
    st.session_state["x_max_ui"] = ""
    st.session_state["y_min_ui"] = "0"
    st.session_state["y_max_ui"] = "100"

    ranges_valid = sidebar_module._render_display_section(
        x_source_columns=["elapsedTime", "power"],
        x_max_default=10.0,
        y_max_default=100.0,
        x_source_error=None,
    )

    assert ranges_valid is True
    assert "Data Source" not in recorded["captions"]
    assert recorded["expanders"] == ["Display", "Set X Range", "Set Y Range"]
    assert st.session_state["set_x_range"] is False
    assert st.session_state["set_y_range"] is True
