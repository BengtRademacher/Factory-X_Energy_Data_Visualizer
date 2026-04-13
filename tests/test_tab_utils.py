from __future__ import annotations

import pandas as pd
from unittest.mock import Mock

from app.ui import tab_utils
from app.ui.tab_utils import ensure_valid_ranges, sample_distribution_frame, sample_time_ordered_frame


def test_sample_time_ordered_frame_keeps_order_and_target_size() -> None:
    frame = pd.DataFrame({"value": list(range(10))})

    sampled = sample_time_ordered_frame(frame, 4)

    assert len(sampled) == 4
    assert sampled["value"].tolist() == sorted(sampled["value"].tolist())
    assert sampled["value"].tolist()[0] == 0
    assert sampled["value"].tolist()[-1] == 9


def test_sample_distribution_frame_is_deterministic() -> None:
    frame = pd.DataFrame({"value": list(range(20))})

    first = sample_distribution_frame(frame, 5)
    second = sample_distribution_frame(frame, 5)

    assert first.equals(second)


def test_ensure_valid_ranges_ignores_invalid_x_axis_for_categorical_tabs(monkeypatch) -> None:
    warning = Mock()
    monkeypatch.setattr(tab_utils.st, "warning", warning)

    result = ensure_valid_ranges(
        {"ranges_valid": False, "x_range_valid": False, "y_range_valid": True},
        x_axis_relevant=False,
    )

    assert result is True
    warning.assert_not_called()


def test_ensure_valid_ranges_keeps_y_axis_validation_for_categorical_tabs(monkeypatch) -> None:
    warning = Mock()
    monkeypatch.setattr(tab_utils.st, "warning", warning)

    result = ensure_valid_ranges(
        {"ranges_valid": False, "x_range_valid": False, "y_range_valid": False},
        message="Invalid Y range.",
        x_axis_relevant=False,
    )

    assert result is False
    warning.assert_called_once_with("Invalid Y range.")
