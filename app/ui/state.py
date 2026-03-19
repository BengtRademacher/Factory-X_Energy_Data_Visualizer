"""Session-state management for the Factory-X plotting app."""

import streamlit as st

from app.config import (
    BAR_DEFAULTS,
    BOX_DEFAULTS,
    DONUT_DEFAULTS,
    EXPORT_DEFAULTS,
    HISTOGRAM_DEFAULTS,
    PLOT_DEFAULTS,
    SANKEY_DEFAULTS,
    SCATTER_DEFAULTS,
    SECONDARY_AXIS_DEFAULTS,
)


def initialize_state() -> None:
    """Initialize the full UI session state."""
    if "plot_refresh_counter" not in st.session_state:
        st.session_state["plot_refresh_counter"] = 0

    _init_global_state()
    _init_line_plot_state()
    _init_bar_plot_state()
    _init_box_plot_state()
    _init_donut_state()
    _init_scatter_state()
    _init_histogram_state()
    _init_sankey_state()
    _init_export_state()
    _init_ui_state()


def _init_global_state() -> None:
    """Initialize global settings shared by all plots."""
    defaults = {
        "plot_width": int(PLOT_DEFAULTS.width),
        "plot_height": int(PLOT_DEFAULTS.height),
        "axis_annotation_fontsize": int(PLOT_DEFAULTS.axis_fontsize),
        "axis_title_fontsize": int(PLOT_DEFAULTS.axis_title_fontsize),
        "line_width": float(PLOT_DEFAULTS.line_width),
        "x_source_column": None,
        "x_source_auto_selected": False,
        "x_axis_label": PLOT_DEFAULTS.x_label,
        "y_axis_label": PLOT_DEFAULTS.y_label,
        "x_unit": PLOT_DEFAULTS.x_unit,
        "y_unit": PLOT_DEFAULTS.y_unit,
        "x_tick_step": float(PLOT_DEFAULTS.x_tick_step),
        "y_tick_step": float(PLOT_DEFAULTS.y_tick_step),
        "set_x_range": False,
        "x_min": float(PLOT_DEFAULTS.x_min),
        "x_max": float(PLOT_DEFAULTS.x_max),
        "set_y_range": False,
        "y_min": float(PLOT_DEFAULTS.y_min),
        "y_max": float(PLOT_DEFAULTS.y_max),
        "ranges_valid": True,
    }
    _set_defaults(defaults)

    for key in ("plot_width", "plot_height"):
        value = st.session_state.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            st.session_state[key] = int(round(value))


def _init_line_plot_state() -> None:
    """Initialize state for line plots."""
    defaults = {
        "line_selected_components": [],
        "line_stacked_enabled": False,
        "line_colors": {},
        "secondary_axis_enabled": SECONDARY_AXIS_DEFAULTS.enabled,
        "secondary_axis_components": [],
        "secondary_axis_colors": {},
        "secondary_axis_label": SECONDARY_AXIS_DEFAULTS.label,
        "secondary_axis_unit": SECONDARY_AXIS_DEFAULTS.unit,
        "secondary_axis_tick_step": SECONDARY_AXIS_DEFAULTS.tick_step,
        "secondary_axis_min": SECONDARY_AXIS_DEFAULTS.min_value,
        "secondary_axis_max": SECONDARY_AXIS_DEFAULTS.max_value,
        "secondary_ranges_valid": True,
    }
    _set_defaults(defaults)


def _init_bar_plot_state() -> None:
    """Initialize state for bar charts."""
    defaults = {
        "bar_selected_components": [],
        "bar_colors": {},
        "bar_width": BAR_DEFAULTS.bar_width,
        "bar_label_rotation": BAR_DEFAULTS.label_rotation,
        "bar_hide_x_labels": BAR_DEFAULTS.hide_x_labels,
        "bar_show_compare": False,
        "bar_compare_components": [],
    }
    _set_defaults(defaults)


def _init_box_plot_state() -> None:
    """Initialize state for box plots."""
    defaults = {
        "box_selected_components": [],
        "box_colors": {},
        "box_width": BOX_DEFAULTS.box_width,
        "box_label_rotation": BOX_DEFAULTS.label_rotation,
    }
    _set_defaults(defaults)


def _init_donut_state() -> None:
    """Initialize state for donut charts."""
    defaults = {
        "donut_components": [],
        "donut_colors": {},
        "donut_hole": DONUT_DEFAULTS.hole,
        "donut_chart_size": DONUT_DEFAULTS.chart_size_px,
        "donut_label_mode": DONUT_DEFAULTS.label_mode,
        "donut_show_others": DONUT_DEFAULTS.show_others,
        "donut_show_legend": DONUT_DEFAULTS.show_legend,
        "donut_total_target_kw": DONUT_DEFAULTS.total_target_kw,
        "donut_title": DONUT_DEFAULTS.title,
    }
    _set_defaults(defaults)


