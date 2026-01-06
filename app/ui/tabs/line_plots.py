"""Linienplot Tab für die Factory-X Plotting-App."""

import streamlit as st
from typing import List, Tuple

from app.config import DEFAULT_COLORS, MAX_PLOT_ROWS, PLOT_DEFAULTS
from app.plotting import plot_line
from app.export import export_plots


def render(processed, options: dict) -> None:
    """Rendert den Linienplot Tab."""
    
    if not processed.has_data:
        st.info("Bitte laden Sie Dateien hoch, um Diagramme zu erstellen.")
        return
    
    if not options.get("ranges_valid", True):
        st.warning("Ungültige Achsenbereiche: Bitte korrigieren Sie Y-Min < Y-Max und X-Min < X-Max.")
        return
    
    # Zwei-Spalten-Layout
    main_col, custom_col = st.columns([4, 1])
    
    alias_pool = options.get("alias_pool", [])
    
    with custom_col:
        st.markdown("### ⚙️ Optionen")
        
        # Komponentenauswahl
        components = st.multiselect(
            "Komponenten",
            options=alias_pool,
            default=st.session_state.get("line_selected_components", []),
            key="line_selected_components"
        )
        
        # Farben
        colors = _render_color_picker(components, "line")
        
        st.divider()
        
        # Sekundäre Achse
        secondary_args = _render_secondary_axis(alias_pool, options)
    
    with main_col:
        if not components:
            st.info("Bitte wählen Sie mindestens eine Komponente aus.")
            return
        
        # Daten vorbereiten
        combined_df = processed.combined_frame
        if len(combined_df) > MAX_PLOT_ROWS:
            combined_df = combined_df.sample(n=MAX_PLOT_ROWS, random_state=42)
            st.info(f"Großer Datensatz: Gesampelt auf {MAX_PLOT_ROWS:,} Zeilen.")
        
        # Plot erstellen
        xlim = None
        if options.get("set_x_range"):
            xlim = (options.get("x_min"), options.get("x_max"))
        
        ylim = None
        if options.get("set_y_range"):
            ylim = (options.get("y_min"), options.get("y_max"))
        
        fig = plot_line(
            combined_df=combined_df,
            file_boundaries=processed.file_boundaries,
            components=components,
            title="Linienplot",
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
            **secondary_args,
        )
        
        if fig:
            st.pyplot(fig, width="stretch")
            
            if options.get("export_trigger") and options.get("export_format"):
                export_plots(
                    [("Linienplot", fig)],
                    options.get("export_filename", "export"),
                    options.get("export_format"),
                )
            import matplotlib.pyplot as plt
            plt.close(fig)


def _render_color_picker(components: list, prefix: str) -> dict:
    """Rendert Color-Picker für die Komponenten."""
    
    colors = {}
    if not components:
        return colors
    
    with st.expander("🎨 Farben", expanded=False):
        for i, comp in enumerate(components):
            key = f"{prefix}_color_{comp}"
            default = st.session_state.get(key, DEFAULT_COLORS[i % len(DEFAULT_COLORS)])
            colors[comp] = st.color_picker(f"{comp}", value=default, key=key)
    
    st.session_state[f"{prefix}_colors"] = colors
    return colors


def _render_secondary_axis(alias_pool: list, options: dict) -> dict:
    """Rendert die Einstellungen für die sekundäre Achse."""
    
    st.checkbox("Sekundäre Y-Achse", key="secondary_axis_enabled")
    
    if not st.session_state.get("secondary_axis_enabled"):
        return {}
    
    secondary_components = st.multiselect(
        "Sekundär-Komponenten",
        options=alias_pool,
        key="secondary_axis_components",
    )
    
    secondary_colors = {}
    if secondary_components:
        with st.expander("Sekundär-Farben", expanded=False):
            for i, comp in enumerate(secondary_components):
                key = f"secondary_color_{comp}"
                default = st.session_state.get(key, DEFAULT_COLORS[(i + 4) % len(DEFAULT_COLORS)])
                secondary_colors[comp] = st.color_picker(f"{comp}", value=default, key=key)
    
    st.text_input("Sekundär-Label", key="secondary_axis_label")
    st.text_input("Sekundär-Einheit", key="secondary_axis_unit")
    st.number_input("Sekundär-Tick-Schrittweite", min_value=0.0, key="secondary_axis_tick_step")
    
    st.checkbox("Sekundär-Bereich festlegen", key="secondary_axis_set_range")
    
    secondary_ylim = None
    if st.session_state.get("secondary_axis_set_range"):
        sec_min = st.number_input("Sekundär-Min", key="secondary_axis_min")
        sec_max = st.number_input("Sekundär-Max", key="secondary_axis_max")
        if sec_max > sec_min:
            secondary_ylim = (sec_min, sec_max)
        else:
            st.warning("Sekundär-Max muss größer als Sekundär-Min sein.")
    
    return {
        "secondary_components": secondary_components,
        "secondary_colors": secondary_colors,
        "secondary_y_unit": st.session_state.get("secondary_axis_unit", ""),
        "secondary_y_label": st.session_state.get("secondary_axis_label", "Sekundärwert"),
        "secondary_y_tick_step": st.session_state.get("secondary_axis_tick_step"),
        "secondary_ylim": secondary_ylim,
    }


def _figure_size(options: dict) -> Tuple[float, float]:
    """Berechnet die Figurengröße aus den Optionen (mm -> Zoll)."""
    width_mm = float(options.get("plot_width", PLOT_DEFAULTS.width))
    height_mm = float(options.get("plot_height", PLOT_DEFAULTS.height))
    return (width_mm / 25.4, height_mm / 25.4)

