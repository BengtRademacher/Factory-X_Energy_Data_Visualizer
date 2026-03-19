"""Box plot tab for the Factory-X plotting app."""

from typing import Tuple

import streamlit as st

from app.config import PLOT_DEFAULTS
from app.export import export_plots
from app.plotting import plot_boxplot
from app.ui.components import build_color_targets, get_valid_multiselect_state, render_component_color_section


def render(processed, options: dict) -> None:
    """Render the Box Plots tab."""
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
            default=get_valid_multiselect_state("box_selected_components", component_options),
            key="box_selected_components",
        )

        colors = render_component_color_section("box", build_color_targets(components))

        st.divider()

        box_width = st.slider("Box Width", 0.1, 1.2, step=0.05, key="box_width")
        label_rotation = st.slider("Label Rotation", 0, 90, step=5, key="box_label_rotation")

    with main_col:
        if not components:
            st.info("Please select at least one component.")
            return

        fig = plot_boxplot(
            df_by_file=processed.frames_by_file,
            components=components,
            title="Box Plot",
            figsize=_figure_size(options),
            axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
            axis_title_fontsize=options.get("axis_title_fontsize", PLOT_DEFAULTS.axis_title_fontsize),
            colors=colors,
            line_width=options.get("line_width", PLOT_DEFAULTS.line_width),
            label_rotation=label_rotation,
            ylim=None,
            y_unit=options.get("y_unit", PLOT_DEFAULTS.y_unit),
            legend_inside=False,
            y_tick_step=options.get("y_tick_step"),
            y_label=options.get("y_axis_label", PLOT_DEFAULTS.y_label),
            box_width=box_width,
        )

        if fig:
            st.pyplot(fig, width="stretch")

            if options.get("export_trigger") and options.get("export_format"):
                export_plots(
                    [("Box Plot", fig)],
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
