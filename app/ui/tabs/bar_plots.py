"""Säulendiagramm Tab für die Factory-X Plotting-App."""

import streamlit as st
from typing import Tuple

from app.config import DEFAULT_COLORS, PLOT_DEFAULTS, BAR_DEFAULTS
from app.plotting import plot_bar, plot_bar_evp
from app.export import export_plots
from app.ui.components import render_color_selector


def render(processed, options: dict) -> None:
    """Rendert den Säulendiagramm Tab."""
    
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
            default=st.session_state.get("bar_selected_components", []),
            key="bar_selected_components"
        )
        
        # Farben
        colors = _render_color_picker(components, "bar")
        
        st.divider()
        
        # Säulen-Optionen
        aggregation_options = ["Mittelwert", "Summe"]
        current_mode = st.session_state.get("bar_mode", BAR_DEFAULTS.mode)
        mode_index = aggregation_options.index(current_mode) if current_mode in aggregation_options else 0
        mode = st.selectbox(
            "Aggregation",
            aggregation_options,
            index=mode_index,
            key="bar_mode"
        )
        
        bar_width = st.slider(
            "Säulenbreite",
            0.05, 0.60,
            step=0.01,
            key="bar_width"
        )
        
        label_rotation = st.slider(
            "Beschriftungswinkel",
            0, 90,
            step=5,
            key="bar_label_rotation"
        )
        
        hide_x_labels = st.checkbox(
            "X-Beschriftung ausblenden",
            key="bar_hide_x_labels"
        )
        
        st.divider()
        
        # Vergleichssäule
        show_compare = st.checkbox("Vergleichssäule", key="bar_show_compare")
        compare_components = []
        if show_compare:
            compare_components = st.multiselect(
                "Vergleichs-Komponenten",
                options=alias_pool,
                key="bar_compare_components"
            )
    
    with main_col:
        plots_to_export = []
        
        if components:
            fig = plot_bar(
                df_by_file=processed.frames_by_file,
                components=components,
                title="Säulendiagramm",
                mode=mode,
                label_rotation=label_rotation,
                colors=colors,
                hide_x_labels=hide_x_labels,
                figsize=_figure_size(options),
                line_width=options.get("line_width", PLOT_DEFAULTS.line_width),
                axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
                axis_title_fontsize=options.get("axis_title_fontsize", PLOT_DEFAULTS.axis_title_fontsize),
                ylim=None,
                y_unit=options.get("y_unit", PLOT_DEFAULTS.y_unit),
                bar_width=bar_width,
                y_tick_step=options.get("y_tick_step"),
                y_label=options.get("y_axis_label", PLOT_DEFAULTS.y_label),
                x_label=options.get("x_axis_label", ""),
            )
            if fig:
                st.pyplot(fig, width="stretch")
                plots_to_export.append(("Säulendiagramm", fig))
                import matplotlib.pyplot as plt
                plt.close(fig)
        else:
            st.info("Bitte wählen Sie mindestens eine Komponente aus.")
        
        # Vergleichsdiagramm
        if show_compare and components and compare_components:
            st.divider()
            st.subheader("Vergleich")
            
            fig_compare = plot_bar_evp(
                df_by_file=processed.frames_by_file,
                elec_components=components,
                pneu_components=compare_components,
                title="Vergleich: Gruppe 1 vs. Gruppe 2",
                mode=mode,
                label_rotation=label_rotation,
                colors=colors,
                hide_x_labels=hide_x_labels,
                figsize=_figure_size(options),
                line_width=options.get("line_width", PLOT_DEFAULTS.line_width),
                axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
                axis_title_fontsize=options.get("axis_title_fontsize", PLOT_DEFAULTS.axis_title_fontsize),
                ylim=None,
                y_unit=options.get("y_unit", PLOT_DEFAULTS.y_unit),
                bar_width=bar_width,
                y_tick_step=options.get("y_tick_step"),
                y_label=options.get("y_axis_label", PLOT_DEFAULTS.y_label),
                x_label=options.get("x_axis_label", ""),
            )
            if fig_compare:
                st.pyplot(fig_compare, width="stretch")
                plots_to_export.append(("Vergleichsdiagramm", fig_compare))
                import matplotlib.pyplot as plt
                plt.close(fig_compare)
        
        if options.get("export_trigger") and options.get("export_format") and plots_to_export:
            export_plots(
                plots_to_export,
                options.get("export_filename", "export"),
                options.get("export_format"),
            )


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

