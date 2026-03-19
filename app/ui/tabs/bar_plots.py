"""Bar chart tab for the Factory-X plotting app."""

import streamlit as st

from app.config import PLOT_DEFAULTS
from app.plotting import plot_bar, plot_bar_evp
from app.ui.components import build_color_targets, get_valid_multiselect_state, render_component_color_section
from app.ui.tab_utils import (
    ensure_has_data,
    ensure_valid_ranges,
    figure_size_from_options,
    finalize_matplotlib_figures,
    render_matplotlib_figure,
)


def render(processed, options: dict) -> None:
    """Render the Bar Charts tab."""
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
            default=get_valid_multiselect_state("bar_selected_components", component_options),
            key="bar_selected_components",
        )

        colors = render_component_color_section("bar", build_color_targets(components))

        st.divider()

        bar_width = st.slider("Bar Width", 0.05, 0.60, step=0.01, key="bar_width")
        label_rotation = st.slider("Label Rotation", 0, 90, step=5, key="bar_label_rotation")
        hide_x_labels = st.checkbox("Hide X Labels", key="bar_hide_x_labels")

        st.divider()

        show_compare = st.checkbox("Comparison Bars", key="bar_show_compare")
        compare_components = []
        if show_compare:
            compare_components = st.multiselect(
                "Comparison Components",
                options=component_options,
                default=get_valid_multiselect_state("bar_compare_components", component_options),
                key="bar_compare_components",
            )

    with main_col:
        plots_to_export = []

        if components:
            fig = plot_bar(
                df_by_file=processed.frames_by_file,
                components=components,
                title="Bar Chart",
                label_rotation=label_rotation,
                colors=colors,
                hide_x_labels=hide_x_labels,
                figsize=figure_size_from_options(options),
                line_width=options.get("line_width", PLOT_DEFAULTS.line_width),
                axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
                axis_title_fontsize=options.get("axis_title_fontsize", PLOT_DEFAULTS.axis_title_fontsize),
                ylim=None,
                y_unit=options.get("y_unit", PLOT_DEFAULTS.y_unit),
                bar_width=bar_width,
                y_tick_step=options.get("y_tick_step"),
                y_label=options.get("y_axis_label", PLOT_DEFAULTS.y_label),
                x_label=options.get("x_axis_label", ""),
                per_file_means=processed.per_file_numeric_means,
            )
            if fig:
                render_matplotlib_figure(fig)
                plots_to_export.append(("Bar Chart", fig))
        else:
            st.info("Please select at least one component.")

        if show_compare and components and compare_components:
            st.divider()
            st.subheader("Comparison")

            fig_compare = plot_bar_evp(
                df_by_file=processed.frames_by_file,
                elec_components=components,
                pneu_components=compare_components,
                title="Comparison: Group 1 vs. Group 2",
                label_rotation=label_rotation,
                colors=colors,
                hide_x_labels=hide_x_labels,
                figsize=figure_size_from_options(options),
                line_width=options.get("line_width", PLOT_DEFAULTS.line_width),
                axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
                axis_title_fontsize=options.get("axis_title_fontsize", PLOT_DEFAULTS.axis_title_fontsize),
                ylim=None,
                y_unit=options.get("y_unit", PLOT_DEFAULTS.y_unit),
                bar_width=bar_width,
                y_tick_step=options.get("y_tick_step"),
                y_label=options.get("y_axis_label", PLOT_DEFAULTS.y_label),
                x_label=options.get("x_axis_label", ""),
                per_file_means=processed.per_file_numeric_means,
            )
            if fig_compare:
                render_matplotlib_figure(fig_compare)
                plots_to_export.append(("Comparison Chart", fig_compare))

        finalize_matplotlib_figures(plots_to_export, options)
