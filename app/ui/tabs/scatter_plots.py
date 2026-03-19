"""Scatter plot tab for the Factory-X plotting app."""

from typing import Tuple

import pandas as pd
import streamlit as st

from app.config import MAX_PLOT_ROWS, PLOT_DEFAULTS
from app.export import export_plots
from app.plotting import plot_scatter
from app.ui.components import get_valid_selectbox_state

POINT_TYPE_OPTIONS = {
    "Circle": "o",
    "Square": "s",
    "Triangle Up": "^",
    "Triangle Down": "v",
    "Diamond": "D",
    "Plus": "+",
    "X": "x",
}


def render(processed, options: dict) -> None:
    """Render the Scatter Plot tab."""
    if not processed.has_data:
        st.info("Please upload files to create charts.")
        return

    if not options.get("ranges_valid", True):
        st.warning("Invalid axis ranges.")
        return

    main_col, custom_col = st.columns([4, 1])
    component_options = options.get("numeric_plot_columns", [])
    combined = processed.combined_frame

    with custom_col:
        st.markdown("### :material/tune: Options")

        x_options = ["-"] + component_options
        y_options = ["-"] + component_options
        color_options = ["-"] + component_options

        get_valid_selectbox_state("scatter_x_select", x_options, "-")
        get_valid_selectbox_state("scatter_y_select", y_options, "-")
        get_valid_selectbox_state("scatter_color_select", color_options, "-")

        scatter_x = st.selectbox("X Axis", options=x_options, key="scatter_x_select")
        scatter_y = st.selectbox("Y Axis", options=y_options, key="scatter_y_select")
        scatter_color = st.selectbox("Color Encoding", options=color_options, key="scatter_color_select")

        st.session_state["scatter_x"] = scatter_x if scatter_x != "-" else None
        st.session_state["scatter_y"] = scatter_y if scatter_y != "-" else None
        st.session_state["scatter_color"] = scatter_color if scatter_color != "-" else None

        st.divider()

        point_size = st.number_input("Point Size", min_value=5.0, max_value=200.0, step=5.0, key="scatter_point_size")
        point_type = st.selectbox("Point Type", options=list(POINT_TYPE_OPTIONS.keys()), key="scatter_point_type")
        edge_width = st.number_input("Edge Width", min_value=0.0, max_value=5.0, step=0.1, key="scatter_edge_width")

        color_label = None
        color_min, color_min_error = (None, False)
        color_max, color_max_error = (None, False)
        color_tick_step, color_tick_step_error = (None, False)
        if scatter_color and scatter_color != "-":
            is_numeric_color = scatter_color in combined.columns and pd.api.types.is_numeric_dtype(combined[scatter_color])
            if not st.session_state.get("scatter_color_label"):
                st.session_state["scatter_color_label"] = scatter_color
            if is_numeric_color:
                st.divider()
                st.caption("Color Legend Scale")
                color_label = st.text_input("Color Legend", key="scatter_color_label")
                min_col, max_col = st.columns(2)
                color_min, color_min_error = _parse_optional_float(
                    min_col.text_input("Color Min", key="scatter_color_min", placeholder="Auto")
                )
                color_max, color_max_error = _parse_optional_float(
                    max_col.text_input("Color Max", key="scatter_color_max", placeholder="Auto")
                )
                color_tick_step, color_tick_step_error = _parse_optional_float(
                    st.text_input("Color Tick Step", key="scatter_color_tick_step", placeholder="Auto")
                )
            else:
                color_label = st.text_input("Color Legend", key="scatter_color_label")

    with main_col:
        x_col = st.session_state.get("scatter_x")
        y_col = st.session_state.get("scatter_y")

        if not x_col or not y_col:
            st.info("Please select both an X and a Y component.")
            return

        if x_col not in combined.columns or y_col not in combined.columns:
            st.warning("The selected columns were not found in the data.")
            return

        if color_min_error or color_max_error or color_tick_step_error:
            st.warning("Color Legend Scale requires valid numeric values or blank fields for Auto.")
            return
        if color_tick_step is not None and color_tick_step <= 0:
            st.warning("Color Tick Step must be greater than 0.")
            return
        if color_min is not None and color_max is not None and color_max <= color_min:
            st.warning("Color Max must be greater than Color Min.")
            return

        if len(combined) > MAX_PLOT_ROWS:
            combined = combined.sample(n=MAX_PLOT_ROWS, random_state=42)
            st.info(f"Large dataset detected. Sampled down to {MAX_PLOT_ROWS:,} rows.")

        color_col = st.session_state.get("scatter_color")
        scatter_df = combined[[x_col, y_col]].copy()
        if color_col and color_col in combined.columns:
            scatter_df[color_col] = combined[color_col]

        fig = plot_scatter(
            scatter_df,
            x_col=x_col,
            y_col=y_col,
            color_col=color_col if color_col and color_col in scatter_df.columns else None,
            figsize=_figure_size(options),
            axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
            axis_title_fontsize=options.get("axis_title_fontsize", PLOT_DEFAULTS.axis_title_fontsize),
            point_size=point_size,
            edge_width=edge_width,
            marker=POINT_TYPE_OPTIONS[point_type],
            x_label=options.get("x_axis_label", PLOT_DEFAULTS.x_label),
            y_label=options.get("y_axis_label", PLOT_DEFAULTS.y_label),
            x_unit=options.get("x_unit", PLOT_DEFAULTS.x_unit),
            y_unit=options.get("y_unit", PLOT_DEFAULTS.y_unit),
            color_label=color_label or None,
            xlim=(options.get("x_min"), options.get("x_max")) if options.get("set_x_range") else None,
            ylim=(options.get("y_min"), options.get("y_max")) if options.get("set_y_range") else None,
            x_tick_step=options.get("x_tick_step"),
            y_tick_step=options.get("y_tick_step"),
            color_min=color_min,
            color_max=color_max,
            color_tick_step=color_tick_step,
        )

        if fig is None:
            st.warning("No valid data points were found.")
            return

        st.pyplot(fig, width="stretch")

        if options.get("export_trigger") and options.get("export_format"):
            export_plots(
                [("Scatter Plot", fig)],
                options.get("export_filename", "export"),
                options.get("export_format"),
            )
        import matplotlib.pyplot as plt

        plt.close(fig)


def _figure_size(options: dict) -> Tuple[float, float]:
    """Calculate figure size from sidebar options (mm -> inches)."""
    width_mm = float(options.get("plot_width", PLOT_DEFAULTS.width))
    height_mm = float(options.get("plot_height", PLOT_DEFAULTS.height))
    return (width_mm / 25.4, height_mm / 25.4)


def _parse_optional_float(value: str | None) -> tuple[float | None, bool]:
    """Parse a blankable numeric input."""
    normalized = (value or "").strip()
    if not normalized:
        return (None, False)

    try:
        return (float(normalized.replace(",", ".")), False)
    except ValueError:
        return (None, True)
