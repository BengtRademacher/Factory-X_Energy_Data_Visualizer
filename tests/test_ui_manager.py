"""Tests für die UI-Komponenten."""

from __future__ import annotations

from unittest.mock import patch, Mock

import pandas as pd
import streamlit as st

from app.ui.state import initialize_state
from app.ui.sidebar import render_sidebar


@patch('streamlit.sidebar')
@patch('streamlit.expander')
def test_render_sidebar(mock_expander, mock_sidebar):
    """Test dass render_sidebar ein Dictionary zurückgibt."""
    mock_expander.return_value.__enter__ = Mock(return_value=None)
    mock_expander.return_value.__exit__ = Mock(return_value=None)
    
    # Mit leerem DataFrame
    options = render_sidebar(None)
    assert isinstance(options, dict)
    assert 'plot_width' in options


def test_initialize_state():
    """Test dass initialize_state die Session-State-Variablen setzt."""
    initialize_state()
    assert 'plot_width' in st.session_state
    assert 'line_selected_components' in st.session_state
