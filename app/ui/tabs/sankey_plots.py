"""Sankey tab for the Factory-X plotting app."""

import inspect

import streamlit as st

from app.config import DEFAULT_COLORS, PLOT_DEFAULTS
from app.export import export_plots
from app.plotting import plot_sankey_energy_flow
from app.ui.components import ColorTarget, build_color_targets, get_valid_multiselect_state, render_component_color_section
from app.ui.tab_utils import ensure_has_data, ensure_valid_ranges, figure_size_from_options


def _plotly_chart_kwargs() -> dict:
    """Build a Streamlit-compatible Plotly chart call without deprecated kwargs."""
    parameters = inspect.signature(st.plotly_chart).parameters
    kwargs: dict[str, object] = {}
    if "config" in parameters:
        kwargs["config"] = {}
    if "width" in parameters:
        kwargs["width"] = "stretch"
    else:
        kwargs["use_container_width"] = True
    return kwargs


def render(processed, options: dict) -> None:
    """Render the Sankey tab."""
    if not ensure_has_data(processed, "Please upload files to create charts."):
        return

    if not ensure_valid_ranges(options):
        return

    main_col, custom_col = st.columns([4, 1])
    component_options = options.get("numeric_plot_columns", [])

    with custom_col:
        st.markdown("### :material/tune: Options")

        title = st.text_input("Title", key="sankey_title")

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
            figsize=figure_size_from_options(options),
            axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
            title=title,
            colors=colors,
            unit=unit,
            component_means=processed.overall_numeric_means,
        )

        if fig is None:
            st.info("No data is available for the Sankey diagram.")
            return

        st.plotly_chart(fig, **_plotly_chart_kwargs())

        if options.get("export_trigger") and options.get("export_format"):
            export_plots(
                [(title, fig)],
                options.get("export_filename", "export"),
                options.get("export_format"),
            )
