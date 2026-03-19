"""Pie and donut chart tab for the Factory-X plotting app."""

import streamlit as st

from app.config import PLOT_DEFAULTS
from app.plotting import plot_donut
from app.ui.components import ColorTarget, build_color_targets, get_valid_multiselect_state, render_component_color_section
from app.ui.tab_utils import ensure_has_data, ensure_valid_ranges, finalize_matplotlib_figures, render_matplotlib_figure


def render(processed, options: dict) -> None:
    """Render the Pie and Donut Charts tab."""
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
            default=get_valid_multiselect_state("donut_components", component_options),
            key="donut_components",
        )

        show_others = st.checkbox("'Others' Segment", key="donut_show_others")

        color_targets = build_color_targets(components)
        if show_others:
            color_targets.append(ColorTarget(id="Others", label="Others Color", default_color="#888888"))
        colors = render_component_color_section("donut", color_targets)

        st.divider()

        hole = st.slider("Donut Hole", 0.0, 0.9, step=0.05, key="donut_hole")
        chart_size = st.slider("Chart Size (px)", 300, 1000, step=10, key="donut_chart_size")
        label_mode = st.selectbox("Labels", ["Percent", "kW"], key="donut_label_mode")
        show_legend = st.checkbox("Show Legend", key="donut_show_legend")
        total_target_kw = st.number_input("Scaled Total Demand (kW)", min_value=0.0, step=0.5, key="donut_total_target_kw")
        title = st.text_input("Title", key="donut_title")

    with main_col:
        if not components:
            st.info("Please select at least one component.")
            return

        fig = plot_donut(
            combined_df=processed.combined_frame,
            components=components,
            colors=colors,
            hole=hole,
            label_mode=label_mode,
            total_target_kw=total_target_kw,
            show_others=show_others,
            chart_size_px=chart_size,
            title=title,
            axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
            show_legend=show_legend,
            source_unit=options.get("y_unit", PLOT_DEFAULTS.y_unit),
            component_means=processed.overall_numeric_means,
        )

        if fig is None:
            st.warning("The selected components do not contain usable values.")
            return

        render_matplotlib_figure(fig)
        finalize_matplotlib_figures([(title, fig)], options)
