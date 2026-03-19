"""Shared helpers for Matplotlib and Plotly chart modules."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

plt.rcParams["font.family"] = ["Aptos", "Segoe UI", "sans-serif"]
plt.rcParams["font.sans-serif"] = ["Aptos", "Segoe UI", "Arial", "sans-serif"]


def format_axis_with_unit(
    axis_obj,
    unit_str,
    axis_fontsize,
    min_value=None,
    max_value=None,
    tick_step=None,
    thousands_for_ints=False,
):
    """Apply fixed ticks and show the unit on the second-to-last tick."""
    if min_value is not None and max_value is not None:
        if max_value < min_value:
            min_value, max_value = max_value, min_value
        if tick_step and tick_step > 0:
            if min_value < 0:
                ticks = np.arange(min_value, max_value + tick_step, tick_step)
            else:
                ticks = np.arange(min_value, max_value, tick_step)
            if len(ticks) == 0 or not np.isclose(ticks[-1], max_value):
                ticks = np.append(ticks, max_value)
            if not any(np.isclose(ticks, min_value)):
                ticks = np.insert(ticks, 0, min_value)
            axis_obj.set_ticks(ticks)
        else:
            fig = plt.gcf()
            if fig.canvas:
                fig.canvas.draw()
            ticks = axis_obj.get_ticklocs()
            if len(ticks) == 0:
                ticks = np.array(sorted({min_value, max_value}))
            else:
                ticks[0] = min_value
                ticks[-1] = max_value
            axis_obj.set_ticks(ticks)

    def _format_tick(value, pos):
        ticks = axis_obj.get_ticklocs()
        if len(ticks) >= 2 and np.isclose(value, ticks[-2]) and unit_str:
            return unit_str

        rounded = np.round(value)
        if np.isclose(value, rounded):
            if thousands_for_ints:
                return f"{int(rounded):,}".replace(",", ".")
            return str(int(rounded))
        return f"{value:.2f}".rstrip("0").rstrip(".")

    axis_obj.set_major_formatter(FuncFormatter(_format_tick))
    axis_obj.set_tick_params(labelsize=axis_fontsize)


def annotate_file_sections(ax, boundaries, total_duration, annotation_fontsize):
    """Draw section boundaries and file annotations in line-based plots."""
    if len(boundaries) <= 1:
        return

    ylim = ax.get_ylim()
    for index, (filename, start_time) in enumerate(boundaries):
        if index > 0:
            ax.axvline(x=start_time, linestyle="--", color="grey", linewidth=1)
        next_time = boundaries[index + 1][1] if index + 1 < len(boundaries) else total_duration
        mid_point = start_time + (next_time - start_time) / 2
        y_text = ylim[1] - (ylim[1] - ylim[0]) * 0.03
        ax.text(
            mid_point,
            y_text,
            f"  {filename.split('.')[0]}  ",
            ha="center",
            va="top",
            fontsize=annotation_fontsize,
            bbox=dict(boxstyle="round,pad=0.3,rounding_size=2", fc="white", ec="none", alpha=1.0),
        )
    ax.set_ylim(ylim)


def format_label_with_unit(label: str, unit: str | None) -> str:
    if unit:
        return f"{label} [{unit}]"
    return label


def build_even_ticks(min_value: float, max_value: float, step: float) -> np.ndarray:
    if step <= 0:
        return np.array([min_value, max_value])

    ticks = np.arange(min_value, max_value + step, step)
    if len(ticks) == 0 or not np.isclose(ticks[-1], max_value):
        ticks = np.append(ticks, max_value)
    if not np.isclose(ticks[0], min_value):
        ticks = np.insert(ticks, 0, min_value)
    return np.sort(np.unique(ticks))


def unit_to_kw_factor(unit: str | None) -> float:
    if not unit:
        return 1.0
    normalized = unit.strip().lower()
    if normalized in {"w", "watt", "watts"}:
        return 0.001
    if normalized in {"kw", "kilowatt", "kilowatts"}:
        return 1.0
    return 1.0

