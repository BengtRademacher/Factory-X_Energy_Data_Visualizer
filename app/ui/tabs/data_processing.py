"""Data Processing tab for the Factory-X plotting app."""

from __future__ import annotations

from typing import List, Tuple

import pandas as pd
import streamlit as st

from app.config import DEFAULT_COLORS, HISTOGRAM_DEFAULTS, MAX_PREVIEW_ROWS, MAX_SUMMARY_ROWS, PLOT_DEFAULTS
from app.plotting import plot_histogram
from app.ui.components import (
    get_valid_multiselect_state,
    get_valid_selectbox_state,
    render_panel_header,
)
from app.ui.tab_utils import (
    ensure_has_data,
    figure_size_from_options,
    finalize_matplotlib_figures,
    render_matplotlib_figure,
    sample_distribution_frame,
    sample_time_ordered_frame,
)
from app.x_axis import resolve_frame_x_axis


def render(processed, options: dict) -> None:
    """Render the Data Processing tab."""
    if not ensure_has_data(processed, "Please upload files to view and edit data."):
        return

    main_col, custom_col = st.columns([4, 1])

    with custom_col:
        file_names = list(processed.frames_by_file.keys())
        if not file_names:
            st.info("No files are available.")
            return

        default_file = file_names[0]
        current_file = get_valid_selectbox_state("data_selected_file", file_names, default_file)
        columns_available = processed.available_columns

        with st.container(border=True):
            render_panel_header(
                "Analysis Focus",
                "Choose the source file for the preview and decide which columns should receive descriptive summaries.",
                eyebrow="Controls",
                metrics=[
                    ("Files", len(file_names)),
                    ("Summary columns", len(get_valid_multiselect_state("data_summary_columns", columns_available))),
                ],
            )

            selected_file = st.selectbox(
                "File",
                file_names,
                index=file_names.index(current_file),
                key="data_selected_file",
            )

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
        preview_context = _prepare_preview_context(frame, selected_file, options)
        _render_preview(preview_context, selected_file)

        st.divider()

        _render_quick_plot(preview_context, selected_file, options)

        st.divider()

        _render_summary(processed.combined_frame, selected_cols, options)


def _prepare_preview_context(frame: pd.DataFrame, selected_file: str, options: dict) -> dict:
    """Prepare the shared preview context for preview and quick-plot sections."""
    if len(frame) > MAX_PREVIEW_ROWS:
        frame_sample = sample_time_ordered_frame(frame, MAX_PREVIEW_ROWS)
        sample_note = f"Large file detected. Preview sampled to {MAX_PREVIEW_ROWS:,} rows."
    else:
        frame_sample = frame
        sample_note = "Full file shown in the preview."

    preview = frame_sample.drop(columns=["elapsedTime"], errors="ignore").copy()
    time_values = frame_sample.index.total_seconds() if isinstance(frame_sample.index, pd.TimedeltaIndex) else frame_sample.index
    preview.insert(0, "elapsedTime", time_values)
    preview_display = preview.reset_index(drop=True).head(min(len(preview), 500))

    x_source_column = options.get("x_source_column")
    plot_candidates = [
        col
        for col in preview_display.columns
        if col != "elapsedTime" and pd.api.types.is_numeric_dtype(preview_display[col])
    ]
    if x_source_column in plot_candidates:
        plot_candidates = [col for col in plot_candidates if col != x_source_column]

    x_resolution = None
    if x_source_column and plot_candidates:
        x_resolution = resolve_frame_x_axis(frame_sample.reset_index(drop=True), x_source_column, file_name=selected_file)

    return {
        "frame": frame,
        "frame_sample": frame_sample,
        "preview": preview,
        "preview_display": preview_display,
        "sample_note": sample_note,
        "preview_rows": len(preview_display),
        "x_source_column": x_source_column,
        "plot_candidates": plot_candidates,
        "x_resolution": x_resolution,
        "csv_export": preview.reset_index(drop=True).to_csv(index=False).encode("utf-8"),
    }


def _render_preview(context: dict, selected_file: str) -> None:
    """Render the preview section."""
    preview_display = context["preview_display"]
    frame = context["frame"]

    with st.container(border=True):
        render_panel_header(
            "Preview",
            "Inspect the selected file before building plots or summary statistics.",
            eyebrow="Step 1",
            metrics=[
                ("File", selected_file),
                ("Rows", _format_count(len(frame))),
                ("Columns", preview_display.shape[1]),
                ("Numeric", _count_numeric_columns(preview_display)),
                ("Preview", _format_count(context["preview_rows"])),
            ],
        )
        st.markdown(
            f'<p class="fx-inline-note">{context["sample_note"]}</p>',
            unsafe_allow_html=True,
        )
        st.dataframe(preview_display, width="stretch")

        st.download_button(
            "Download CSV",
            data=context["csv_export"],
            file_name=f"{selected_file}_preprocessed.csv",
            mime="text/csv",
            key=f"download_csv_{selected_file}",
            icon=":material/download:",
        )


