"""Helpers for resolving a manually selected X axis."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.data_manager import ProcessedData

X_SOURCE_PLACEHOLDER = "(please select)"


@dataclass(slots=True)
class XAxisResolution:
    values: pd.Series
    file_boundaries: list[tuple[str, float]]
    max_value: float | None
    error: str | None = None


def resolve_processed_x_axis(processed: ProcessedData, column: str | None) -> XAxisResolution:
    """Resolve one shared X axis across all files."""
    if not column:
        return XAxisResolution(
            values=pd.Series(dtype=float),
            file_boundaries=[],
            max_value=None,
            error="Please select an X source.",
        )

    if not processed.has_data or not processed.frames_by_file:
        return XAxisResolution(
            values=pd.Series(dtype=float),
            file_boundaries=[],
            max_value=None,
            error="No data is available for the X axis.",
        )

    parts: list[pd.Series] = []
    boundaries: list[tuple[str, float]] = []
    offset = 0.0

    for file_name, frame in processed.frames_by_file.items():
        resolved = resolve_frame_x_axis(frame, column, file_name=file_name)
        if resolved.error:
            return XAxisResolution(
                values=pd.Series(dtype=float),
                file_boundaries=[],
                max_value=None,
                error=resolved.error,
            )

        file_values = resolved.values.reset_index(drop=True)
        normalized = file_values - float(file_values.iloc[0])
        shifted = normalized + offset
        boundaries.append((file_name, float(shifted.iloc[0])))
        parts.append(shifted)
        offset = float(shifted.iloc[-1])

    combined = pd.concat(parts, ignore_index=True) if parts else pd.Series(dtype=float)
    max_value = float(combined.max()) if not combined.empty else None
    return XAxisResolution(values=combined, file_boundaries=boundaries, max_value=max_value, error=None)


def resolve_frame_x_axis(frame: pd.DataFrame, column: str | None, *, file_name: str | None = None) -> XAxisResolution:
    """Resolve the X axis for a single file."""
    if not column:
        return XAxisResolution(
            values=pd.Series(dtype=float),
            file_boundaries=[],
            max_value=None,
            error="Please select an X source.",
        )

    if column in frame.columns:
        series = frame[column]
    elif frame.index.name == column:
        series = pd.Series(frame.index, name=column)
    else:
        suffix = f" in '{file_name}'" if file_name else ""
        return XAxisResolution(
            values=pd.Series(dtype=float),
            file_boundaries=[],
            max_value=None,
            error=f"The X source '{column}' is missing{suffix}.",
        )

    resolved = _coerce_x_axis_series(series)
    if resolved is None:
        suffix = f" in '{file_name}'" if file_name else ""
        return XAxisResolution(
            values=pd.Series(dtype=float),
            file_boundaries=[],
            max_value=None,
            error=(
                f"The X source '{column}' is not usable{suffix}. "
                "Numeric, datetime, or timedelta columns without invalid values are supported."
            ),
        )

    return XAxisResolution(
        values=resolved.reset_index(drop=True),
        file_boundaries=[],
        max_value=float(resolved.max()) if not resolved.empty else None,
        error=None,
    )


def _coerce_x_axis_series(series: pd.Series) -> pd.Series | None:
    """Convert one series into numeric X-axis values."""
    if series.empty or series.isna().any():
        return None

    if pd.api.types.is_timedelta64_dtype(series):
        return series.dt.total_seconds().astype(float)

    if pd.api.types.is_datetime64_any_dtype(series):
        parsed = series
        if getattr(parsed.dt, "tz", None) is not None:
            parsed = parsed.dt.tz_convert(None)
        base = parsed.iloc[0]
        return (parsed - base).dt.total_seconds().astype(float)

    if pd.api.types.is_numeric_dtype(series):
        numeric = pd.to_numeric(series, errors="coerce")
        return numeric.astype(float) if numeric.notna().all() else None

    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().all():
        return numeric.astype(float)

    string_values = series.astype(str)
    if string_values.str.contains(r"\d", regex=True).all():
        parsed_datetime = pd.to_datetime(series, errors="coerce", utc=True)
        if parsed_datetime.notna().all():
            parsed_datetime = parsed_datetime.dt.tz_convert(None)
            base = parsed_datetime.iloc[0]
            return (parsed_datetime - base).dt.total_seconds().astype(float)

        parsed_timedelta = pd.to_timedelta(series, errors="coerce")
        if parsed_timedelta.notna().all():
            return parsed_timedelta.dt.total_seconds().astype(float)

    return None
