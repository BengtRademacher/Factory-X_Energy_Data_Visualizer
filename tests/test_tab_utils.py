from __future__ import annotations

import pandas as pd

from app.ui.tab_utils import sample_distribution_frame, sample_time_ordered_frame


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
