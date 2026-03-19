from __future__ import annotations

import pandas as pd

from app.data_manager import ProcessedData
from app.x_axis import resolve_frame_x_axis, resolve_processed_x_axis


def test_resolve_frame_x_axis_accepts_numeric_datetime_and_timedelta() -> None:
    frame = pd.DataFrame(
        {
            "num": [10, 20, 35],
            "dt": pd.to_datetime(["2024-01-01 00:00:00", "2024-01-01 00:00:02", "2024-01-01 00:00:05"]),
            "delta": pd.to_timedelta([0, 3, 7], unit="s"),
        }
    )

    assert resolve_frame_x_axis(frame, "num").error is None
    assert resolve_frame_x_axis(frame, "dt").values.tolist() == [0.0, 2.0, 5.0]
    assert resolve_frame_x_axis(frame, "delta").values.tolist() == [0.0, 3.0, 7.0]


def test_resolve_frame_x_axis_rejects_text() -> None:
    frame = pd.DataFrame({"status": ["on", "off", "idle"]})

    result = resolve_frame_x_axis(frame, "status", file_name="demo.csv")

    assert result.error is not None
    assert "status" in result.error


def test_resolve_processed_x_axis_continues_multiple_files() -> None:
    frame_a = pd.DataFrame({"x": [0, 250, 500], "y": [1, 2, 3]})
    frame_b = pd.DataFrame({"x": [0, 400, 800], "y": [4, 5, 6]})
    processed = ProcessedData(
        combined_frame=pd.concat([frame_a, frame_b], ignore_index=True),
        file_boundaries=[],
        frames_by_file={"a.csv": frame_a, "b.csv": frame_b},
    )

    result = resolve_processed_x_axis(processed, "x")

    assert result.error is None
    assert result.values.tolist() == [0.0, 250.0, 500.0, 500.0, 900.0, 1300.0]
    assert result.file_boundaries == [("a.csv", 0.0), ("b.csv", 500.0)]


def test_resolve_processed_x_axis_blocks_when_column_missing_in_one_file() -> None:
    frame_a = pd.DataFrame({"x": [0, 1], "y": [1, 2]})
    frame_b = pd.DataFrame({"y": [3, 4]})
    processed = ProcessedData(
        combined_frame=pd.concat([frame_a, frame_b], ignore_index=True, sort=False),
        file_boundaries=[],
        frames_by_file={"a.csv": frame_a, "b.csv": frame_b},
    )

    result = resolve_processed_x_axis(processed, "x")

    assert result.error is not None
    assert "b.csv" in result.error


def test_resolve_frame_x_axis_accepts_elapsed_time_from_index() -> None:
    frame = pd.DataFrame(
        {"power": [1, 2, 3]},
        index=pd.to_timedelta([0, 2, 5], unit="s"),
    )
    frame.index.name = "elapsedTime"

    result = resolve_frame_x_axis(frame, "elapsedTime", file_name="demo.xlsx")

    assert result.error is None
    assert result.values.tolist() == [0.0, 2.0, 5.0]