def _render_quick_plot(context: dict, selected_file: str, options: dict) -> None:
    """Render the quick-plot section."""
    preview_display = context["preview_display"]
    x_source_column = context["x_source_column"]
    plot_candidates = context["plot_candidates"]
    x_resolution = context["x_resolution"]

    with st.container(border=True):
        render_panel_header(
            "Quick Plot",
            "Use the current preview selection to validate trends before switching to a dedicated chart tab.",
            eyebrow="Step 2",
            metrics=[
                ("X source", x_source_column or "Not set"),
                ("Available series", len(plot_candidates)),
                ("Rows plotted", _format_count(len(preview_display))),
            ],
        )

        if not x_source_column:
            st.info("The quick plot becomes available once an X source is selected in the sidebar.")
            return

        if not plot_candidates:
            st.info("No numeric columns are available for a quick preview chart.")
            return

        if x_resolution and x_resolution.error:
            st.warning(x_resolution.error)
            return

        preview_key = f"preview_plot_columns_{selected_file}"
        selected_columns = st.multiselect(
            "Columns for Quick Plot",
            options=plot_candidates,
            default=get_valid_multiselect_state(preview_key, plot_candidates),
            key=preview_key,
        )
        if not selected_columns:
            st.info("Select one or more numeric columns to draw a quick line preview.")
            return

        chart_df = preview_display[selected_columns].copy()
        if x_resolution is not None:
            chart_df.index = x_resolution.values.iloc[: len(chart_df)]
        st.line_chart(chart_df, height=260, width="stretch")


def _render_summary(combined_frame: pd.DataFrame, selected_cols: list[str], options: dict) -> None:
    """Render the data summary."""
    df_sum = combined_frame.copy()
    used_sample = False
    if len(df_sum) > MAX_SUMMARY_ROWS:
        df_sum = sample_distribution_frame(df_sum, MAX_SUMMARY_ROWS).sort_index()
        used_sample = True

    numeric_selected = sum(
        1 for column in selected_cols
        if column in df_sum.columns and pd.to_numeric(df_sum[column], errors="coerce").notna().any()
    )

    with st.container(border=True):
        render_panel_header(
            "Summary",
            "Review descriptive statistics per selected column. Each block stays self-contained so results are easier to scan and compare.",
            eyebrow="Step 3",
            metrics=[
                ("Selected columns", len(selected_cols)),
                ("Rows analyzed", _format_count(len(df_sum))),
                ("Numeric", numeric_selected),
                ("Sampling", "Sampled" if used_sample else "Full data"),
            ],
        )

        if used_sample:
            st.warning(f"Dataset is large ({len(combined_frame):,} rows). Using a sample instead.")

        if not selected_cols:
            st.info("Select one or more columns in the options panel to generate summaries.")
            return

    plots_to_export: List[Tuple[str, object]] = []

    for col in selected_cols:
        if col not in df_sum.columns:
            continue

        series = df_sum[col]
        numeric_series = pd.to_numeric(series, errors="coerce")

        if numeric_series.notna().any():
            with st.container(border=True):
                render_panel_header(
                    col,
                    "Numeric column summary with descriptive statistics and a compact distribution view.",
                    eyebrow="Numeric column",
                    metrics=_build_numeric_metrics(numeric_series),
                )
                desc = numeric_series.describe()
                desc_df = desc.to_frame(name="Value")
                desc_df["Value"] = desc_df["Value"].apply(lambda value: f"{value:.4f}" if pd.notna(value) else "N/A")
                st.table(desc_df)

            fig_hist = plot_histogram(
                series=numeric_series,
                title=f"Histogram - {col}",
                figsize=figure_size_from_options(options),
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
                render_matplotlib_figure(fig_hist)
                plots_to_export.append((f"Histogram - {col}", fig_hist))
        else:
            with st.container(border=True):
                render_panel_header(
                    col,
                    "Categorical column summary with occurrence-oriented overview statistics.",
                    eyebrow="Categorical column",
                    metrics=_build_categorical_metrics(series),
                )
                desc = series.astype(str).describe()
                desc_df = desc.to_frame(name="Value")
                desc_df["Value"] = desc_df["Value"].astype(str)
                st.table(desc_df)

    finalize_matplotlib_figures(plots_to_export, options)


def _format_count(value: int) -> str:
    """Format integer values for KPI display."""
    return f"{value:,}"


def _format_metric(value: float) -> str:
    """Format numeric KPI values compactly."""
    if pd.isna(value):
        return "N/A"
    absolute = abs(float(value))
    if absolute >= 1000:
        return f"{value:,.0f}"
    if absolute >= 10:
        return f"{value:.1f}"
    return f"{value:.2f}"


def _count_numeric_columns(frame: pd.DataFrame) -> int:
    """Count numeric columns inside a preview frame."""
    return sum(pd.api.types.is_numeric_dtype(frame[column]) for column in frame.columns)


def _build_numeric_metrics(series: pd.Series) -> list[tuple[str, object]]:
    """Build KPI chips for numeric summary cards."""
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return []

    return [
        ("Values", _format_count(len(clean))),
        ("Mean", _format_metric(clean.mean())),
        ("Std", _format_metric(clean.std(ddof=0))),
        ("Min / Max", f"{_format_metric(clean.min())} / {_format_metric(clean.max())}"),
    ]


def _build_categorical_metrics(series: pd.Series) -> list[tuple[str, object]]:
    """Build KPI chips for categorical summary cards."""
    clean = series.dropna().astype(str)
    if clean.empty:
        return [("Values", "0")]

    top_value = clean.mode().iloc[0] if not clean.mode().empty else clean.iloc[0]
    return [
        ("Values", _format_count(len(clean))),
        ("Unique", clean.nunique()),
        ("Top", top_value),
    ]
