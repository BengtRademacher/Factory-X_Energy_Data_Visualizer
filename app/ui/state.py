"""Session State Management für die Factory-X Plotting-App.

Dieses Modul verwaltet alle Streamlit Session-State Variablen und stellt sicher,
dass Einstellungen beim Tab-Wechsel erhalten bleiben.
"""

import streamlit as st
from app.config import (
    PLOT_DEFAULTS,
    BAR_DEFAULTS,
    BOX_DEFAULTS,
    DONUT_DEFAULTS,
    SCATTER_DEFAULTS,
    HISTOGRAM_DEFAULTS,
    SANKEY_DEFAULTS,
    SECONDARY_AXIS_DEFAULTS,
    EXPORT_DEFAULTS,
)


def initialize_state() -> None:
    """Initialisiert den Session State für alle UI-Optionen."""
    
    # Refresh-Counter für Diagramm-Redraw
    if "plot_refresh_counter" not in st.session_state:
        st.session_state["plot_refresh_counter"] = 0

    # Global Settings
    _init_global_state()
    
    # Plot-spezifische Settings (Memory pro Tab)
    _init_line_plot_state()
    _init_bar_plot_state()
    _init_box_plot_state()
    _init_donut_state()
    _init_scatter_state()
    _init_histogram_state()
    _init_sankey_state()
    
    # Export Settings
    _init_export_state()
    
    # UI-Zustände
    _init_ui_state()


def _init_global_state() -> None:
    """Globale Einstellungen, die für alle Plots gelten."""
    defaults = {
        # Dimensionen
        "plot_width": float(PLOT_DEFAULTS.width),
        "plot_height": float(PLOT_DEFAULTS.height),
        
        # Schrift und Linien
        "axis_annotation_fontsize": int(PLOT_DEFAULTS.axis_fontsize),
        "axis_title_fontsize": int(PLOT_DEFAULTS.axis_title_fontsize),
        "line_width": float(PLOT_DEFAULTS.line_width),
        
        # Achsen-Labels
        "x_axis_label": PLOT_DEFAULTS.x_label,
        "y_axis_label": PLOT_DEFAULTS.y_label,
        "x_unit": PLOT_DEFAULTS.x_unit,
        "y_unit": PLOT_DEFAULTS.y_unit,
        
        # Tick-Schrittweiten
        "x_tick_step": float(PLOT_DEFAULTS.x_tick_step),
        "y_tick_step": float(PLOT_DEFAULTS.y_tick_step),
        
        # Achsenbereiche
        "set_x_range": False,
        "x_min": float(PLOT_DEFAULTS.x_min),
        "x_max": float(PLOT_DEFAULTS.x_max),
        "set_y_range": False,
        "y_min": float(PLOT_DEFAULTS.y_min),
        "y_max": float(PLOT_DEFAULTS.y_max),
        
        # Datenverarbeitung
        "component_aliases": {},
        "time_column_name": None,
        "time_range_start": None,
        "time_range_end": None,
        
        # Validierung
        "ranges_valid": True,
    }
    _set_defaults(defaults)


def _init_line_plot_state() -> None:
    """State für Linienplots."""
    defaults = {
        "line_selected_components": [],
        "line_colors": {},
        
        # Sekundäre Achse
        "secondary_axis_enabled": SECONDARY_AXIS_DEFAULTS.enabled,
        "secondary_axis_components": [],
        "secondary_axis_colors": {},
        "secondary_axis_label": SECONDARY_AXIS_DEFAULTS.label,
        "secondary_axis_unit": SECONDARY_AXIS_DEFAULTS.unit,
        "secondary_axis_tick_step": SECONDARY_AXIS_DEFAULTS.tick_step,
        "secondary_axis_set_range": False,
        "secondary_axis_min": SECONDARY_AXIS_DEFAULTS.min_value,
        "secondary_axis_max": SECONDARY_AXIS_DEFAULTS.max_value,
        "secondary_ranges_valid": True,
    }
    _set_defaults(defaults)


def _init_bar_plot_state() -> None:
    """State für Säulendiagramme."""
    defaults = {
        "bar_selected_components": [],
        "bar_colors": {},
        "bar_mode": BAR_DEFAULTS.mode,
        "bar_width": BAR_DEFAULTS.bar_width,
        "bar_label_rotation": BAR_DEFAULTS.label_rotation,
        "bar_hide_x_labels": BAR_DEFAULTS.hide_x_labels,
        
        # Vergleichssäule
        "bar_show_compare": False,
        "bar_compare_components": [],
    }
    _set_defaults(defaults)


def _init_box_plot_state() -> None:
    """State für Boxplots."""
    defaults = {
        "box_selected_components": [],
        "box_colors": {},
        "box_width": BOX_DEFAULTS.box_width,
        "box_label_rotation": BOX_DEFAULTS.label_rotation,
    }
    _set_defaults(defaults)