def _init_scatter_state() -> None:
    """Initialize state for scatter plots."""
    defaults = {
        "scatter_x_select": "-",
        "scatter_y_select": "-",
        "scatter_color_select": "-",
        "scatter_x": None,
        "scatter_y": None,
        "scatter_color": None,
        "scatter_point_size": SCATTER_DEFAULTS.point_size,
        "scatter_edge_width": SCATTER_DEFAULTS.edge_width,
        "scatter_point_type": SCATTER_DEFAULTS.point_type,
        "scatter_color_label": SCATTER_DEFAULTS.color_label,
        "scatter_color_min": SCATTER_DEFAULTS.color_min,
        "scatter_color_max": SCATTER_DEFAULTS.color_max,
        "scatter_color_tick_step": SCATTER_DEFAULTS.color_tick_step,
    }
    _set_defaults(defaults)


def _init_histogram_state() -> None:
    """Initialize state for histograms."""
    defaults = {
        "histogram_components": [],
        "histogram_colors": {},
        "histogram_bins": HISTOGRAM_DEFAULTS.bins,
        "histogram_line_width": HISTOGRAM_DEFAULTS.line_width,
    }
    _set_defaults(defaults)


def _init_sankey_state() -> None:
    """Initialize state for Sankey charts."""
    defaults = {
        "sankey_selected_electric": [],
        "sankey_selected_pneumatic": [],
        "sankey_productive_vars": [],
        "sankey_colors": {},
        "sankey_unit": SANKEY_DEFAULTS.unit,
        "sankey_title": SANKEY_DEFAULTS.title,
    }
    _set_defaults(defaults)


def _init_export_state() -> None:
    """Initialize state for exports."""
    defaults = {
        "export_filename": EXPORT_DEFAULTS.filename,
        "export_formats": EXPORT_DEFAULTS.formats.copy(),
        "export_separate_files": EXPORT_DEFAULTS.separate_files,
        "donut_export_filename": "donut_export",
        "donut_export_formats": ["PDF", "PNG"],
        "donut_export_separate": False,
    }
    _set_defaults(defaults)

    if st.session_state.get("export_filename") == "name":
        st.session_state["export_filename"] = EXPORT_DEFAULTS.filename


def _init_ui_state() -> None:
    """Initialize UI-related state."""
    _set_defaults({"active_tab_name": "Line Plots"})


def reset_ui_state() -> None:
    """Reset UI widgets and clear data-driven selections."""
    selection_keys = {
        "_cached_processed_x_axes",
        "line_selected_components",
        "secondary_axis_components",
        "bar_selected_components",
        "bar_compare_components",
        "box_selected_components",
        "donut_components",
        "histogram_components",
        "sankey_selected_electric",
        "sankey_selected_pneumatic",
        "sankey_productive_vars",
        "scatter_x_select",
        "scatter_y_select",
        "scatter_color_select",
        "scatter_x",
        "scatter_y",
        "scatter_color",
        "scatter_point_type",
        "scatter_color_min",
        "scatter_color_max",
        "scatter_color_tick_step",
        "x_source_column",
        "x_source_column_select",
        "x_source_auto_selected",
        "data_summary_columns",
    }

    ui_patterns = [
        "_width",
        "_rotation",
        "_bins",
        "_size",
        "_hole",
        "_step",
        "_label",
        "_unit",
        "_title",
        "_filename",
        "_min",
        "_max",
        "_tick_step",
        "_range",
        "plot_width",
        "plot_height",
        "axis_annotation_fontsize",
        "axis_title_fontsize",
        "line_width",
        "x_axis_label",
        "y_axis_label",
    ]

    exclude_patterns = [
        "_selected",
        "_colors",
        "_color_",
        "processed_data",
        "_components",
        "_vars",
        "_mode",
        "_select",
        "_options",
        "_aggregation",
        "_axis",
        "_type",
        "_source",
        "_label_mode",
    ]

    for key in list(st.session_state.keys()):
        if key in selection_keys or key.startswith("preview_plot_columns_"):
            st.session_state.pop(key, None)
            continue

        is_ui_element = any(pattern in key for pattern in ui_patterns)
        is_excluded = any(pattern in key for pattern in exclude_patterns)

        if is_ui_element and not is_excluded:
            st.session_state.pop(key, None)

    st.session_state["plot_refresh_counter"] = st.session_state.get("plot_refresh_counter", 0) + 1


def _set_defaults(defaults: dict) -> None:
    """Set default session-state values only when they do not exist yet."""
    for key, value in defaults.items():
        if key not in st.session_state:
            if isinstance(value, float):
                st.session_state[key] = float(value)
            elif isinstance(value, int) and not isinstance(value, bool):
                st.session_state[key] = int(value)
            else:
                st.session_state[key] = value


def get_state(key: str, default=None):
    """Read a value from session state."""
    return st.session_state.get(key, default)


def set_state(key: str, value) -> None:
    """Write a value to session state."""
    st.session_state[key] = value
