"""Globale Sidebar für die Factory-X Plotting-App.

Enthält:
- Datei-Upload
- Globale Zeitfilter und Aliasing
- Projektweite Darstellungseinstellungen
- Export-Einstellungen
"""

import streamlit as st
import pandas as pd
import numpy as np

from app.config import (
    PLOT_DEFAULTS,
    EXPORT_DEFAULTS,
    VARS_ELEKTRISCH,
    VARS_PNEUMATISCH,
)
from app.ui.state import initialize_state, reset_ui_state


def render_sidebar(combined_df: pd.DataFrame | None) -> dict:
    """Rendert die globale Sidebar und gibt die Optionen zurück."""
    
    st.sidebar.header("Einstellungen")
    
    # Berechne verfügbare Spalten und Defaults
    numeric_cols = []
    y_max_default = 100.0
    x_max_default = 100.0
    
    if combined_df is not None and not combined_df.empty:
        numeric_cols = combined_df.select_dtypes(include=np.number).columns.tolist()
        numeric_cols_without_elapsed = [c for c in numeric_cols if c != "elapsedTime"]
        if numeric_cols_without_elapsed:
            y_max_default = float(combined_df[numeric_cols_without_elapsed].max().max())
        if "elapsedTime" in combined_df.columns:
            x_max_default = float(combined_df["elapsedTime"].dt.total_seconds().max())
    
    available_columns = list(combined_df.columns) if combined_df is not None and not combined_df.empty else []
    
    # Komponenten-Pool
    component_pool = sorted(set(VARS_ELEKTRISCH + VARS_PNEUMATISCH))
    current_aliases = dict(st.session_state.get("component_aliases", {}))
    alias_pool = sorted(set(component_pool + list(current_aliases.keys()) + list(current_aliases.values())))
    if not alias_pool:
        alias_pool = component_pool
    
    with st.sidebar:
        # Data Processing Section
        _render_data_processing_section(available_columns, combined_df)
        
        # Darstellung Section
        ranges_valid = _render_display_section(x_max_default, y_max_default)
        st.session_state["ranges_valid"] = ranges_valid
        
        # Export Section
        export_trigger, export_format = _render_export_section()

        st.divider()
        st.button(
            "Standardwerte wiederherstellen", 
            key="reset_button", 
            use_container_width=True, 
            type="secondary",
            on_click=reset_ui_state
        )
    
    # Aktualisiere alias_pool nach möglichen Änderungen
    current_aliases = dict(st.session_state.get("component_aliases", {}))
    alias_pool = sorted(set(component_pool + list(current_aliases.keys()) + list(current_aliases.values()) + available_columns))
    
    return _build_options_dict(alias_pool, export_trigger, export_format, x_max_default, y_max_default)


def _render_data_processing_section(available_columns: list, combined_df: pd.DataFrame | None) -> None:
    """Rendert die Datenverarbeitungs-Einstellungen."""
    
    current_aliases = dict(st.session_state.get("component_aliases", {}))
    
    with st.expander("📊 Datenverarbeitung", expanded=st.session_state.get("expander_vorverarbeitung", False)):
        st.caption("Mapping und Zeitfilter")
        
        if available_columns:
            # Alias-Formular
            with st.form("alias_form"):
                original_choice = st.selectbox(
                    "Originalspalte",
                    options=available_columns,
                    key="alias_original_select",
                )
                alias_value = st.text_input(
                    "Alias-Name",
                    value=current_aliases.get(original_choice, "") if original_choice else "",
                    key="alias_value_input",
                ).strip()
                submit_alias = st.form_submit_button("Alias hinzufügen")
            
            if submit_alias and alias_value and original_choice:
                current_aliases[original_choice] = alias_value
                st.session_state["component_aliases"] = dict(current_aliases)
                st.success(f"Alias für '{original_choice}' gesetzt.")
            
            # Alias-Tabelle
            if current_aliases:
                st.table(pd.DataFrame(
                    sorted(current_aliases.items()),
                    columns=["Original", "Alias"]
                ))
                
                remove_choice = st.selectbox(
                    "Alias entfernen",
                    options=["-"] + list(current_aliases.keys()),
                    key="alias_remove_select",
                )
                if st.button("Entfernen", key="alias_remove_button"):
                    if remove_choice != "-":
                        current_aliases.pop(remove_choice, None)
                        st.session_state["component_aliases"] = dict(current_aliases)
        
        # Zeitfilter
        _render_time_filter(available_columns, combined_df)


