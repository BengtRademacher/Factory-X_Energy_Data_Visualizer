"""Histogramm Tab für die Factory-X Plotting-App."""

import streamlit as st
import pandas as pd
from typing import Tuple, List

from app.config import DEFAULT_COLORS, PLOT_DEFAULTS, HISTOGRAM_DEFAULTS
from app.plotting import plot_histogram
from app.export import export_plots


def render(processed, options: dict) -> None:
    """Rendert den Histogramm Tab."""
    
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
            default=st.session_state.get("histogram_components", []),
            key="histogram_components"
        )
        
        # Farben
        colors = _render_color_picker(components, "histogram")
        
        st.divider()
        
        # Histogramm-Optionen
        bins = st.slider(
            "Anzahl Bins",
            min_value=10,
            max_value=200,
            step=5,
            key="histogram_bins"
        )
        
        line_width = st.slider(
            "Linienbreite",
            min_value=0.5,
            max_value=5.0,
            step=0.5,
            key="histogram_line_width"
        )
    
    with main_col:
        if not components:
            st.info("Bitte wählen Sie mindestens eine Komponente aus.")
            return
        
        plots_to_export: List[Tuple[str, object]] = []
        combined_df = processed.combined_frame
        
        for i, comp in enumerate(components):
            if comp not in combined_df.columns:
                st.warning(f"Spalte '{comp}' nicht gefunden.")
                continue
            
            series = pd.to_numeric(combined_df[comp], errors="coerce")
            if series.isna().all():
                st.warning(f"Spalte '{comp}' enthält keine numerischen Daten.")
                continue
            
            color = colors.get(comp, DEFAULT_COLORS[i % len(DEFAULT_COLORS)])
            
            fig = plot_histogram(
                series=series,
                title=f"Histogramm – {comp}",
                figsize=_figure_size(options),
                axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
                axis_title_fontsize=options.get("axis_title_fontsize", PLOT_DEFAULTS.axis_title_fontsize),
                bins=bins,
                line_width=line_width,
                color=color,
                x_label=comp,
                y_label="Prozent",
                x_unit=options.get("y_unit", PLOT_DEFAULTS.y_unit),  # Einheit der Komponente
                y_unit="%",
            )
            
            if fig is not None:
                st.pyplot(fig, width="stretch")
                plots_to_export.append((f"Histogramm – {comp}", fig))
                import matplotlib.pyplot as plt
                plt.close(fig)
        
        # Export über globalen Trigger
        if options.get("export_trigger") and options.get("export_format") and plots_to_export:
            export_plots(
                plots_to_export,
                options.get("export_filename", "export"),
                options.get("export_format"),
            )


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

