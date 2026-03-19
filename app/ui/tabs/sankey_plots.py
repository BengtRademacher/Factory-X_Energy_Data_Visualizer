"""Sankey tab for the Factory-X plotting app."""

from typing import Tuple

import streamlit as st

from app.config import DEFAULT_COLORS, PLOT_DEFAULTS, SANKEY_DEFAULTS
from app.export import export_plots
from app.plotting import plot_sankey_energy_flow
from app.ui.components import ColorTarget, build_color_targets, get_valid_multiselect_state, render_component_color_section


def render(processed, options: dict) -> None:
    """Render the Sankey tab."""
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

        title = st.text_input("Title", key="sankey_title")

        mode_options = ["Average", "Sum"]
        current_mode = st.session_state.get("sankey_mode", SANKEY_DEFAULTS.mode)
        mode_index = mode_options.index(current_mode) if current_mode in mode_options else 0
        mode = st.selectbox("Mode", mode_options, index=mode_index, key="sankey_mode")

        unit = st.text_input("Unit", key="sankey_unit")

        st.divider()

        electric = st.multiselect(
            "Electric Components",
            options=component_options,
            default=get_valid_multiselect_state("sankey_selected_electric", component_options),
            key="sankey_selected_electric",
        )

        pneumatic = st.multiselect(
            "Pneumatic Components",
            options=component_options,
            default=get_valid_multiselect_state("sankey_selected_pneumatic", component_options),
            key="sankey_selected_pneumatic",
        )

        all_selected = electric + pneumatic
        productive = st.multiselect(
            "Productive Components",
            options=all_selected,
            default=get_valid_multiselect_state("sankey_productive_vars", all_selected),
            key="sankey_productive_vars",
        )

        st.divider()

        sankey_targets = [
            ColorTarget(id="Electric", label="Electric (Group)", default_color=DEFAULT_COLORS[0]),
            ColorTarget(id="Pneumatic", label="Pneumatic (Group)", default_color=DEFAULT_COLORS[3]),
        ]
        sankey_targets.extend(build_color_targets(all_selected))
        colors = render_component_color_section("sankey", sankey_targets)

    with main_col:
        if not electric and not pneumatic:
            st.info("Please select at least one component.")
            return

        fig = plot_sankey_energy_flow(
            df=processed.combined_frame,
            selected_electric=electric,
            selected_pneumatic=pneumatic,
            productive_vars=productive,
            mode=mode,
            figsize=_figure_size(options),
            axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
            title=title,
            colors=colors,
            unit=unit,
        )

        if fig is None:
            st.info("No data is available for the Sankey diagram.")
            return

        st.plotly_chart(fig, width="stretch")

        if options.get("export_trigger") and options.get("export_format"):
            export_plots(
                [(title, fig)],
                options.get("export_filename", "export"),
                options.get("export_format"),
            )


def _figure_size(options: dict) -> Tuple[float, float]:
    """Calculate figure size from sidebar options (mm -> inches)."""
    width_mm = float(options.get("plot_width", PLOT_DEFAULTS.width))
    height_mm = float(options.get("plot_height", PLOT_DEFAULTS.height))
    return (width_mm / 25.4, height_mm / 25.4)
