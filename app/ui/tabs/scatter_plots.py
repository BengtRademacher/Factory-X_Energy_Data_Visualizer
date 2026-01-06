"""Scatter Plot Tab für die Factory-X Plotting-App."""

import streamlit as st
from typing import Tuple

from app.config import PLOT_DEFAULTS, SCATTER_DEFAULTS, MAX_PLOT_ROWS
from app.plotting import plot_scatter
from app.export import export_plots


def render(processed, options: dict) -> None:
    """Rendert den Scatter Plot Tab."""
    
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
        
        # Achsenauswahl
        x_options = ["-"] + alias_pool
        y_options = ["-"] + alias_pool
        color_options = ["-"] + alias_pool
        
        scatter_x = st.selectbox(
            "X-Achse",
            options=x_options,
            key="scatter_x_select"
        )
        
        scatter_y = st.selectbox(
            "Y-Achse",
            options=y_options,
            key="scatter_y_select"
        )
        
        scatter_color = st.selectbox(
            "Farbcodierung",
            options=color_options,
            key="scatter_color_select"
        )
        
        # Update interne session state Werte (ohne "-" Platzhalter)
        st.session_state["scatter_x"] = scatter_x if scatter_x != "-" else None
        st.session_state["scatter_y"] = scatter_y if scatter_y != "-" else None
        st.session_state["scatter_color"] = scatter_color if scatter_color != "-" else None
        
        st.divider()
        
        # Scatter-Optionen
        point_size = st.number_input(
            "Punktgröße",
            min_value=5.0,
            max_value=200.0,
            step=5.0,
            key="scatter_point_size"
        )
        
        edge_width = st.number_input(
            "Konturbreite",
            min_value=0.0,
            max_value=5.0,
            step=0.1,
            key="scatter_edge_width"
        )
        
        st.divider()
        
        # Einheiten
        x_unit = st.text_input(
            "X-Einheit",
            key="scatter_x_unit"
        )
        
        y_unit = st.text_input(
            "Y-Einheit",
            key="scatter_y_unit"
        )
        
        # Farblegende nur anzeigen, wenn Farbcodierung ausgewählt
        color_label = None
        if scatter_color and scatter_color != "-":
            # Default-Label auf Spaltennamen setzen, falls leer
            if not st.session_state.get("scatter_color_label"):
                st.session_state["scatter_color_label"] = scatter_color
            color_label = st.text_input(
                "Farblegende",
                key="scatter_color_label"
            )
    
    with main_col:
        x_col = st.session_state.get("scatter_x")
        y_col = st.session_state.get("scatter_y")
        
        if not x_col or not y_col:
            st.info("Bitte wählen Sie X- und Y-Komponente aus.")
            return
        
        combined = processed.combined_frame
        
        if x_col not in combined.columns or y_col not in combined.columns:
            st.warning("Ausgewählte Spalten nicht in den Daten gefunden.")
            return
        
        # Sampling für große Daten
        if len(combined) > MAX_PLOT_ROWS:
            combined = combined.sample(n=MAX_PLOT_ROWS, random_state=42)
            st.info(f"Großer Datensatz: Gesampelt auf {MAX_PLOT_ROWS:,} Zeilen.")
        
        color_col = st.session_state.get("scatter_color")
        scatter_df = combined[[x_col, y_col]].copy()
        if color_col and color_col in combined.columns:
            scatter_df[color_col] = combined[color_col]
        
        fig = plot_scatter(
            scatter_df,
            x_col=x_col,
            y_col=y_col,
            color_col=color_col if color_col and color_col in scatter_df.columns else None,
            figsize=_figure_size(options),
            axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
            axis_title_fontsize=options.get("axis_title_fontsize", PLOT_DEFAULTS.axis_title_fontsize),
            point_size=point_size,
            edge_width=edge_width,
            x_unit=x_unit or None,
            y_unit=y_unit or None,
            color_label=color_label or None,
        )
        
        if fig is None:
            st.warning("Keine gültigen Datenpunkte gefunden.")
            return
        
        st.pyplot(fig, width="stretch")
        
        if options.get("export_trigger") and options.get("export_format"):
            export_plots(
                [("Scatter Plot", fig)],
                options.get("export_filename", "export"),
                options.get("export_format"),
            )
        import matplotlib.pyplot as plt
        plt.close(fig)


def _figure_size(options: dict) -> Tuple[float, float]:
    """Berechnet die Figurengröße aus den Optionen (mm -> Zoll)."""
    width_mm = float(options.get("plot_width", PLOT_DEFAULTS.width))
    height_mm = float(options.get("plot_height", PLOT_DEFAULTS.height))
    return (width_mm / 25.4, height_mm / 25.4)

