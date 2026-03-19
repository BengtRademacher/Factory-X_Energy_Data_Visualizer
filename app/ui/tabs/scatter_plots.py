"""Scatter plot tab for the Factory-X plotting app."""

from typing import Tuple

import streamlit as st

from app.config import MAX_PLOT_ROWS, PLOT_DEFAULTS
from app.export import export_plots
from app.plotting import plot_scatter
from app.ui.components import get_valid_selectbox_state


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
        edge_width = st.number_input("Edge Width", min_value=0.0, max_value=5.0, step=0.1, key="scatter_edge_width")

        st.divider()

        x_unit = st.text_input("X Unit", key="scatter_x_unit")
        y_unit = st.text_input("Y Unit", key="scatter_y_unit")

        color_label = None
        if scatter_color and scatter_color != "-":
            if not st.session_state.get("scatter_color_label"):
                st.session_state["scatter_color_label"] = scatter_color
            color_label = st.text_input("Color Legend", key="scatter_color_label")

    with main_col:
        x_col = st.session_state.get("scatter_x")
        y_col = st.session_state.get("scatter_y")

        if not x_col or not y_col:
            st.info("Please select both an X and a Y component.")
            return

        combined = processed.combined_frame
        if x_col not in combined.columns or y_col not in combined.columns:
            st.warning("The selected columns were not found in the data.")
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
            x_unit=x_unit or None,
            y_unit=y_unit or None,
            color_label=color_label or None,
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