def _render_time_filter(available_columns: list, combined_df: pd.DataFrame | None) -> None:
    """Rendert den globalen Zeitfilter."""
    
    time_options = ["(keine)", "(Index)"] + sorted(set(available_columns))
    default_time_col = st.session_state.get("time_column_name")
    
    time_index = 0
    if default_time_col and default_time_col in time_options:
        time_index = time_options.index(default_time_col)
    elif "elapsedTime" in time_options:
        time_index = time_options.index("elapsedTime")
    
    selected_time_label = st.selectbox(
        "Zeitquelle",
        options=time_options,
        index=time_index,
        key="time_column_select",
    )
    
    if selected_time_label == "(keine)":
        st.session_state["time_column_name"] = None
        st.session_state["time_range_start"] = None
        st.session_state["time_range_end"] = None
    elif selected_time_label == "(Index)":
        st.session_state["time_column_name"] = "__index__"
    else:
        st.session_state["time_column_name"] = selected_time_label
    
    # Zeit-Range Inputs
    if st.session_state.get("time_column_name"):
        col1, col2 = st.columns(2)
        with col1:
            start_text = st.text_input(
                "Zeitstart (s)",
                value="" if st.session_state.get("time_range_start") is None else str(st.session_state["time_range_start"]),
                key="time_range_start_text",
            )
            start_value = _parse_float(start_text)
            st.session_state["time_range_start"] = start_value
        
        with col2:
            end_text = st.text_input(
                "Zeitende (s)",
                value="" if st.session_state.get("time_range_end") is None else str(st.session_state["time_range_end"]),
                key="time_range_end_text",
            )
            end_value = _parse_float(end_text)
            st.session_state["time_range_end"] = end_value


def _render_display_section(x_max_default: float, y_max_default: float) -> bool:
    """Rendert die Darstellungs-Einstellungen. Gibt zurück, ob Ranges valide sind."""
    
    ranges_valid = True
    
    with st.expander("🎨 Darstellung", expanded=st.session_state.get("expander_darstellung", False)):
        st.caption("Formatierung")
        st.slider("Breite (mm)", 
                  min_value=100.0, max_value=500.0, step=10.0, 
                  key="plot_width")
        st.slider("Höhe (mm)", 
                  min_value=50.0, max_value=400.0, step=10.0, 
                  key="plot_height")
        st.slider("Schriftgröße (Ticks)", 
                  min_value=8, max_value=30, step=1, 
                  key="axis_annotation_fontsize")
        st.slider("Schriftgröße (Achsen)", 
                  min_value=8, max_value=40, step=1, 
                  key="axis_title_fontsize")
        st.slider("Liniendicke", 
                  min_value=0.1, max_value=4.0, step=0.05, 
                  key="line_width")
        
        st.divider()
        st.caption("Beschriftung")
        
        st.text_input("X-Achse", key="x_axis_label")
        st.text_input("Y-Achse", key="y_axis_label")
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Einheit X", key="x_unit")
        with col2:
            st.text_input("Einheit Y", key="y_unit")
        
        st.divider()
        st.caption("Bereich festlegen")
        
        st.checkbox("Range X", key="set_x_range")
        if st.session_state.get("set_x_range"):
            c1, c2 = st.columns(2)
            x_min = c1.text_input("X-Min", value=str(st.session_state.get("x_min", 0.0)), key="x_min_ui")
            x_max = c2.text_input("X-Max", value=str(st.session_state.get("x_max", x_max_default)), key="x_max_ui")
            try:
                st.session_state["x_min"] = float(x_min.replace(",", "."))
                st.session_state["x_max"] = float(x_max.replace(",", "."))
            except ValueError: pass
            
            if st.session_state.get("x_max", x_max_default) <= st.session_state.get("x_min", 0.0):
                st.warning("X-Max muss größer als X-Min sein.")
                ranges_valid = False
        
        st.checkbox("Range Y", key="set_y_range")
        if st.session_state.get("set_y_range"):
            c1, c2 = st.columns(2)
            y_min = c1.text_input("Y-Min", value=str(st.session_state.get("y_min", 0.0)), key="y_min_ui")
            y_max = c2.text_input("Y-Max", value=str(st.session_state.get("y_max", y_max_default)), key="y_max_ui")
            try:
                st.session_state["y_min"] = float(y_min.replace(",", "."))
                st.session_state["y_max"] = float(y_max.replace(",", "."))
            except ValueError: pass
            
            if st.session_state.get("y_max", y_max_default) <= st.session_state.get("y_min", 0.0):
                st.warning("Y-Max muss größer als Y-Min sein.")
                ranges_valid = False
        
        c1, c2 = st.columns(2)
        x_step = c1.text_input("Schrittweite X", value=str(st.session_state.get("x_tick_step", PLOT_DEFAULTS.x_tick_step)), key="x_tick_step_ui")
        y_step = c2.text_input("Schrittweite Y", value=str(st.session_state.get("y_tick_step", PLOT_DEFAULTS.y_tick_step)), key="y_tick_step_ui")
        try:
            st.session_state["x_tick_step"] = float(x_step.replace(",", "."))
            st.session_state["y_tick_step"] = float(y_step.replace(",", "."))
        except ValueError: pass

    return ranges_valid


