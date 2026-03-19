"""Global sidebar for shared display and export settings."""

import pandas as pd
import streamlit as st

from app.config import EXPORT_DEFAULTS, PLOT_DEFAULTS
from app.ui.state import reset_ui_state
from app.x_axis import resolve_processed_x_axis


def render_sidebar(processed) -> dict:
    """Render the global sidebar and return the shared options."""
    st.sidebar.header("Settings")

    combined_df: pd.DataFrame | None = processed.combined_frame if processed and processed.has_data else None
    all_available_columns: list[str] = []
    numeric_plot_columns: list[str] = []
    x_source_columns: list[str] = []
    y_max_default = 100.0
    x_max_default = 100.0

    if combined_df is not None and not combined_df.empty:
        x_source_columns = combined_df.columns.tolist()
        all_available_columns = [col for col in combined_df.columns if col != "elapsedTime"]
        numeric_plot_columns = [
            col for col in combined_df.columns
            if col != "elapsedTime" and pd.api.types.is_numeric_dtype(combined_df[col])
        ]
        if numeric_plot_columns:
            y_max_default = float(combined_df[numeric_plot_columns].max().max())

    x_source_column = _sync_x_source_state(x_source_columns)
    x_resolution = resolve_processed_x_axis(processed, x_source_column)
    if x_resolution.error is None and x_resolution.max_value is not None:
        x_max_default = float(x_resolution.max_value)

    with st.sidebar:
        ranges_valid = _render_display_section(
            x_source_columns,
            x_max_default,
            y_max_default,
            x_resolution.error,
        )
        st.session_state["ranges_valid"] = ranges_valid

        export_trigger, export_format = _render_export_section()

        st.divider()
        st.button(
            "Restore Defaults",
            key="reset_button",
            use_container_width=True,
            type="secondary",
            on_click=reset_ui_state,
        )

    return _build_options_dict(
        all_available_columns,
        numeric_plot_columns,
        x_source_columns,
        export_trigger,
        export_format,
        x_max_default,
        y_max_default,
        x_resolution.error,
    )


def _render_display_section(
    x_source_columns: list[str],
    x_max_default: float,
    y_max_default: float,
    x_source_error: str | None,
) -> bool:
    """Render shared display settings and return whether ranges are valid."""
    ranges_valid = True

    with st.expander(
        "Display",
        expanded=st.session_state.get("expander_display", False),
        icon=":material/palette:",
    ):
        if x_source_columns:
            current_x_source = st.session_state.get("x_source_column")
            x_source_index = x_source_columns.index(current_x_source) if current_x_source in x_source_columns else 0
            st.selectbox(
                "X Source",
                options=x_source_columns,
                index=x_source_index,
                key="x_source_column_select",
                on_change=_handle_x_source_change,
            )
            st.session_state["x_source_column"] = st.session_state.get("x_source_column_select")
            if st.session_state.get("x_source_auto_selected"):
                st.warning(f'Column "{st.session_state["x_source_column"]}" was automatically selected as the X source.')
            elif x_source_error:
                st.warning(x_source_error)
        else:
            st.session_state["x_source_column"] = None
            st.session_state["x_source_auto_selected"] = False
            if x_source_error:
                st.info(x_source_error)

        st.caption("Formatting")
        st.slider("Width (mm)", min_value=100, max_value=500, step=5, key="plot_width")
        st.slider("Height (mm)", min_value=50, max_value=400, step=5, key="plot_height")
        st.slider("Tick Font Size", min_value=8, max_value=30, step=1, key="axis_annotation_fontsize")
        st.slider("Axis Font Size", min_value=8, max_value=40, step=1, key="axis_title_fontsize")
        st.slider("Line Width", min_value=0.1, max_value=4.0, step=0.05, key="line_width")

        st.divider()
        st.caption("Labels")
        st.text_input("X Axis", key="x_axis_label")
        st.text_input("Y Axis", key="y_axis_label")

        col1, col2 = st.columns(2)
        with col1:
            st.text_input("X Unit", key="x_unit")
        with col2:
            st.text_input("Y Unit", key="y_unit")

        st.divider()
        st.caption("Ranges")

        x_active, x_range_valid = _render_range_expander(
            title="Set X Range",
            axis_key="x",
            min_label="X Min",
            max_label="X Max",
            default_min=0.0,
            default_max=x_max_default,
        )
        st.session_state["set_x_range"] = x_active
        ranges_valid = ranges_valid and x_range_valid

        y_active, y_range_valid = _render_range_expander(
            title="Set Y Range",
            axis_key="y",
            min_label="Y Min",
            max_label="Y Max",
            default_min=0.0,
            default_max=y_max_default,
        )
        st.session_state["set_y_range"] = y_active
        ranges_valid = ranges_valid and y_range_valid

        col1, col2 = st.columns(2)
        x_step = col1.text_input(
            "X Tick Step",
            value=str(st.session_state.get("x_tick_step", PLOT_DEFAULTS.x_tick_step)),
            key="x_tick_step_ui",
        )
        y_step = col2.text_input(
            "Y Tick Step",
            value=str(st.session_state.get("y_tick_step", PLOT_DEFAULTS.y_tick_step)),
            key="y_tick_step_ui",
        )
        try:
            st.session_state["x_tick_step"] = float(x_step.replace(",", "."))
            st.session_state["y_tick_step"] = float(y_step.replace(",", "."))
        except ValueError:
            pass

    return ranges_valid


