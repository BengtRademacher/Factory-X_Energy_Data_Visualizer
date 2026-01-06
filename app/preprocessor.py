"""Data preprocessing utilities for harmonizing components and time ranges."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd

from app.data_manager import ProcessedData


TimeRange = Tuple[float | None, float | None]


@dataclass(slots=True)
class PreprocessConfig:
    component_aliases: Dict[str, str]
    time_range: TimeRange | None = None
    time_column: str | None = None


@dataclass(slots=True)
class PreprocessedResult:
    combined_frame: pd.DataFrame
    frames_by_file: Dict[str, pd.DataFrame]
    file_boundaries: list[tuple[str, pd.Timedelta]]
    component_aliases: Dict[str, str]
    applied_time_range: TimeRange | None
    time_column: str | None

    @property
    def has_data(self) -> bool:
        return self.combined_frame is not None and not self.combined_frame.empty

    @property
    def available_components(self) -> list[str]:
        if self.combined_frame is None or self.combined_frame.empty:
            return []
        cols = [c for c in self.combined_frame.columns if c != "elapsedTime"]
        return sorted(cols)


class DataPreprocessor:
    """Prepares data for plotting by applying mappings and global filters."""

    def run(self, processed: ProcessedData, config: PreprocessConfig) -> PreprocessedResult:
        if not processed.has_data:
            return PreprocessedResult(
                combined_frame=processed.combined_frame,
                frames_by_file=processed.frames_by_file,
                file_boundaries=processed.file_boundaries,
                component_aliases=config.component_aliases,
                applied_time_range=config.time_range,
                time_column=config.time_column,
            )

        component_aliases = config.component_aliases or {}
        combined = processed.combined_frame.copy()
        frames_by_file = {name: df.copy() for name, df in processed.frames_by_file.items()}

        combined = self._apply_component_mapping(combined, component_aliases)
        frames_by_file = {
            name: self._apply_component_mapping(df, component_aliases)
            for name, df in frames_by_file.items()
        }

        effective_time_column = None
        use_index = False
        if config.time_column == "__index__":
            use_index = True
        elif config.time_column:
            effective_time_column = component_aliases.get(config.time_column, config.time_column)

        combined = self._ensure_elapsed_time(combined, effective_time_column, use_index=use_index, set_index=False)
        frames_by_file = {
            name: self._ensure_elapsed_time(df, effective_time_column, use_index=use_index, set_index=True)
            for name, df in frames_by_file.items()
        }

        if config.time_range:
            combined = self._apply_time_range_combined(combined, config.time_range)
            frames_by_file = {
                name: self._apply_time_range_per_file(df, config.time_range)
                for name, df in frames_by_file.items()
            }

        return PreprocessedResult(
            combined_frame=combined,
            frames_by_file=frames_by_file,
            file_boundaries=processed.file_boundaries,
            component_aliases=component_aliases,
            applied_time_range=config.time_range,
            time_column=effective_time_column if not use_index else "__index__",
        )

    @staticmethod
    def _apply_component_mapping(df: pd.DataFrame, aliases: Dict[str, str]) -> pd.DataFrame:
        if not aliases:
            return df

        rename_map = {col: aliases[col] for col in df.columns if col in aliases}
        if rename_map:
            df = df.rename(columns=rename_map)

        if df.columns.duplicated().any():
            df = DataPreprocessor._collapse_duplicate_columns(df)

        return df

    @staticmethod
    def _collapse_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
        collapsed = {}
        for col in dict.fromkeys(df.columns):
            subset = df.loc[:, df.columns == col]
            if subset.shape[1] == 1:
                collapsed[col] = subset.iloc[:, 0]
                continue

            numeric_mask = subset.dtypes.apply(pd.api.types.is_numeric_dtype)
            if bool(numeric_mask.all()):
                collapsed[col] = subset.sum(axis=1)
                continue

            # Non-numeric: ffill, then fallback to mean if convertible, else mode/bfill
            fallback_series = subset.ffill(axis=1).iloc[:, -1].copy()
            nan_count = fallback_series.isna().sum()
            if nan_count > 0:
                # Assuming st.warning is available, otherwise this line will cause an error
                # from streamlit import warning
                # warning(f"Bei Duplikat '{col}': {nan_count} NaNs nach ffill. Fallback zu mean/mode/bfill.")
                print(f"Bei Duplikat '{col}': {nan_count} NaNs nach ffill. Fallback zu mean/mode/bfill.")
                # Try mean fallback if numeric convertible
                try:
                    mean_fallback = pd.to_numeric(fallback_series, errors='coerce').fillna(fallback_series.mean())
                    fallback_series = mean_fallback
                except:
                    mode_val = subset.mode(axis=1).iloc[:, 0] if not subset.mode(axis=1).empty else pd.Series(np.nan, index=subset.index)
                    fallback_series = fallback_series.fillna(mode_val).fillna(method="bfill")
            collapsed[col] = fallback_series

        return pd.DataFrame(collapsed, index=df.index)

    @staticmethod
    def _series_to_timedelta(series: pd.Series) -> pd.Series | None:
        if series.empty:
            return None

        if pd.api.types.is_timedelta64_dtype(series):
            return series

        if pd.api.types.is_datetime64_any_dtype(series):
            base = series.iloc[0]
            return (series - base).astype("timedelta64[ns]")

        numeric = pd.to_numeric(series, errors="coerce")
        if numeric.notna().sum() >= max(1, int(0.6 * len(series))):
            numeric = numeric.ffill().bfill()
            return pd.to_timedelta(numeric, unit="s")

        parsed = pd.to_datetime(series, errors="coerce")
        nan_count = parsed.isna().sum()
        if nan_count > 0:
            # from streamlit import warning
            # warning(f"Bei Zeitkonvertierung: {nan_count} ungültige Strings zu NaT konvertiert.")
            print(f"Bei Zeitkonvertierung: {nan_count} ungültige Strings zu NaT konvertiert.")
        if parsed.notna().any():
            parsed = parsed.ffill().bfill()
            base = parsed.iloc[0]
            return (parsed - base).astype("timedelta64[ns]")

        return None

    @staticmethod
    def _ensure_elapsed_time(df: pd.DataFrame, time_column: str | None, *, use_index: bool, set_index: bool) -> pd.DataFrame:
        if df is None or df.empty:
            return df

        df = df.copy()
        elapsed = None

        if use_index:
            if isinstance(df.index, pd.TimedeltaIndex):
                elapsed = df.index
            else:
                idx_numeric = pd.Series(df.index).reset_index(drop=True)
                elapsed = DataPreprocessor._series_to_timedelta(idx_numeric)
        elif time_column and time_column in df.columns:
            series = df[time_column].ffill().bfill()
            elapsed = DataPreprocessor._series_to_timedelta(series)
        elif "elapsedTime" in df.columns:
            series = df["elapsedTime"].ffill().bfill()
            elapsed = DataPreprocessor._series_to_timedelta(series)

        if elapsed is None:
            elapsed = pd.to_timedelta(np.arange(len(df)), unit="s")

        if "elapsedTime" in df.columns:
            df["elapsedTime"] = elapsed
        else:
            df.insert(len(df.columns), "elapsedTime", elapsed)

        if set_index:
            df = df.set_index("elapsedTime", drop=False)

        return df

    @staticmethod
    def _apply_time_range_combined(df: pd.DataFrame, time_range: TimeRange) -> pd.DataFrame:
        if "elapsedTime" not in df.columns:
            return df

        # Handle NaT values explicitly
        df = df.dropna(subset=["elapsedTime"])
        if df.empty:
            # Assuming st.warning is available, otherwise this line will cause an error
            # from streamlit import warning
            # warning("Alle Zeitwerte sind NaT oder ungültig nach Filterung.")
            print("Alle Zeitwerte sind NaT oder ungültig nach Filterung.")
            return df

        start, end = DataPreprocessor._normalize_time_range(time_range)
        mask = pd.Series(True, index=df.index)
        elapsed_seconds = df["elapsedTime"].dt.total_seconds()

        if start is not None:
            mask &= elapsed_seconds >= start
        if end is not None:
            mask &= elapsed_seconds <= end

        return df.loc[mask]

    @staticmethod
    def _apply_time_range_per_file(df: pd.DataFrame, time_range: TimeRange) -> pd.DataFrame:
        if df.empty:
            return df

        # Handle NaT values
        df = df.dropna(subset=["elapsedTime"])
        if df.empty:
            # Assuming st.warning is available, otherwise this line will cause an error
            # from streamlit import warning
            # warning("Alle Zeitwerte sind NaT oder ungültig in dieser Datei.")
            print("Alle Zeitwerte sind NaT oder ungültig in dieser Datei.")
            return df

        start, end = DataPreprocessor._normalize_time_range(time_range)
        index = df.index
        if isinstance(index, pd.TimedeltaIndex):
            start_delta = pd.to_timedelta(start, unit="s") if start is not None else None
            end_delta = pd.to_timedelta(end, unit="s") if end is not None else None
            mask = pd.Series(True, index=df.index)
            if start_delta is not None:
                mask &= index >= start_delta
            if end_delta is not None:
                mask &= index <= end_delta
            return df.loc[mask]

        if "elapsedTime" not in df.columns:
            return df

        elapsed_seconds = df["elapsedTime"].dt.total_seconds()
        mask = pd.Series(True, index=df.index)
        if start is not None:
            mask &= elapsed_seconds >= start
        if end is not None:
            mask &= elapsed_seconds <= end
        return df.loc[mask]

    @staticmethod
    def _normalize_time_range(time_range: TimeRange) -> TimeRange:
        start, end = time_range
        start = float(start) if start is not None else None
        end = float(end) if end is not None else None
        if start is not None and end is not None and start > end:
            start, end = end, start
        return start, end