def _init_donut_state() -> None:
    """State für Donut-Diagramme."""
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
    """State für Scatter-Plots."""
    defaults = {
        # Selectbox-Keys (werden direkt von Widgets verwendet)
        "scatter_x_select": "-",
        "scatter_y_select": "-",
        "scatter_color_select": "-",
        # Interne Werte (ohne "-" Platzhalter)
        "scatter_x": None,
        "scatter_y": None,
        "scatter_color": None,
        # Scatter-Optionen
        "scatter_point_size": SCATTER_DEFAULTS.point_size,
        "scatter_edge_width": SCATTER_DEFAULTS.edge_width,
        "scatter_x_unit": SCATTER_DEFAULTS.x_unit,
        "scatter_y_unit": SCATTER_DEFAULTS.y_unit,
        "scatter_color_label": SCATTER_DEFAULTS.color_label,
    }
    _set_defaults(defaults)


def _init_histogram_state() -> None:
    """State für Histogramme."""
    defaults = {
        "histogram_components": [],
        "histogram_colors": {},
        "histogram_bins": HISTOGRAM_DEFAULTS.bins,
        "histogram_line_width": HISTOGRAM_DEFAULTS.line_width,
    }
    _set_defaults(defaults)


def _init_sankey_state() -> None:
    """State für Sankey-Diagramme."""
    defaults = {
        "sankey_selected_elektrisch": [],
        "sankey_selected_pneumatisch": [],
        "sankey_productive_vars": [],
        "sankey_colors": {},
        "sankey_mode": SANKEY_DEFAULTS.mode,
        "sankey_unit": SANKEY_DEFAULTS.unit,
        "sankey_title": SANKEY_DEFAULTS.title,
    }
    _set_defaults(defaults)


def _init_export_state() -> None:
    """State für Export-Einstellungen."""
    defaults = {
        "export_filename": EXPORT_DEFAULTS.filename,
        "export_formats": EXPORT_DEFAULTS.formats.copy(),
        "export_separate_files": EXPORT_DEFAULTS.separate_files,
        
        # Donut-spezifischer Export
        "donut_export_filename": "donut_export",
        "donut_export_formats": ["PDF", "PNG"],
        "donut_export_separate": False,
    }
    _set_defaults(defaults)


def _init_ui_state() -> None:
    """State für UI-Elemente (Expander, etc.)."""
    defaults = {
        "active_tab_name": "Linienplots",
    }
    _set_defaults(defaults)


def reset_ui_state() -> None:
    """Setzt selektiv UI-Elemente (Slider, Textfelder) zurück.
    
    Resettet globale Einstellungen und UI-Elemente in allen Tabs.
    Ignoriert Komponenten-Auswahlen, Farben, Dropdowns und Aliase.
    """
    # Muster für Slider und Textfelder (diese werden gelöscht)
    ui_patterns = [
        "_width", "_rotation", "_bins", "_size", "_hole", "_step", 
        "_label", "_unit", "_title", "_filename", "_min", "_max", 
        "_tick_step", "_range", "plot_width", "plot_height", "axis_annotation_fontsize",
        "axis_title_fontsize", "line_width", "x_axis_label", "y_axis_label"
    ]
    
    # Keys, die NIEMALS resettet werden sollen (Ausschlussliste für Dropdowns/Listen)
    exclude_patterns = [
        "_selected", "_colors", "_color_", "component_aliases",
        "processed_data", "_components", "_vars", "_mode", "_select",
        "_options", "_aggregation", "_axis", "_type", "_source", "_label_mode"
    ]
    
    for key in list(st.session_state.keys()):
        # Prüfen ob der Key zu den UI-Elementen passt
        is_ui_element = any(pat in key for pat in ui_patterns)
        
        # Ausschlusskriterien prüfen
        is_excluded = any(pat in key for pat in exclude_patterns)
        
        if is_ui_element and not is_excluded:
            st.session_state.pop(key, None)

    # Refresh Counter erhöhen
    st.session_state["plot_refresh_counter"] = st.session_state.get("plot_refresh_counter", 0) + 1


def _set_defaults(defaults: dict) -> None:
    """Setzt Standardwerte nur, wenn sie noch nicht existieren.
    
    Stellt sicher, dass die Typen (int/float) exakt erhalten bleiben,
    damit Streamlit-Widgets sie korrekt als Initialwerte erkennen.
    """
    for key, value in defaults.items():
        if key not in st.session_state:
            # Explizite Konvertierung für numerische Werte zur Typsicherheit
            if isinstance(value, float):
                st.session_state[key] = float(value)
            elif isinstance(value, int) and not isinstance(value, bool):
                st.session_state[key] = int(value)
            else:
                st.session_state[key] = value


def get_state(key: str, default=None):
    """Holt einen Wert aus dem Session State."""
    return st.session_state.get(key, default)


def set_state(key: str, value) -> None:
    """Setzt einen Wert im Session State."""
    st.session_state[key] = value
