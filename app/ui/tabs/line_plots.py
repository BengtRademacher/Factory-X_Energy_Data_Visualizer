"""Line plot tab for the Factory-X plotting app."""

from typing import Tuple

import streamlit as st

from app.config import MAX_PLOT_ROWS, PLOT_DEFAULTS
from app.export import export_plots
from app.plotting import plot_line
from app.ui.components import build_color_targets, get_valid_multiselect_state, render_component_color_section
from app.x_axis import resolve_processed_x_axis


def render(processed, options: dict) -> None:
    """Render the Line Plots tab."""
    if not processed.has_data:
        st.info("Please upload files to create charts.")
        return

    if not options.get("ranges_valid", True):
        st.warning("Invalid axis ranges. Please ensure Y Min < Y Max and X Min < X Max.")
        return

    x_source_column = options.get("x_source_column")
    component_options = options.get("numeric_plot_columns", [])
    if x_source_column in component_options:
        component_options = [col for col in component_options if col != x_source_column]

    main_col, custom_col = st.columns([4, 1])

    with custom_col:
        st.markdown("### :material/tune: Options")

        components = st.multiselect(
            "Components",
            options=component_options,
            default=get_valid_multiselect_state("line_selected_components", component_options),
            key="line_selected_components",
        )

        colors = render_component_color_section("line", build_color_targets(components))
        st.checkbox("Stacked Plots", key="line_stacked_enabled")

        st.divider()
        secondary_args = _render_secondary_axis(component_options)

    with main_col:
        if not x_source_column:
            st.info("Please choose an X source in the sidebar.")
            return

        x_resolution = resolve_processed_x_axis(processed, x_source_column)
        if x_resolution.error:
            st.warning(x_resolution.error)
            return

        if not components:
            st.info("Please select at least one component.")
            return

        combined_df = processed.combined_frame.reset_index(drop=True)
        x_values = x_resolution.values.reset_index(drop=True)

        if len(combined_df) > MAX_PLOT_ROWS:
            sampled_index = combined_df.sample(n=MAX_PLOT_ROWS, random_state=42).sort_index().index
            combined_df = combined_df.loc[sampled_index].reset_index(drop=True)
            x_values = x_values.loc[sampled_index].reset_index(drop=True)
            st.info(f"Large dataset detected. Sampled down to {MAX_PLOT_ROWS:,} rows.")

        xlim = (options.get("x_min"), options.get("x_max")) if options.get("set_x_range") else None
        ylim = (options.get("y_min"), options.get("y_max")) if options.get("set_y_range") else None

        fig = plot_line(
            combined_df=combined_df,
            x_values=x_values,
            file_boundaries=x_resolution.file_boundaries,
            components=components,
            title="Line Plot",
            colors=colors,
            figsize=_figure_size(options),
            line_width=options.get("line_width", PLOT_DEFAULTS.line_width),
            axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
            axis_title_fontsize=options.get("axis_title_fontsize", PLOT_DEFAULTS.axis_title_fontsize),
            xlim=xlim,
            ylim=ylim,
            x_unit=options.get("x_unit", PLOT_DEFAULTS.x_unit),
            y_unit=options.get("y_unit", PLOT_DEFAULTS.y_unit),
            x_tick_step=options.get("x_tick_step"),
            y_tick_step=options.get("y_tick_step"),
            x_label=options.get("x_axis_label", PLOT_DEFAULTS.x_label),
            y_label=options.get("y_axis_label", PLOT_DEFAULTS.y_label),
            stacked=st.session_state.get("line_stacked_enabled", False),
            **secondary_args,
        )

        if fig:
            st.pyplot(fig, width="stretch")

            if options.get("export_trigger") and options.get("export_format"):
                export_plots(
                    [("Line Plot", fig)],
                    options.get("export_filename", "export"),
                    options.get("export_format"),
                )
            import matplotlib.pyplot as plt

            plt.close(fig)


def _render_secondary_axis(component_options: list[str]) -> dict:
    """Render settings for the secondary axis."""
    st.checkbox("Secondary Y Axis", key="secondary_axis_enabled")

    if not st.session_state.get("secondary_axis_enabled"):
        render_component_color_section("secondary_axis", [], title="Secondary Colors")
        return {}

    secondary_ylim = None
    with st.container(border=True):
        secondary_components = st.multiselect(
            "Secondary Components",
            options=component_options,
            default=get_valid_multiselect_state("secondary_axis_components", component_options),
            key="secondary_axis_components",
        )

        secondary_colors = render_component_color_section(
            "secondary_axis",
            build_color_targets(secondary_components, start_index=4),
            title="Secondary Colors",
        )

        st.text_input("Secondary Label", key="secondary_axis_label")
        st.text_input("Secondary Unit", key="secondary_axis_unit")
        secondary_tick_step, secondary_tick_step_error = _parse_required_float(
            st.text_input(
                "Secondary Tick Step",
                value=_format_float_input(st.session_state.get("secondary_axis_tick_step")),
                key="secondary_axis_tick_step_ui",
            )
        )
        if secondary_tick_step_error:
            st.warning("Secondary Tick Step must be a valid number.")
            secondary_tick_step = None
        elif secondary_tick_step <= 0:
            st.warning("Secondary Tick Step must be greater than 0.")
            secondary_tick_step = None
        else:
            st.session_state["secondary_axis_tick_step"] = secondary_tick_step

        st.caption("Range")
        col1, col2 = st.columns(2)
        sec_min, sec_min_error = _parse_required_float(
            col1.text_input(
                "Secondary Min",
                value=_format_float_input(st.session_state.get("secondary_axis_min")),
                key="secondary_axis_min_ui",
            )
        )
        sec_max, sec_max_error = _parse_required_float(
            col2.text_input(
                "Secondary Max",
                value=_format_float_input(st.session_state.get("secondary_axis_max")),
                key="secondary_axis_max_ui",
            )
        )
        if sec_min_error or sec_max_error:
            st.warning("Secondary range requires valid numbers.")
        elif sec_max > sec_min:
            st.session_state["secondary_axis_min"] = sec_min
            st.session_state["secondary_axis_max"] = sec_max
            secondary_ylim = (sec_min, sec_max)
        else:
            st.warning("Secondary Max must be greater than Secondary Min.")

    return {
        "secondary_components": secondary_components,
        "secondary_colors": secondary_colors,
        "secondary_y_unit": st.session_state.get("secondary_axis_unit", ""),
        "secondary_y_label": st.session_state.get("secondary_axis_label", "Secondary value"),
        "secondary_y_tick_step": secondary_tick_step,
        "secondary_ylim": secondary_ylim,
    }


def _figure_size(options: dict) -> Tuple[float, float]:
    """Calculate figure size from sidebar options (mm -> inches)."""
    width_mm = float(options.get("plot_width", PLOT_DEFAULTS.width))
    height_mm = float(options.get("plot_height", PLOT_DEFAULTS.height))
    return (width_mm / 25.4, height_mm / 25.4)


def _parse_required_float(value: str | None) -> tuple[float | None, bool]:
    """Parse a required numeric input."""
    normalized = (value or "").strip()
    if not normalized:
        return (None, True)

    try:
        return (float(normalized.replace(",", ".")), False)
    except ValueError:
        return (None, True)


def _format_float_input(value: object) -> str:
    """Format numeric state values for plain text inputs."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"{value:g}".replace(".", ",")
    if value is None:
        return ""
    return str(value)
