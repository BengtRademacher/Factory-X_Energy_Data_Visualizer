"""Sankey Diagramm Tab für die Factory-X Plotting-App."""

import streamlit as st
from typing import Tuple

from app.config import DEFAULT_COLORS, PLOT_DEFAULTS, SANKEY_DEFAULTS
from app.plotting import plot_sankey_energy_flow
from app.export import export_plots
from app.ui.components import render_color_selector


def render(processed, options: dict) -> None:
    """Rendert den Sankey Tab."""
    
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
        
        # Titel und Modus
        title = st.text_input(
            "Titel",
            key="sankey_title"
        )
        
        # Modus-Auswahl mit korrektem Index
        mode_options = ["Mittelwert", "Summe"]
        current_mode = st.session_state.get("sankey_mode", SANKEY_DEFAULTS.mode)
        mode_index = mode_options.index(current_mode) if current_mode in mode_options else 0
        mode = st.selectbox(
            "Modus",
            mode_options,
            index=mode_index,
            key="sankey_mode"
        )
        
        unit = st.text_input(
            "Einheit",
            key="sankey_unit"
        )
        
        st.divider()
        
        # Komponentenauswahl
        elektrisch = st.multiselect(
            "Elektrische Komponenten",
            options=alias_pool,
            default=st.session_state.get("sankey_selected_elektrisch", []),
            key="sankey_selected_elektrisch"
        )
        
        pneumatisch = st.multiselect(
            "Pneumatische Komponenten",
            options=alias_pool,
            default=st.session_state.get("sankey_selected_pneumatisch", []),
            key="sankey_selected_pneumatisch"
        )
        
        # Produktive Komponenten
        all_selected = elektrisch + pneumatisch
        productive = st.multiselect(
            "Produktive Komponenten",
            options=all_selected,
            default=[c for c in st.session_state.get("sankey_productive_vars", []) if c in all_selected],
            key="sankey_productive_vars"
        )
        
        st.divider()
        
        # Farben
        colors = _render_sankey_colors(elektrisch, pneumatisch)
    
    with main_col:
        if not elektrisch and not pneumatisch:
            st.info("Bitte wählen Sie mindestens eine Komponente aus.")
            return
        
        fig = plot_sankey_energy_flow(
            df=processed.combined_frame,
            selected_elektrisch=elektrisch,
            selected_pneumatisch=pneumatisch,
            productive_vars=productive,
            mode=mode,
            figsize=_figure_size(options),
            axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
            title=title,
            colors=colors,
            unit=unit,
        )
        
        if fig is None:
            st.info("Keine Daten für das Sankey-Diagramm verfügbar.")
            return
        
        st.plotly_chart(fig, width="stretch")
        
        if options.get("export_trigger") and options.get("export_format"):
            export_plots(
                [(title, fig)],
                options.get("export_filename", "export"),
                options.get("export_format"),
            )


def _render_sankey_colors(elektrisch: list, pneumatisch: list) -> dict:
    """Rendert Farbauswahl für Sankey-Komponenten."""
    
    colors = st.session_state.get("sankey_colors", {}).copy()
    
    with st.expander("🎨 Farben", expanded=False):
        colors["Elektrisch"] = render_color_selector(
            "Elektrisch (Gruppe)",
            "sankey_color_elektrisch",
            DEFAULT_COLORS[0]
        )
        
        colors["Pneumatisch"] = render_color_selector(
            "Pneumatisch (Gruppe)",
            "sankey_color_pneumatisch",
            DEFAULT_COLORS[3]
        )
        
        all_vars = elektrisch + pneumatisch
        for i, var in enumerate(all_vars):
            key = f"sankey_color_{var}"
            default = DEFAULT_COLORS[i % len(DEFAULT_COLORS)]
            colors[var] = render_color_selector(f"{var}", key, default)
    
    st.session_state["sankey_colors"] = colors
    return colors


def _figure_size(options: dict) -> Tuple[float, float]:
    """Berechnet die Figurengröße aus den Optionen (mm -> Zoll)."""
    width_mm = float(options.get("plot_width", PLOT_DEFAULTS.width))
    height_mm = float(options.get("plot_height", PLOT_DEFAULTS.height))
    return (width_mm / 25.4, height_mm / 25.4)

