from __future__ import annotations

from io import BytesIO

import pandas as pd
import pytest

from app.data_manager import DataManager


@pytest.fixture
def manager() -> DataManager:
    return DataManager()


def _csv_buffer(content: str) -> BytesIO:
    buffer = BytesIO(content.encode("utf-8"))
    buffer.name = "test.csv"
    buffer.seek(0)
    return buffer


def test_load_files_combines_elapsed_time(manager: DataManager) -> None:
    csv_content = "elapsedTime,value\n0,10\n1,20\n2,30"
    buffer = _csv_buffer(csv_content)

    data = manager.load_files([buffer])

    assert data.has_data
    assert "elapsedTime" in data.combined_frame.columns
    assert data.combined_frame["value"].tolist() == [10, 20, 30]


def test_sum_components(manager: DataManager) -> None:
    index = pd.to_timedelta([0, 1, 2], unit="s")
    df = pd.DataFrame({"elapsedTime": index, "a": [1, 2, 3], "b": [4, 5, 6]}).set_index("elapsedTime")
    data = {"file": df}

    result = manager.sum_components(data, ["a", "b"])

    assert not result.empty
    assert result.shape == (3, 1)
    assert list(result.columns) == ["file"]
    assert result.iloc[:, 0].tolist() == [5, 7, 9]


def test_sum_categories(manager: DataManager) -> None:
    index = pd.to_timedelta([0, 1, 2], unit="s")
    df = pd.DataFrame(
        {
            "elapsedTime": index,
            "elec_a": [1, 2, 3],
            "pneu_a": [4, 5, 6],
        }
    ).set_index("elapsedTime")

    data = {"file": df}
    result = manager.sum_categories(data, ["elec_a"], ["pneu_a"])

    assert list(result.columns) == ["Electric", "Pneumatic"]
    assert result.iloc[0].tolist() == [1, 4]


def test_ensure_elapsed_time_accepts_german_time_columns(manager: DataManager) -> None:
    frame = pd.DataFrame({"zeit": [0, 1, 2.5], "power": [1, 2, 3]})

    result = manager.ensure_elapsed_time(frame.copy(), "demo.csv")

    assert "elapsedTime" in result.columns
    assert result["elapsedTime"].dt.total_seconds().tolist() == [0.0, 1.0, 2.5]


def test_load_files_exposes_metadata_diagnostics_and_means(manager: DataManager) -> None:
    csv_content = "value,status\n10,on\n5,off\n30,on"
    buffer = _csv_buffer(csv_content)

    data = manager.load_files([buffer])

    assert data.available_columns == ["value", "status"]
    assert data.numeric_columns == ["value"]
    assert data.per_file_numeric_means.loc["test.csv", "value"] == 15.0
    assert data.overall_numeric_means["value"] == 15.0
    assert "value" in data.interval_means_by_file["test.csv"].columns
    assert any("Derived time from the row index" in diagnostic.message for diagnostic in data.diagnostics)


def test_load_files_uses_content_based_upload_signatures(manager: DataManager) -> None:
    first = manager.load_files([_csv_buffer("elapsedTime,value\n0,10\n1,20")])
    second = manager.load_files([_csv_buffer("elapsedTime,value\n0,10\n1,999")])

    assert first.upload_signature != second.upload_signature
