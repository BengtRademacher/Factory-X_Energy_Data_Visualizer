"""Data Processing Tab für die Factory-X Plotting-App."""

import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Tuple

from app.config import DEFAULT_COLORS, MAX_PREVIEW_ROWS, PLOT_DEFAULTS, HISTOGRAM_DEFAULTS
from app.plotting import plot_histogram
from app.export import export_plots


def render(processed, options: dict) -> None:
    """Rendert den Data Processing Tab."""
    
    if not processed.has_data:
        st.info("Bitte laden Sie Dateien hoch, um Daten anzuzeigen und zu bearbeiten.")
        return
    
    # Zwei-Spalten-Layout: Hauptbereich | Customization
    main_col, custom_col = st.columns([4, 1])
    
    with custom_col:
        st.markdown("### ⚙️ Optionen")
        
        file_names = list(processed.frames_by_file.keys())
        selected_file = st.selectbox(
            "Datei",
            file_names,
            key="data_selected_file"
        )
        
        # Spaltenauswahl für Summary
        columns_available = [c for c in processed.combined_frame.columns if c != "elapsedTime"]
        
        # Default für Summary: Hauptversorgung bevorzugen
        summary_defaults = [c for c in ["Hauptversorgung"] if c in columns_available]
        if not summary_defaults and columns_available:
            summary_defaults = columns_available[:1]
            
        selected_cols = st.multiselect(
            "Spalten für Summary",
            options=columns_available,
            default=summary_defaults,
            key="data_summary_columns"
        )
    
    with main_col:
        if not selected_file:
            return
        
        frame = processed.frames_by_file[selected_file]
        _render_preview(frame, selected_file, options)
        
        st.divider()
        
        _render_summary(processed.combined_frame, selected_cols, options)


def _render_preview(frame: pd.DataFrame, selected_file: str, options: dict) -> None:
    """Rendert die Datenvorschau."""
    
    # Sample für große Dateien
    if len(frame) > MAX_PREVIEW_ROWS:
        frame_sample = frame.sample(n=MAX_PREVIEW_ROWS, random_state=42)
        st.info(f"Datei zu groß ({len(frame):,} Zeilen), Stichprobe von {MAX_PREVIEW_ROWS:,} Zeilen für Vorschau.")
    else:
        frame_sample = frame
    
    preview = frame_sample.drop(columns=["elapsedTime"], errors="ignore").copy()
    if isinstance(frame_sample.index, pd.TimedeltaIndex):
        time_values = frame_sample.index.total_seconds()
    else:
        time_values = frame_sample.index
    preview.insert(0, "elapsedTime", time_values)
    
    with st.container(border=True):
        st.subheader("📋 Datenvorschau")
        
        preview_rows = min(len(preview), 500)
        if len(preview) > preview_rows:
            st.caption(f"Vorschau auf {preview_rows} Zeilen begrenzt.")
        
        preview_display = preview.reset_index(drop=True).head(preview_rows)
        st.dataframe(preview_display, width='stretch')
        
        # Mini-Plot
        plot_candidates = [
            col for col in preview_display.columns
            if col != "elapsedTime" and pd.api.types.is_numeric_dtype(preview_display[col])
        ]
        if plot_candidates:
            # Defaults: Hauptversorgung, Fallback: erste Spalte mit echten Einträgen
            defaults = [c for c in ["Hauptversorgung"] if c in plot_candidates]
            if not defaults:
                for col in plot_candidates:
                    # Prüfe auf "echte Einträge" (nicht nur NaN und nicht nur 0)
                    non_na = preview_display[col].dropna()
                    if not non_na.empty and not (non_na == 0).all():
                        defaults = [col]
                        break
                if not defaults:
                    defaults = [plot_candidates[0]]

            selected_columns = st.multiselect(
                "Spalten für Quick-Plot",
                options=plot_candidates,
                default=defaults,
                key=f"preview_plot_columns_{selected_file}",
            )
            if selected_columns:
                chart_df = preview_display.set_index("elapsedTime")[selected_columns]
                st.line_chart(chart_df, height=220, width="stretch")
        
        # Download
        csv_export = preview.reset_index(drop=True).to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ CSV herunterladen",
            data=csv_export,
            file_name=f"{selected_file}_preprocessed.csv",
            mime="text/csv",
            key=f"download_csv_{selected_file}",
        )


def _render_summary(combined_frame: pd.DataFrame, selected_cols: list, options: dict) -> None:
    """Rendert die Datenzusammenfassung."""
    
    if not selected_cols:
        return
    
    st.subheader("📊 Zusammenfassung")
    
    df_sum = combined_frame.copy()
    max_rows = 1_000_000
    if len(df_sum) > max_rows:
        st.warning(f"Datensatz ({len(df_sum):,} Zeilen) zu groß, Stichprobe verwendet.")
        df_sum = df_sum.sample(n=max_rows, random_state=42).sort_index()
    
    plots_to_export: List[Tuple[str, object]] = []
    
    for col in selected_cols:
        series = df_sum[col]
        
        st.markdown(f"**{col}**")
        numeric_series = pd.to_numeric(series, errors="coerce")
        
        if numeric_series.notna().any():
            with st.container(border=True):
                desc = numeric_series.describe()
                desc_df = desc.to_frame(name="Wert")
                desc_df["Wert"] = desc_df["Wert"].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "N/A")
                st.table(desc_df)
            
            fig_hist = plot_histogram(
                series=numeric_series,
                title=f"Histogramm – {col}",
                figsize=_figure_size(options),
                axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
                axis_title_fontsize=options.get("axis_title_fontsize", PLOT_DEFAULTS.axis_title_fontsize),
                bins=HISTOGRAM_DEFAULTS.bins,
                line_width=HISTOGRAM_DEFAULTS.line_width,
                color=DEFAULT_COLORS[0],
                x_label=col,
                y_label="Prozent",
                x_unit=options.get("y_unit", PLOT_DEFAULTS.y_unit),
                y_unit="%",
            )
            if fig_hist is not None:
                st.pyplot(fig_hist, width="stretch")
                plots_to_export.append((f"Histogramm – {col}", fig_hist))
        else:
            with st.container(border=True):
                desc = series.astype(str).describe()
                desc_df = desc.to_frame(name="Wert")
                desc_df["Wert"] = desc_df["Wert"].astype(str)
                st.table(desc_df)
    
    if options.get("export_trigger") and options.get("export_format") and plots_to_export:
        export_plots(
            plots_to_export,
            options.get("export_filename", "export"),
            options.get("export_format"),
        )


def _figure_size(options: dict) -> Tuple[float, float]:
    """Berechnet die Figurengröße aus den Optionen (mm -> Zoll)."""
    width_mm = float(options.get("plot_width", PLOT_DEFAULTS.width))
    height_mm = float(options.get("plot_height", PLOT_DEFAULTS.height))
    return (width_mm / 25.4, height_mm / 25.4)
