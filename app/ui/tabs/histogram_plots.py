"""Histogram tab for the Factory-X plotting app."""

from typing import List

import numpy as np
import pandas as pd
import streamlit as st

from app.config import DEFAULT_COLORS, PLOT_DEFAULTS
from app.plotting import plot_histogram
from app.ui.components import build_color_targets, get_valid_multiselect_state, render_component_color_section
from app.ui.tab_utils import (
    ensure_has_data,
    ensure_valid_ranges,
    figure_size_from_options,
    finalize_matplotlib_figures,
    render_matplotlib_figure,
)


def render(processed, options: dict) -> None:
    """Render the Histogram tab."""
    if not ensure_has_data(processed, "Please upload files to create charts."):
        return

    if not ensure_valid_ranges(options):
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

        plots_to_export: List[tuple[str, object]] = []
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
                figsize=figure_size_from_options(options),
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
                render_matplotlib_figure(fig)
                plots_to_export.append((f"Histogram - {comp}", fig))

        finalize_matplotlib_figures(plots_to_export, options)