def _render_export_section() -> tuple[bool, str | None]:
    """Rendert die Export-Einstellungen. Gibt zurück, ob Export getriggert wurde und welches Format."""
    
    export_format = None
    
    with st.expander("💾 Export", expanded=False):
        st.text_input("Dateiname", key="export_filename")
        
        st.caption("Exportformat wählen:")
        c1, c2 = st.columns(2)
        if c1.button("Generiere PNG", key="export_png_button", use_container_width=True):
            export_format = "PNG"
        if c2.button("Generiere PDF", key="export_pdf_button", use_container_width=True):
            export_format = "PDF"
        
        c3, c4 = st.columns(2)
        if c3.button("Generiere SVG", key="export_svg_button", use_container_width=True):
            export_format = "SVG"
        if c4.button("Generiere EPS", key="export_eps_button", use_container_width=True):
            export_format = "EPS"
    
    return (export_format is not None, export_format)


def _parse_float(text: str) -> float | None:
    """Parst einen String zu float, gibt None bei leerem String zurück."""
    cleaned = text.strip().replace(",", ".")
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _build_options_dict(alias_pool: list, export_trigger: bool, export_format: str | None, x_max_default: float, y_max_default: float) -> dict:
    """Baut das Options-Dictionary für die Render-Funktionen."""
    
    return {
        # Dimensionen (in mm)
        "plot_width": float(st.session_state.get("plot_width", PLOT_DEFAULTS.width)),
        "plot_height": float(st.session_state.get("plot_height", PLOT_DEFAULTS.height)),
        
        # Schrift und Linien
        "axis_annotation_fontsize": int(st.session_state.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize)),
        "axis_title_fontsize": int(st.session_state.get("axis_title_fontsize", PLOT_DEFAULTS.axis_title_fontsize)),
        "line_width": float(st.session_state.get("line_width", PLOT_DEFAULTS.line_width)),
        
        # Achsen
        "x_axis_label": st.session_state.get("x_axis_label", PLOT_DEFAULTS.x_label),
        "y_axis_label": st.session_state.get("y_axis_label", PLOT_DEFAULTS.y_label),
        "x_unit": st.session_state.get("x_unit", PLOT_DEFAULTS.x_unit),
        "y_unit": st.session_state.get("y_unit", PLOT_DEFAULTS.y_unit),
        "x_tick_step": float(st.session_state.get("x_tick_step", PLOT_DEFAULTS.x_tick_step)),
        "y_tick_step": float(st.session_state.get("y_tick_step", PLOT_DEFAULTS.y_tick_step)),
        
        # Bereiche
        "set_x_range": bool(st.session_state.get("set_x_range", False)),
        "set_y_range": bool(st.session_state.get("set_y_range", False)),
        "x_min": float(st.session_state.get("x_min", 0.0)),
        "x_max": float(st.session_state.get("x_max", x_max_default)),
        "y_min": float(st.session_state.get("y_min", 0.0)),
        "y_max": float(st.session_state.get("y_max", y_max_default)),
        
        # Datenverarbeitung
        "component_aliases": st.session_state.get("component_aliases", {}),
        "time_column_name": st.session_state.get("time_column_name"),
        "time_range_start": st.session_state.get("time_range_start"),
        "time_range_end": st.session_state.get("time_range_end"),
        
        # Validierung
        "ranges_valid": bool(st.session_state.get("ranges_valid", True)),
        
        # Export
        "export_trigger": export_trigger,
        "export_format": export_format,
        "export_filename": st.session_state.get("export_filename", EXPORT_DEFAULTS.filename),
        
        # Pool
        "alias_pool": alias_pool,
    }

