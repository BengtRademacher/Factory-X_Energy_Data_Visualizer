"""Boxplot Tab für die Factory-X Plotting-App."""

import streamlit as st
from typing import Tuple

from app.config import DEFAULT_COLORS, PLOT_DEFAULTS, BOX_DEFAULTS
from app.plotting import plot_boxplot
from app.export import export_plots
from app.ui.components import render_color_selector


def render(processed, options: dict) -> None:
    """Rendert den Boxplot Tab."""
    
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
            default=st.session_state.get("box_selected_components", []),
            key="box_selected_components"
        )
        
        # Farben
        colors = _render_color_picker(components, "box")
        
        st.divider()
        
        # Boxplot-Optionen
        box_width = st.slider(
            "Box-Breite",
            0.1, 1.2,
            step=0.05,
            key="box_width"
        )
        
        label_rotation = st.slider(
            "Beschriftungswinkel",
            0, 90,
            step=5,
            key="box_label_rotation"
        )
    
    with main_col:
        if not components:
            st.info("Bitte wählen Sie mindestens eine Komponente aus.")
            return
        
        fig = plot_boxplot(
            df_by_file=processed.frames_by_file,
            components=components,
            title="Boxplot",
            figsize=_figure_size(options),
            axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
            axis_title_fontsize=options.get("axis_title_fontsize", PLOT_DEFAULTS.axis_title_fontsize),
            colors=colors,
            line_width=options.get("line_width", PLOT_DEFAULTS.line_width),
            label_rotation=label_rotation,
            ylim=None,
            y_unit=options.get("y_unit", PLOT_DEFAULTS.y_unit),
            legend_inside=False,
            y_tick_step=options.get("y_tick_step"),
            y_label=options.get("y_axis_label", PLOT_DEFAULTS.y_label),
            box_width=box_width,
        )
        
        if fig:
            st.pyplot(fig, width="stretch")
            
            if options.get("export_trigger") and options.get("export_format"):
                export_plots(
                    [("Boxplot", fig)],
                    options.get("export_filename", "export"),
                    options.get("export_format"),
                )
            import matplotlib.pyplot as plt
            plt.close(fig)


def _render_color_picker(components: list, prefix: str) -> dict:
    """Rendert Farbauswahl für die Komponenten."""
    
    colors = {}
    if not components:
        return colors
    
    with st.expander("🎨 Farben", expanded=False):
        for i, comp in enumerate(components):
            key = f"{prefix}_color_{comp}"
            default = DEFAULT_COLORS[i % len(DEFAULT_COLORS)]
            colors[comp] = render_color_selector(f"{comp}", key, default)
    
    st.session_state[f"{prefix}_colors"] = colors
    return colors


def _figure_size(options: dict) -> Tuple[float, float]:
    """Berechnet die Figurengröße aus den Optionen (mm -> Zoll)."""
    width_mm = float(options.get("plot_width", PLOT_DEFAULTS.width))
    height_mm = float(options.get("plot_height", PLOT_DEFAULTS.height))
    return (width_mm / 25.4, height_mm / 25.4)