def _render_range_expander(
    *,
    title: str,
    axis_key: str,
    min_label: str,
    max_label: str,
    default_min: float,
    default_max: float,
) -> tuple[bool, bool]:
    """Render a manual range section and return (active, valid)."""
    min_ui_key = f"{axis_key}_min_ui"
    max_ui_key = f"{axis_key}_max_ui"
    min_state_key = f"{axis_key}_min"
    max_state_key = f"{axis_key}_max"

    if min_ui_key not in st.session_state:
        st.session_state[min_ui_key] = str(st.session_state.get(min_state_key, default_min)) if st.session_state.get(
            f"set_{axis_key}_range",
            False,
        ) else ""
    if max_ui_key not in st.session_state:
        st.session_state[max_ui_key] = str(st.session_state.get(max_state_key, default_max)) if st.session_state.get(
            f"set_{axis_key}_range",
            False,
        ) else ""

    current_min = (st.session_state.get(min_ui_key, "") or "").strip()
    current_max = (st.session_state.get(max_ui_key, "") or "").strip()
    expanded = bool(current_min or current_max)

    with st.expander(title, expanded=expanded):
        col1, col2 = st.columns(2)
        min_text = col1.text_input(min_label, key=min_ui_key, placeholder="Auto")
        max_text = col2.text_input(max_label, key=max_ui_key, placeholder="Auto")

    parsed_min, min_error = _parse_optional_float(min_text)
    parsed_max, max_error = _parse_optional_float(max_text)

    if min_error or max_error:
        st.warning(f"{title} requires valid numeric values or blank fields for Auto.")
        return (False, False)

    if parsed_min is None or parsed_max is None:
        return (False, True)

    st.session_state[min_state_key] = parsed_min
    st.session_state[max_state_key] = parsed_max

    if parsed_max <= parsed_min:
        st.warning(f"{max_label} must be greater than {min_label}.")
        return (False, False)

    return (True, True)


def _parse_optional_float(value: str | None) -> tuple[float | None, bool]:
    """Parse a text input into an optional float."""
    normalized = (value or "").strip()
    if not normalized:
        return (None, False)

    try:
        return (float(normalized.replace(",", ".")), False)
    except ValueError:
        return (None, True)


