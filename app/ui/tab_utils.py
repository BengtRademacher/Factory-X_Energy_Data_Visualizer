"""Shared helpers for tab rendering."""

from __future__ import annotations

from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from app.config import PLOT_DEFAULTS
from app.data_manager import ProcessedData
from app.export import export_plots
from app.x_axis import XAxisResolution, resolve_processed_x_axis

_X_AXIS_CACHE_KEY = "_cached_processed_x_axes"


def ensure_has_data(processed, message: str) -> bool:
    """Show an info message and stop rendering when no data is available."""
    if not processed.has_data:
        st.info(message)
        return False
    return True


def ensure_valid_ranges(options: dict, message: str = "Invalid axis ranges.") -> bool:
    """Show a warning and stop rendering when axis ranges are invalid."""
    if not options.get("ranges_valid", True):
        st.warning(message)
        return False
    return True


def figure_size_from_options(options: dict) -> tuple[float, float]:
    """Calculate figure size from sidebar options (mm -> inches)."""
    width_mm = float(options.get("plot_width", PLOT_DEFAULTS.width))
    height_mm = float(options.get("plot_height", PLOT_DEFAULTS.height))
    return (width_mm / 25.4, height_mm / 25.4)


def parse_optional_float(value: str | None) -> tuple[float | None, bool]:
    """Parse a blankable numeric input."""
    normalized = (value or "").strip()
    if not normalized:
        return (None, False)

    try:
        return (float(normalized.replace(",", ".")), False)
    except ValueError:
        return (None, True)


def parse_required_float(value: str | None) -> tuple[float | None, bool]:
    """Parse a required numeric input."""
    normalized = (value or "").strip()
    if not normalized:
        return (None, True)

    try:
        return (float(normalized.replace(",", ".")), False)
    except ValueError:
        return (None, True)


def format_float_input(value: object) -> str:
    """Format numeric state values for plain text inputs."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"{value:g}".replace(".", ",")
    if value is None:
        return ""
    return str(value)


def get_cached_processed_x_axis(processed: ProcessedData, column: str | None) -> XAxisResolution:
    """Memoize X-axis resolution in session state for the current upload set."""
    cache = st.session_state.setdefault(_X_AXIS_CACHE_KEY, {})
    key = (processed.upload_signature, column)
    if key not in cache:
        cache[key] = resolve_processed_x_axis(processed, column)
    return cache[key]


def sample_time_ordered_frame(
    frame: pd.DataFrame,
    max_rows: int,
) -> pd.DataFrame:
    """Downsample a time-ordered frame deterministically while preserving order."""
    if len(frame) <= max_rows:
        return frame

    indices = np.linspace(0, len(frame) - 1, num=max_rows, dtype=int)
    unique_indices = np.unique(indices)
    return frame.iloc[unique_indices].copy()


def sample_time_ordered_pair(
    frame: pd.DataFrame,
    values: pd.Series,
    max_rows: int,
) -> tuple[pd.DataFrame, pd.Series]:
    """Downsample aligned frame/series pairs with the same deterministic index set."""
    if len(frame) <= max_rows:
        return frame, values

    indices = np.linspace(0, len(frame) - 1, num=max_rows, dtype=int)
    unique_indices = np.unique(indices)
    sampled_frame = frame.iloc[unique_indices].reset_index(drop=True)
    sampled_values = values.iloc[unique_indices].reset_index(drop=True)
    return sampled_frame, sampled_values


def sample_distribution_frame(frame: pd.DataFrame, max_rows: int, random_state: int = 42) -> pd.DataFrame:
    """Downsample distribution-oriented data with a deterministic random sample."""
    if len(frame) <= max_rows:
        return frame
    return frame.sample(n=max_rows, random_state=random_state)


def render_matplotlib_figure(fig, *, width: str = "stretch") -> bool:
    """Render one Matplotlib figure if present."""
    if fig is None:
        return False
    st.pyplot(fig, width=width)
    return True


def finalize_matplotlib_figures(
    plots_to_export: Iterable[tuple[str, object]],
    options: dict,
) -> None:
    """Export and close Matplotlib figures collected by one tab."""
    plots = list(plots_to_export)
    try:
        if options.get("export_trigger") and options.get("export_format") and plots:
            export_plots(
                plots,
                options.get("export_filename", "export"),
                options.get("export_format"),
            )
    finally:
        for _, fig in plots:
            plt.close(fig)

