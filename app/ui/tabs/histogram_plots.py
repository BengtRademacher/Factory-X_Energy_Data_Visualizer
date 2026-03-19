"""Histogram tab for the Factory-X plotting app."""

from typing import List, Tuple

import numpy as np
import pandas as pd
import streamlit as st

from app.config import DEFAULT_COLORS, PLOT_DEFAULTS
from app.export import export_plots
from app.plotting import plot_histogram
from app.ui.components import build_color_targets, get_valid_multiselect_state, render_component_color_section


def render(processed, options: dict) -> None:
    """Render the Histogram tab."""
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

        components = st.multiselect(
            "Components",
            options=component_options,
            default=get_valid_multiselect_state("histogram_components", component_options),
            key="histogram_components",
        )

        colors = render_component_color_section("histogram", build_color_targets(components))

        st.divider()

        bins = st.slider("Number of Bins", min_value=10, max_value=200, step=5, key="histogram_bins")
        line_width = st.slider("Line Width", min_value=0.5, max_value=5.0, step=0.5, key="histogram_line_width")

    with main_col:
        if not components:
            st.info("Please select at least one component.")
            return

        plots_to_export: List[Tuple[str, object]] = []
        combined_df = processed.combined_frame
        xlim = (options.get("x_min"), options.get("x_max")) if options.get("set_x_range") else None
        ylim = (options.get("y_min"), options.get("y_max")) if options.get("set_y_range") else None
        bin_edges = None
        if xlim:
            bin_edges = np.linspace(xlim[0], xlim[1], int(bins) + 1)

        for index, comp in enumerate(components):
            if comp not in combined_df.columns:
                st.warning(f"Column '{comp}' was not found.")
                continue

            series = pd.to_numeric(combined_df[comp], errors="coerce")
            if series.isna().all():
                st.warning(f"Column '{comp}' does not contain numeric data.")
                continue

            color = colors.get(comp, DEFAULT_COLORS[index % len(DEFAULT_COLORS)])

            fig = plot_histogram(
                series=series,
                title=f"Histogram - {comp}",
                figsize=_figure_size(options),
                axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
                axis_title_fontsize=options.get("axis_title_fontsize", PLOT_DEFAULTS.axis_title_fontsize),
                bins=bins,
                line_width=line_width,
                color=color,
                x_label=options.get("x_axis_label", PLOT_DEFAULTS.x_label),
                y_label=options.get("y_axis_label", PLOT_DEFAULTS.y_label),
                xlim=xlim,
                ylim=ylim,
                x_unit=options.get("x_unit", PLOT_DEFAULTS.x_unit),
                y_unit=options.get("y_unit", PLOT_DEFAULTS.y_unit),
                x_tick_step=options.get("x_tick_step"),
                y_tick_step=options.get("y_tick_step"),
                bin_edges=bin_edges,
            )

            if fig is not None:
                st.pyplot(fig, width="stretch")
                plots_to_export.append((f"Histogram - {comp}", fig))
                import matplotlib.pyplot as plt

                plt.close(fig)

        if options.get("export_trigger") and options.get("export_format") and plots_to_export:
            export_plots(
                plots_to_export,
                options.get("export_filename", "export"),
                options.get("export_format"),
            )


def _figure_size(options: dict) -> Tuple[float, float]:
    """Calculate figure size from sidebar options (mm -> inches)."""
    width_mm = float(options.get("plot_width", PLOT_DEFAULTS.width))
    height_mm = float(options.get("plot_height", PLOT_DEFAULTS.height))
    return (width_mm / 25.4, height_mm / 25.4)
