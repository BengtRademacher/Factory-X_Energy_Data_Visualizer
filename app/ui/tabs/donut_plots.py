"""Donut/Tortendiagramm Tab für die Factory-X Plotting-App."""

import streamlit as st
from typing import Tuple

from app.config import DEFAULT_COLORS, PLOT_DEFAULTS, DONUT_DEFAULTS
from app.plotting import plot_donut
from app.export import export_plots


def render(processed, options: dict) -> None:
    """Rendert den Donut Tab."""
    
    if not processed.has_data:
        st.info("Bitte laden Sie Dateien hoch, um Diagramme zu erstellen.")
        return
    
    if not options.get("ranges_valid", True):
        st.warning("Ungültige Achsenbereiche.")
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
            default=st.session_state.get("donut_components", []),
            key="donut_components"
        )
        
        # Farben
        colors = _render_color_picker(components, "donut")
        
        st.divider()
        
        # Donut-Optionen
        hole = st.slider(
            "Donut-Öffnung",
            0.0, 0.9,
            step=0.05,
            key="donut_hole"
        )
        
        chart_size = st.slider(
            "Diagrammgröße (px)",
            300, 1000,
            step=10,
            key="donut_chart_size"
        )
        
        label_mode = st.selectbox(
            "Beschriftung",
            ["Prozent", "kW"],
            key="donut_label_mode"
        )
        
        show_legend = st.checkbox(
            "Legende anzeigen",
            key="donut_show_legend"
        )
        
        show_others = st.checkbox(
            "'Others'-Segment",
            key="donut_show_others"
        )
        
        total_target_kw = st.number_input(
            "Skalierter Gesamtbedarf (kW)",
            min_value=0.0,
            step=0.5,
            key="donut_total_target_kw"
        )
        
        title = st.text_input(
            "Titel",
            key="donut_title"
        )
        
        # Others-Farbe
        if show_others:
            key = "donut_color_Others"
            default = st.session_state.get(key, "#888888")
            colors["Others"] = st.color_picker("Farbe: Others", value=default, key=key)
    
    with main_col:
        if not components:
            st.info("Bitte wählen Sie mindestens eine Komponente aus.")
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
        )
        
        if fig is None:
            st.warning("Die ausgewählten Komponenten enthalten keine verwertbaren Werte.")
            return
        
        st.pyplot(fig, width="stretch")
        
        # Globaler Export über Sidebar
        if options.get("export_trigger") and options.get("export_format"):
            export_plots(
                [(title, fig)],
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


def _figure_size(options: dict) -> Tuple[float, float]:
    """Berechnet die Figurengröße aus den Optionen (mm -> Zoll)."""
    width_mm = float(options.get("plot_width", PLOT_DEFAULTS.width))
    height_mm = float(options.get("plot_height", PLOT_DEFAULTS.height))
    return (width_mm / 25.4, height_mm / 25.4)

