"""Compatibility facade for plotting helpers."""

from app.plotting_helpers import (
    annotate_file_sections,
    build_even_ticks as _build_even_ticks,
    format_axis_with_unit,
    format_label_with_unit as _format_label_with_unit,
    unit_to_kw_factor as _unit_to_kw_factor,
)
from app.plotting_matplotlib import (
    plot_bar,
    plot_bar_evp,
    plot_boxplot,
    plot_donut,
    plot_histogram,
    plot_line,
    plot_scatter,
    plot_sum,
)
from app.plotting_plotly import plot_sankey_energy_flow

__all__ = [
    "annotate_file_sections",
    "format_axis_with_unit",
    "plot_line",
    "plot_scatter",
    "plot_sum",
    "plot_bar",
    "plot_bar_evp",
    "plot_boxplot",
    "plot_histogram",
    "plot_donut",
    "plot_sankey_energy_flow",
    "_format_label_with_unit",
    "_build_even_ticks",
    "_unit_to_kw_factor",
]
