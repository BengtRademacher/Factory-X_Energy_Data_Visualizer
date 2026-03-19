"""Bar chart tab for the Factory-X plotting app."""

from typing import Tuple

import streamlit as st

from app.config import BAR_DEFAULTS, PLOT_DEFAULTS
from app.export import export_plots
from app.plotting import plot_bar, plot_bar_evp
from app.ui.components import build_color_targets, get_valid_multiselect_state, render_component_color_section


def render(processed, options: dict) -> None:
    """Render the Bar Charts tab."""
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
            default=get_valid_multiselect_state("bar_selected_components", component_options),
            key="bar_selected_components",
        )

        colors = render_component_color_section("bar", build_color_targets(components))

        st.divider()

        aggregation_options = ["Average", "Sum"]
        current_mode = st.session_state.get("bar_mode", BAR_DEFAULTS.mode)
        mode_index = aggregation_options.index(current_mode) if current_mode in aggregation_options else 0
        mode = st.selectbox("Aggregation", aggregation_options, index=mode_index, key="bar_mode")

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
                mode=mode,
                label_rotation=label_rotation,
                colors=colors,
                hide_x_labels=hide_x_labels,
                figsize=_figure_size(options),
                line_width=options.get("line_width", PLOT_DEFAULTS.line_width),
                axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
                axis_title_fontsize=options.get("axis_title_fontsize", PLOT_DEFAULTS.axis_title_fontsize),
                ylim=None,
                y_unit=options.get("y_unit", PLOT_DEFAULTS.y_unit),
                bar_width=bar_width,
                y_tick_step=options.get("y_tick_step"),
                y_label=options.get("y_axis_label", PLOT_DEFAULTS.y_label),
                x_label=options.get("x_axis_label", ""),
            )
            if fig:
                st.pyplot(fig, width="stretch")
                plots_to_export.append(("Bar Chart", fig))
                import matplotlib.pyplot as plt

                plt.close(fig)
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
                mode=mode,
                label_rotation=label_rotation,
                colors=colors,
                hide_x_labels=hide_x_labels,
                figsize=_figure_size(options),
                line_width=options.get("line_width", PLOT_DEFAULTS.line_width),
                axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
                axis_title_fontsize=options.get("axis_title_fontsize", PLOT_DEFAULTS.axis_title_fontsize),
                ylim=None,
                y_unit=options.get("y_unit", PLOT_DEFAULTS.y_unit),
                bar_width=bar_width,
                y_tick_step=options.get("y_tick_step"),
                y_label=options.get("y_axis_label", PLOT_DEFAULTS.y_label),
                x_label=options.get("x_axis_label", ""),
            )
            if fig_compare:
                st.pyplot(fig_compare, width="stretch")
                plots_to_export.append(("Comparison Chart", fig_compare))
                import matplotlib.pyplot as plt

                plt.close(fig_compare)

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
