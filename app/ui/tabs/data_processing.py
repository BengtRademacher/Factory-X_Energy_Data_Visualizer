"""Data Processing tab for the Factory-X plotting app."""

from typing import List, Tuple

import pandas as pd
import streamlit as st

from app.config import DEFAULT_COLORS, HISTOGRAM_DEFAULTS, MAX_PREVIEW_ROWS, PLOT_DEFAULTS
from app.export import export_plots
from app.plotting import plot_histogram
from app.ui.components import get_valid_multiselect_state, get_valid_selectbox_state
from app.x_axis import resolve_frame_x_axis


def render(processed, options: dict) -> None:
    """Render the Data Processing tab."""
    if not processed.has_data:
        st.info("Please upload files to view and edit data.")
        return

    main_col, custom_col = st.columns([4, 1])

    with custom_col:
        st.markdown("### :material/tune: Options")

        file_names = list(processed.frames_by_file.keys())
        if not file_names:
            st.info("No files are available.")
            return

        default_file = file_names[0]
        current_file = get_valid_selectbox_state("data_selected_file", file_names, default_file)
        selected_file = st.selectbox(
            "File",
            file_names,
            index=file_names.index(current_file),
            key="data_selected_file",
        )

        columns_available = options.get("all_available_columns", [])
        selected_cols = st.multiselect(
            "Columns for Summary",
            options=columns_available,
            default=get_valid_multiselect_state("data_summary_columns", columns_available),
            key="data_summary_columns",
        )

    with main_col:
        if not selected_file:
            return

        frame = processed.frames_by_file[selected_file]
        _render_preview(frame, selected_file, options)

        st.divider()

        _render_summary(processed.combined_frame, selected_cols, options)


def _render_preview(frame: pd.DataFrame, selected_file: str, options: dict) -> None:
    """Render the data preview."""
    if len(frame) > MAX_PREVIEW_ROWS:
        frame_sample = frame.sample(n=MAX_PREVIEW_ROWS, random_state=42)
        st.info(f"Large file ({len(frame):,} rows). Showing a sample of {MAX_PREVIEW_ROWS:,} rows in the preview.")
    else:
        frame_sample = frame

    preview = frame_sample.drop(columns=["elapsedTime"], errors="ignore").copy()
    time_values = frame_sample.index.total_seconds() if isinstance(frame_sample.index, pd.TimedeltaIndex) else frame_sample.index
    preview.insert(0, "elapsedTime", time_values)

    with st.container(border=True):
        st.subheader(":material/table_chart: Data Preview")

        preview_rows = min(len(preview), 500)
        if len(preview) > preview_rows:
            st.caption(f"Preview limited to {preview_rows} rows.")

        preview_display = preview.reset_index(drop=True).head(preview_rows)
        st.dataframe(preview_display, width="stretch")

        x_source_column = options.get("x_source_column")
        plot_candidates = [
            col
            for col in preview_display.columns
            if col != "elapsedTime" and pd.api.types.is_numeric_dtype(preview_display[col])
        ]
        if x_source_column in plot_candidates:
            plot_candidates = [col for col in plot_candidates if col != x_source_column]

        if not x_source_column:
            st.info("The quick plot becomes available once an X source is selected in the sidebar.")
        elif plot_candidates:
            x_resolution = resolve_frame_x_axis(frame_sample.reset_index(drop=True), x_source_column, file_name=selected_file)
            if x_resolution.error:
                st.warning(x_resolution.error)
            else:
                preview_key = f"preview_plot_columns_{selected_file}"
                selected_columns = st.multiselect(
                    "Columns for Quick Plot",
                    options=plot_candidates,
                    default=get_valid_multiselect_state(preview_key, plot_candidates),
                    key=preview_key,
                )
                if selected_columns:
                    chart_df = preview_display[selected_columns].copy()
                    chart_df.index = x_resolution.values.iloc[: len(chart_df)]
                    st.line_chart(chart_df, height=220, width="stretch")

        csv_export = preview.reset_index(drop=True).to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV",
            data=csv_export,
            file_name=f"{selected_file}_preprocessed.csv",
            mime="text/csv",
            key=f"download_csv_{selected_file}",
            icon=":material/download:",
        )


def _render_summary(combined_frame: pd.DataFrame, selected_cols: list[str], options: dict) -> None:
    """Render the data summary."""
    if not selected_cols:
        return

    st.subheader(":material/analytics: Summary")

    df_sum = combined_frame.copy()
    max_rows = 1_000_000
    if len(df_sum) > max_rows:
        st.warning(f"Dataset is large ({len(df_sum):,} rows). Using a sample instead.")
        df_sum = df_sum.sample(n=max_rows, random_state=42).sort_index()

    plots_to_export: List[Tuple[str, object]] = []

    for col in selected_cols:
        if col not in df_sum.columns:
            continue

        series = df_sum[col]
        st.markdown(f"**{col}**")
        numeric_series = pd.to_numeric(series, errors="coerce")

        if numeric_series.notna().any():
            with st.container(border=True):
                desc = numeric_series.describe()
                desc_df = desc.to_frame(name="Value")
                desc_df["Value"] = desc_df["Value"].apply(lambda value: f"{value:.4f}" if pd.notna(value) else "N/A")
                st.table(desc_df)

            fig_hist = plot_histogram(
                series=numeric_series,
                title=f"Histogram - {col}",
                figsize=_figure_size(options),
                axis_fontsize=options.get("axis_annotation_fontsize", PLOT_DEFAULTS.axis_fontsize),
                axis_title_fontsize=options.get("axis_title_fontsize", PLOT_DEFAULTS.axis_title_fontsize),
                bins=HISTOGRAM_DEFAULTS.bins,
                line_width=HISTOGRAM_DEFAULTS.line_width,
                color=DEFAULT_COLORS[0],
                x_label=col,
                y_label="Percent",
                x_unit=options.get("y_unit", PLOT_DEFAULTS.y_unit),
                y_unit="%",
            )
            if fig_hist is not None:
                st.pyplot(fig_hist, width="stretch")
                plots_to_export.append((f"Histogram - {col}", fig_hist))
        else:
            with st.container(border=True):
                desc = series.astype(str).describe()
                desc_df = desc.to_frame(name="Value")
                desc_df["Value"] = desc_df["Value"].astype(str)
                st.table(desc_df)

    if options.get("export_trigger") and options.get("export_format") and plots_to_export:
        export_plots(
            plots_to_export,
            options.get("export_filename", "export"),
            options.get("export_format"),
        )


def _figure_size(options: dict) -> Tuple[float, float]:
    """Calculate figure size from sidebar options (mm -> inches)."""
    width_mm = float(options.get("plot_width", PLOT_DEFAULTS.width))
    height_mm = float(options.get("plot_height", PLOT_DEFAULTS.height))
    return (width_mm / 25.4, height_mm / 25.4)
