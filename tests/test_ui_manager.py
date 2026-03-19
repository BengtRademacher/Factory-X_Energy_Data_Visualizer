"""Tests for the shared UI manager behavior."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pandas as pd
import streamlit as st

from app.config import TAB_SPECS
from app.data_manager import ProcessedData
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
    assert [call.args[0] for call in mock_expander.call_args_list] == ["Display", "Export"]
    mock_warning.assert_called_once_with('Column "elapsedTime" was automatically selected as the X source.')


def test_initialize_state():
    """State initialization should populate shared session values."""
    st.session_state.clear()
    initialize_state()
    assert "plot_width" in st.session_state
    assert "line_selected_components" in st.session_state
    assert isinstance(st.session_state["plot_width"], int)
    assert isinstance(st.session_state["plot_height"], int)
    assert st.session_state["x_source_column"] is None
    assert st.session_state["x_source_auto_selected"] is False
    assert "component_aliases" not in st.session_state
    assert "time_column_name" not in st.session_state


def test_reset_ui_state_clears_data_selections():
    """Reset should remove data-driven selection fields."""
    initialize_state()
    st.session_state["line_selected_components"] = ["power"]
    st.session_state["scatter_x_select"] = "power"
    st.session_state["preview_plot_columns_demo.csv"] = ["power"]
    st.session_state["x_source_column"] = "power"
    st.session_state["x_source_column_select"] = "power"
    st.session_state["x_source_auto_selected"] = True

    reset_ui_state()

    assert "line_selected_components" not in st.session_state
    assert "scatter_x_select" not in st.session_state
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
