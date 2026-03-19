"""Data ingestion and preprocessing services for the plotting application."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import streamlit as st
from pandas.errors import EmptyDataError, ParserError


@dataclass(slots=True)
class ProcessedData:
    """Represents the processed outputs for the application."""

    combined_frame: pd.DataFrame
    file_boundaries: List[Tuple[str, pd.Timedelta]]
    frames_by_file: Dict[str, pd.DataFrame]

    @property
    def has_data(self) -> bool:
        return self.combined_frame is not None and not self.combined_frame.empty


class DataManager:
    """Provides high-level data ingestion and transformation utilities."""

    elapsed_column = "elapsedTime"

    def load_files(self, uploaded_files: Sequence) -> ProcessedData:
        """Load all uploaded files and merge them into one processed payload."""
        if not uploaded_files:
            return ProcessedData(pd.DataFrame(), [], {})

        all_frames: List[pd.DataFrame] = []
        file_boundaries: List[Tuple[str, pd.Timedelta]] = []
        frames_by_file: Dict[str, pd.DataFrame] = {}
        offset = pd.Timedelta(seconds=0)

        for uploaded in uploaded_files:
            frame = self._read_file(uploaded)
            if frame is None or frame.empty:
                st.warning(f"File '{uploaded.name}' could not be read.")
                continue

            frame = self.ensure_elapsed_time(frame, uploaded.name)
            if frame.empty:
                st.warning(
                    f"File '{uploaded.name}' does not contain usable time information and will be skipped."
                )
                continue

            frame[self.elapsed_column] = frame[self.elapsed_column] + offset
            frame.set_index(self.elapsed_column, inplace=True)

            file_boundaries.append((uploaded.name, frame.index[0]))
            frames_by_file[uploaded.name] = frame
            all_frames.append(frame.reset_index())

            offset = frame.index[-1]
            if len(frame.index) > 1:
                step = frame.index[1] - frame.index[0]
                if isinstance(step, pd.Timedelta):
                    offset += step

        combined = pd.concat(all_frames, ignore_index=True) if all_frames else pd.DataFrame()
        return ProcessedData(combined, file_boundaries, frames_by_file)

    def ensure_elapsed_time(self, frame: pd.DataFrame, file_name: str | None = None) -> pd.DataFrame:
        """Ensure that the frame contains a normalized elapsed time column."""
        if self.elapsed_column in frame.columns:
            return self._normalize_elapsed_series(frame)

        elapsed = self._from_datetime_columns(frame)
        if elapsed is not None:
            frame[self.elapsed_column] = elapsed
            return self._normalize_elapsed_series(frame)

        elapsed = self._from_numeric_columns(frame)
        if elapsed is not None:
            frame[self.elapsed_column] = elapsed
            return self._normalize_elapsed_series(frame)

        frame[self.elapsed_column] = pd.to_timedelta(np.arange(len(frame)), unit="s")
        st.info(f"Derived time from the row index (1 s step) for '{file_name or 'file'}'.")
        return frame

    def sum_categories(
        self,
        frames_by_file: Dict[str, pd.DataFrame],
        electric_vars: Iterable[str],
        pneumatic_vars: Iterable[str],
    ) -> pd.DataFrame:
        """Aggregate electric and pneumatic component groups per file."""
        if not frames_by_file:
            return pd.DataFrame()

        totals = {"Electric": [], "Pneumatic": []}
        index: Optional[pd.Index] = None

        for frame in frames_by_file.values():
            if index is None:
                index = frame.index

            electric_cols = [col for col in electric_vars if col in frame.columns]
            pneumatic_cols = [col for col in pneumatic_vars if col in frame.columns]

            totals["Electric"].append(frame[electric_cols].sum(axis=1) if electric_cols else 0)
            totals["Pneumatic"].append(frame[pneumatic_cols].sum(axis=1) if pneumatic_cols else 0)

        if index is None:
            return pd.DataFrame()

        electric_sum = sum(totals["Electric"]) if totals["Electric"] else 0
        pneumatic_sum = sum(totals["Pneumatic"]) if totals["Pneumatic"] else 0
        return pd.DataFrame({"Electric": electric_sum, "Pneumatic": pneumatic_sum}, index=index).fillna(0)

    def sum_components(
        self,
        frames_by_file: Dict[str, pd.DataFrame],
        components: Iterable[str],
    ) -> pd.DataFrame:
        """Sum selected components per file into one column each."""
        if not frames_by_file:
            return pd.DataFrame()

        result: Dict[str, pd.Series] = {}
        for file_name, frame in frames_by_file.items():
            selected_cols = [col for col in components if col in frame.columns]
            result[file_name] = frame[selected_cols].sum(axis=1) if selected_cols else pd.Series(0, index=frame.index)

        return pd.DataFrame(result).fillna(0)

    @staticmethod
    def _read_file(uploaded_file) -> Optional[pd.DataFrame]:
        """Read one uploaded CSV or Excel file."""
        name = getattr(uploaded_file, "name", "Unknown file")
        try:
            lowered = name.lower()
            if lowered.endswith(".csv"):
                return pd.read_csv(uploaded_file, sep=None, engine="python")
            return pd.read_excel(uploaded_file)
        except (ParserError, EmptyDataError) as exc:
            st.warning(f"File '{name}' could not be parsed: {exc}. Please check the file format.")
        except ValueError as exc:
            st.warning(f"File '{name}' contains invalid values and was skipped ({exc}).")
        except Exception as exc:
            st.warning(f"An unexpected error occurred while loading '{name}': {exc}.")
        return None

    def _normalize_elapsed_series(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Normalize the elapsed time series to timedeltas starting at zero."""
        series = frame[self.elapsed_column]
        if not pd.api.types.is_timedelta64_dtype(series):
            if pd.api.types.is_numeric_dtype(series):
                frame[self.elapsed_column] = pd.to_timedelta(series, unit="s", errors="coerce")
            else:
                frame[self.elapsed_column] = pd.to_timedelta(series.astype(str), errors="coerce")

        frame.dropna(subset=[self.elapsed_column], inplace=True)
        if frame.empty:
            return frame

        frame[self.elapsed_column] = frame[self.elapsed_column] - frame[self.elapsed_column].iloc[0]
        return frame

    def _from_datetime_columns(self, frame: pd.DataFrame) -> Optional[pd.Series]:
        """Try to derive elapsed time from datetime-like columns."""
        best_parsed: Optional[pd.Series] = None
        best_ratio = 0.0

        for col in frame.columns:
            series = frame[col]
            if pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_datetime64_any_dtype(series):
                continue
            parsed = series if pd.api.types.is_datetime64_any_dtype(series) else pd.to_datetime(
                series,
                errors="coerce",
                utc=True,
            )
            ratio = float(parsed.notna().mean())
            if ratio > best_ratio and ratio >= 0.6:
                best_ratio = ratio
                best_parsed = parsed

        if best_parsed is None:
            return None

        parsed = best_parsed.dropna()
        if parsed.empty:
            return None

        parsed = parsed.dt.tz_convert(None) if getattr(parsed.dt, "tz", None) is not None else parsed
        elapsed = parsed - parsed.iloc[0]
        return pd.to_timedelta(elapsed)

    def _from_numeric_columns(self, frame: pd.DataFrame) -> Optional[pd.Series]:
        """Try to derive elapsed time from numeric columns."""
        numeric_cols = [col for col in frame.columns if pd.api.types.is_numeric_dtype(frame[col])]
        candidates: List[str] = []

        for col in numeric_cols:
            series = pd.to_numeric(frame[col], errors="coerce")
            if series.notna().mean() < 0.9:
                continue

            diffs = series.diff().dropna()
            if len(diffs) == 0:
                continue

            if float((diffs > 0).mean()) >= 0.9:
                candidates.append(col)

        if not candidates:
            return None

        def _unit_from_name(name: str) -> str:
            lower = name.lower()
            if any(token in lower for token in ["millisecond", "ms"]):
                return "ms"
            if any(token in lower for token in ["microsecond", "us"]):
                return "us"
            if "ns" in lower:
                return "ns"
            return "s"

        candidates.sort(
            key=lambda candidate: (("time" in candidate.lower()) or ("zeit" in candidate.lower()), -frame[candidate].nunique()),
            reverse=True,
        )
        selected = candidates[0]
        if not any(keyword in selected.lower() for keyword in ["time", "zeit"]):
            st.warning(
                f"Selected time column '{selected}' does not contain a 'time/zeit' keyword. Please verify the mapping."
            )
        unit = _unit_from_name(selected)
        elapsed = pd.to_timedelta(pd.to_numeric(frame[selected], errors="coerce"), unit=unit, errors="coerce")
        return elapsed
