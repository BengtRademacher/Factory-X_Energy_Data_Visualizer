"""Data ingestion and preprocessing services for the plotting application."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from io import BytesIO
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import streamlit as st
from pandas.errors import EmptyDataError, ParserError


@dataclass(frozen=True, slots=True)
class LoadDiagnostic:
    """Represents one informational or warning message from the load pipeline."""

    level: str
    message: str
    file_name: str | None = None


@dataclass(frozen=True, slots=True)
class UploadPayload:
    """Serializable upload payload used by the cached processing core."""

    name: str
    size: int
    content: bytes
    signature: str


@dataclass(slots=True)
class ProcessedData:
    """Represents the processed outputs for the application."""

    combined_frame: pd.DataFrame
    file_boundaries: List[Tuple[str, pd.Timedelta]]
    frames_by_file: Dict[str, pd.DataFrame]
    upload_signature: Tuple[str, ...] = ()
    available_columns: List[str] = field(default_factory=list)
    numeric_columns: List[str] = field(default_factory=list)
    diagnostics: List[LoadDiagnostic] = field(default_factory=list)
    per_file_numeric_means: pd.DataFrame = field(default_factory=pd.DataFrame)
    overall_numeric_means: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))
    interval_means_by_file: Dict[str, pd.DataFrame] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.available_columns and self.combined_frame is not None and not self.combined_frame.empty:
            self.available_columns = [
                column for column in self.combined_frame.columns
                if column != DataManager.elapsed_column
            ]

        if not self.numeric_columns and self.combined_frame is not None and not self.combined_frame.empty:
            self.numeric_columns = [
                column for column in self.available_columns
                if column in self.combined_frame.columns and pd.api.types.is_numeric_dtype(self.combined_frame[column])
            ]

    @property
    def has_data(self) -> bool:
        return self.combined_frame is not None and not self.combined_frame.empty


def _empty_processed_data(upload_signature: Tuple[str, ...] = ()) -> ProcessedData:
    return ProcessedData(
        combined_frame=pd.DataFrame(),
        file_boundaries=[],
        frames_by_file={},
        upload_signature=upload_signature,
    )


@st.cache_data(show_spinner=False)
def _load_payloads_cached(payloads: Tuple[UploadPayload, ...]) -> ProcessedData:
    """Cache the expensive read/normalize path for unchanged uploads."""
    return DataManager._load_payloads_core(payloads)


class DataManager:
    """Provides high-level data ingestion and transformation utilities."""

    elapsed_column = "elapsedTime"

    def load_files(self, uploaded_files: Sequence) -> ProcessedData:
        """Load uploaded files and merge them into one processed payload."""
        payloads = self._build_payloads(uploaded_files)
        if not payloads:
            return _empty_processed_data()
        return _load_payloads_cached(payloads)

    @classmethod
    def _load_payloads_core(cls, payloads: Tuple[UploadPayload, ...]) -> ProcessedData:
        if not payloads:
            return _empty_processed_data()

        all_frames: List[pd.DataFrame] = []
        file_boundaries: List[Tuple[str, pd.Timedelta]] = []
        frames_by_file: Dict[str, pd.DataFrame] = {}
        diagnostics: List[LoadDiagnostic] = []
        offset = pd.Timedelta(seconds=0)

        for payload in payloads:
            frame, read_diagnostics = cls._read_payload(payload)
            diagnostics.extend(read_diagnostics)
            if frame is None or frame.empty:
                diagnostics.append(
                    LoadDiagnostic("warning", "File could not be read.", file_name=payload.name)
                )
                continue

            frame, elapsed_diagnostics = cls._ensure_elapsed_time_with_diagnostics(frame, payload.name)
            diagnostics.extend(elapsed_diagnostics)
            if frame.empty:
                diagnostics.append(
                    LoadDiagnostic(
                        "warning",
                        "File does not contain usable time information and was skipped.",
                        file_name=payload.name,
                    )
                )
                continue

            frame[cls.elapsed_column] = frame[cls.elapsed_column] + offset
            frame.set_index(cls.elapsed_column, inplace=True)

            file_boundaries.append((payload.name, frame.index[0]))
            frames_by_file[payload.name] = frame
            all_frames.append(frame.reset_index())

            offset = frame.index[-1]
            if len(frame.index) > 1:
                step = frame.index[1] - frame.index[0]
                if isinstance(step, pd.Timedelta):
                    offset += step

        combined = pd.concat(all_frames, ignore_index=True) if all_frames else pd.DataFrame()
        upload_signature = tuple(f"{payload.name}:{payload.size}:{payload.signature}" for payload in payloads)
        available_columns = [
            column for column in combined.columns
            if column != cls.elapsed_column
        ]
        numeric_columns = [
            column for column in available_columns
            if column in combined.columns and pd.api.types.is_numeric_dtype(combined[column])
        ]

        per_file_numeric_means = cls._compute_per_file_numeric_means(frames_by_file, numeric_columns)
        overall_numeric_means = cls._compute_overall_numeric_means(combined, numeric_columns)
        interval_means_by_file = cls._compute_interval_means_by_file(frames_by_file, numeric_columns)

        return ProcessedData(
            combined_frame=combined,
            file_boundaries=file_boundaries,
            frames_by_file=frames_by_file,
            upload_signature=upload_signature,
            available_columns=available_columns,
            numeric_columns=numeric_columns,
            diagnostics=diagnostics,
            per_file_numeric_means=per_file_numeric_means,
            overall_numeric_means=overall_numeric_means,
            interval_means_by_file=interval_means_by_file,
        )

    @classmethod
    def _build_payloads(cls, uploaded_files: Sequence) -> Tuple[UploadPayload, ...]:
        payloads: List[UploadPayload] = []
        for uploaded_file in uploaded_files:
            content = cls._read_uploaded_bytes(uploaded_file)
            if content is None:
                continue

            name = getattr(uploaded_file, "name", "Unknown file")
            payloads.append(
                UploadPayload(
                    name=name,
                    size=len(content),
                    content=content,
                    signature=sha256(content).hexdigest(),
                )
            )
        return tuple(payloads)

    @staticmethod
    def _read_uploaded_bytes(uploaded_file) -> bytes | None:
        if uploaded_file is None:
            return None

        if hasattr(uploaded_file, "getvalue"):
            content = uploaded_file.getvalue()
        elif hasattr(uploaded_file, "read"):
            content = uploaded_file.read()
        else:
            return None

        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)
        return content

    def ensure_elapsed_time(self, frame: pd.DataFrame, file_name: str | None = None) -> pd.DataFrame:
        """Ensure that the frame contains a normalized elapsed time column."""
        normalized, _ = self._ensure_elapsed_time_with_diagnostics(frame, file_name)
        return normalized

    @classmethod
    def _ensure_elapsed_time_with_diagnostics(
        cls,
        frame: pd.DataFrame,
        file_name: str | None = None,
    ) -> tuple[pd.DataFrame, list[LoadDiagnostic]]:
        diagnostics: list[LoadDiagnostic] = []
        if cls.elapsed_column in frame.columns:
            return cls._normalize_elapsed_series(frame), diagnostics

        elapsed = cls._from_datetime_columns(frame)
        if elapsed is not None:
            frame[cls.elapsed_column] = elapsed
            return cls._normalize_elapsed_series(frame), diagnostics

        elapsed = cls._from_numeric_columns(frame)
        if elapsed is not None:
            frame[cls.elapsed_column] = elapsed
            return cls._normalize_elapsed_series(frame), diagnostics

        frame[cls.elapsed_column] = pd.to_timedelta(np.arange(len(frame)), unit="s")
        diagnostics.append(
            LoadDiagnostic(
                "info",
                "Derived time from the row index (1 s step).",
                file_name=file_name or "file",
            )
        )
        return frame, diagnostics

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
    def _read_payload(payload: UploadPayload) -> tuple[pd.DataFrame | None, list[LoadDiagnostic]]:
        """Read one cached CSV or Excel payload."""
        diagnostics: list[LoadDiagnostic] = []
        try:
            lowered = payload.name.lower()
            buffer = BytesIO(payload.content)
            if lowered.endswith(".csv"):
                return pd.read_csv(buffer, sep=None, engine="python"), diagnostics
            return pd.read_excel(buffer), diagnostics
        except (ParserError, EmptyDataError) as exc:
            diagnostics.append(
                LoadDiagnostic(
                    "warning",
                    f"File could not be parsed: {exc}. Please check the file format.",
                    file_name=payload.name,
                )
            )
        except ValueError as exc:
            diagnostics.append(
                LoadDiagnostic(
                    "warning",
                    f"File contains invalid values and was skipped ({exc}).",
                    file_name=payload.name,
                )
            )
        except Exception as exc:
            diagnostics.append(
                LoadDiagnostic(
                    "warning",
                    f"An unexpected error occurred while loading the file: {exc}.",
                    file_name=payload.name,
                )
            )
        return None, diagnostics

    @classmethod
    def _normalize_elapsed_series(cls, frame: pd.DataFrame) -> pd.DataFrame:
        """Normalize the elapsed time series to timedeltas starting at zero."""
        series = frame[cls.elapsed_column]
        if not pd.api.types.is_timedelta64_dtype(series):
            if pd.api.types.is_numeric_dtype(series):
                frame[cls.elapsed_column] = pd.to_timedelta(series, unit="s", errors="coerce")
            else:
                frame[cls.elapsed_column] = pd.to_timedelta(series.astype(str), errors="coerce")

        frame.dropna(subset=[cls.elapsed_column], inplace=True)
        if frame.empty:
            return frame

        frame[cls.elapsed_column] = frame[cls.elapsed_column] - frame[cls.elapsed_column].iloc[0]
        return frame

    @staticmethod
    def _from_datetime_columns(frame: pd.DataFrame) -> Optional[pd.Series]:
        """Try to derive elapsed time from datetime-like columns."""
        best_parsed: Optional[pd.Series] = None
        best_ratio = 0.0

        for col in frame.columns:
            series = frame[col]
            if pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_datetime64_any_dtype(series):
                continue
            if not pd.api.types.is_datetime64_any_dtype(series):
                string_values = series.astype(str)
                if float(string_values.str.contains(r"\d", regex=True).mean()) < 0.6:
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

    @staticmethod
    def _from_numeric_columns(frame: pd.DataFrame) -> Optional[pd.Series]:
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
        unit = _unit_from_name(selected)
        elapsed = pd.to_timedelta(pd.to_numeric(frame[selected], errors="coerce"), unit=unit, errors="coerce")
        return elapsed

    @staticmethod
    def _compute_per_file_numeric_means(
        frames_by_file: Dict[str, pd.DataFrame],
        numeric_columns: Sequence[str],
    ) -> pd.DataFrame:
        rows: dict[str, pd.Series] = {}
        for file_name, frame in frames_by_file.items():
            available = [column for column in numeric_columns if column in frame.columns]
            if not available:
                rows[file_name] = pd.Series(dtype=float)
                continue
            rows[file_name] = frame[available].apply(pd.to_numeric, errors="coerce").mean(axis=0)
        return pd.DataFrame.from_dict(rows, orient="index")

    @staticmethod
    def _compute_overall_numeric_means(
        combined_frame: pd.DataFrame,
        numeric_columns: Sequence[str],
    ) -> pd.Series:
        if combined_frame.empty or not numeric_columns:
            return pd.Series(dtype=float)
        return combined_frame[list(numeric_columns)].apply(pd.to_numeric, errors="coerce").mean(axis=0)

    @staticmethod
    def _compute_interval_means_by_file(
        frames_by_file: Dict[str, pd.DataFrame],
        numeric_columns: Sequence[str],
    ) -> Dict[str, pd.DataFrame]:
        interval_means: Dict[str, pd.DataFrame] = {}
        for file_name, frame in frames_by_file.items():
            available = [column for column in numeric_columns if column in frame.columns]
            if not available:
                interval_means[file_name] = pd.DataFrame(index=frame.index.unique())
                continue
            numeric_frame = frame[available].apply(pd.to_numeric, errors="coerce")
            interval_means[file_name] = numeric_frame.groupby(level=0).mean()
        return interval_means
