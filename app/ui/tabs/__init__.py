"""Tab registry for the Factory-X plotting app."""

from __future__ import annotations

from dataclasses import dataclass

from app.config import TAB_SPECS
from app.ui.tabs import (
    bar_plots,
    box_plots,
    data_processing,
    donut_plots,
    histogram_plots,
    line_plots,
    sankey_plots,
    scatter_plots,
)


@dataclass(frozen=True, slots=True)
class TabDefinition:
    """One registered tab renderer."""

    title: str
    label: str
    module: object


TAB_REGISTRY = [
    TabDefinition(TAB_SPECS[0].title, TAB_SPECS[0].label, data_processing),
    TabDefinition(TAB_SPECS[1].title, TAB_SPECS[1].label, line_plots),
    TabDefinition(TAB_SPECS[2].title, TAB_SPECS[2].label, bar_plots),
    TabDefinition(TAB_SPECS[3].title, TAB_SPECS[3].label, box_plots),
    TabDefinition(TAB_SPECS[4].title, TAB_SPECS[4].label, donut_plots),
    TabDefinition(TAB_SPECS[5].title, TAB_SPECS[5].label, scatter_plots),
    TabDefinition(TAB_SPECS[6].title, TAB_SPECS[6].label, histogram_plots),
    TabDefinition(TAB_SPECS[7].title, TAB_SPECS[7].label, sankey_plots),
]

TAB_BY_TITLE = {tab.title: tab for tab in TAB_REGISTRY}

__all__ = [
    "TAB_BY_TITLE",
    "TAB_REGISTRY",
    "TabDefinition",
    "data_processing",
    "line_plots",
    "bar_plots",
    "box_plots",
    "donut_plots",
    "scatter_plots",
    "histogram_plots",
    "sankey_plots",
]