def _sync_x_source_state(x_source_columns: list[str]) -> str | None:
    """Keep the global X source selection in sync, including auto-defaults."""
    if not x_source_columns:
        st.session_state["x_source_column"] = None
        st.session_state["x_source_auto_selected"] = False
        return None

    current_x_source = st.session_state.get("x_source_column")
    if current_x_source in x_source_columns:
        st.session_state.setdefault("x_source_auto_selected", False)
        st.session_state["x_source_column_select"] = current_x_source
        return current_x_source

    auto_selected = x_source_columns[0]
    st.session_state["x_source_column"] = auto_selected
    st.session_state["x_source_column_select"] = auto_selected
    st.session_state["x_source_auto_selected"] = True
    return auto_selected


def _handle_x_source_change() -> None:
    """Mark a manual X source selection."""
    st.session_state["x_source_column"] = st.session_state.get("x_source_column_select")
    st.session_state["x_source_auto_selected"] = False


def _render_export_section() -> tuple[bool, str | None]:
    """Render export settings and return whether export was triggered."""
    export_format = None

    with st.expander("Export", expanded=False, icon=":material/download:"):
        st.text_input("File Name", key="export_filename")

        col1, col2 = st.columns(2)
        if col1.button("Generate\nPNG", key="export_png_button", use_container_width=True):
            export_format = "PNG"
        if col2.button("Generate\nPDF", key="export_pdf_button", use_container_width=True):
            export_format = "PDF"

        col3, col4 = st.columns(2)
        if col3.button("Generate\nSVG", key="export_svg_button", use_container_width=True):
            export_format = "SVG"
        if col4.button("Generate\nEPS", key="export_eps_button", use_container_width=True):
            export_format = "EPS"

    return (export_format is not None, export_format)


def _build_options_dict(
    all_available_columns: list[str],
    numeric_plot_columns: list[str],
    x_source_columns: list[str],
    export_trigger: bool,
    export_format: str | None,
    x_max_default: float,
    y_max_default: float,
    x_source_error: str | None,
) -> dict:
    """Build the shared options dictionary used by the tabs."""
    return {
        "plot_width": float(st.session_state.get("plot_width", PLOT_DEFAULTS.width)),
        "plot_height": float(st.session_state.get("plot_height", PLOT_DEFAULTS.height)),
        "axis_annotation_fontsize": int(st.session_state.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize)),
        "axis_title_fontsize": int(st.session_state.get("axis_title_fontsize", PLOT_DEFAULTS.axis_title_fontsize)),
        "line_width": float(st.session_state.get("line_width", PLOT_DEFAULTS.line_width)),
        "x_source_column": st.session_state.get("x_source_column"),
        "x_source_error": x_source_error,
        "x_axis_label": st.session_state.get("x_axis_label", PLOT_DEFAULTS.x_label),
        "y_axis_label": st.session_state.get("y_axis_label", PLOT_DEFAULTS.y_label),
        "x_unit": st.session_state.get("x_unit", PLOT_DEFAULTS.x_unit),
        "y_unit": st.session_state.get("y_unit", PLOT_DEFAULTS.y_unit),
        "x_tick_step": float(st.session_state.get("x_tick_step", PLOT_DEFAULTS.x_tick_step)),
        "y_tick_step": float(st.session_state.get("y_tick_step", PLOT_DEFAULTS.y_tick_step)),
        "set_x_range": bool(st.session_state.get("set_x_range", False)),
        "set_y_range": bool(st.session_state.get("set_y_range", False)),
        "x_min": float(st.session_state.get("x_min", 0.0)),
        "x_max": float(st.session_state.get("x_max", x_max_default)),
        "y_min": float(st.session_state.get("y_min", 0.0)),
        "y_max": float(st.session_state.get("y_max", y_max_default)),
        "ranges_valid": bool(st.session_state.get("ranges_valid", True)),
        "export_trigger": export_trigger,
        "export_format": export_format,
        "export_filename": st.session_state.get("export_filename", EXPORT_DEFAULTS.filename),
        "all_available_columns": all_available_columns,
        "numeric_plot_columns": numeric_plot_columns,
        "x_source_columns": x_source_columns,
    }
