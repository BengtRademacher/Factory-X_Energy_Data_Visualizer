"""Central configuration for the Factory-X Energy Data Visualizer."""

from dataclasses import dataclass, field
from typing import List

# -----------------------------------------------------------------------------
# Colors
# -----------------------------------------------------------------------------
DEFAULT_COLORS = [
    "#4B5BA9",
    "#006DB9",
    "#007CC5",
    "#01A579",
    "#B1CB21",
    "#F9B31A",
    "#EF7100",
    "#E50037",
]

COMBINED_BAR_COLORS = [
    "#4B5BA9",
    "#006DB9",
    "#007CC5",
    "#01A579",
    "#B1CB21",
    "#F9B31A",
    "#EF7100",
    "#E50037",
    "#16A085",
]

COLOR_PALETTE = {
    "Purple": "#4B5BA9",
    "Blue": "#006DB9",
    "Light Blue": "#007CC5",
    "Dark Green": "#01A579",
    "Light Green": "#B1CB21",
    "Yellow": "#F9B31A",
    "Orange": "#EF7100",
    "Red": "#E50037",
    "Teal": "#16A085",
}


# -----------------------------------------------------------------------------
# Plot configuration
# -----------------------------------------------------------------------------
@dataclass
class PlotDefaults:
    """Default values shared across plot types."""

    width: float = 300.0
    height: float = 150.0
    font_family: str = "Aptos"
    title_fontsize: int = 20
    axis_fontsize: int = 16
    axis_title_fontsize: int = 20
    line_width: float = 2.0
    x_label: str = "Time t"
    y_label: str = "Power P"
    x_unit: str = "s"
    y_unit: str = "W"
    x_tick_step: float = 100.0
    y_tick_step: float = 1000.0
    x_min: float = 0.0
    x_max: float = 100.0
    y_min: float = 0.0
    y_max: float = 100.0
    label_rotation: int = 45


@dataclass
class BarPlotDefaults:
    """Default values for bar charts."""

    bar_width: float = 0.25
    hide_x_labels: bool = False
    label_rotation: int = 45


@dataclass
class BoxPlotDefaults:
    """Default values for box plots."""

    box_width: float = 0.8
    label_rotation: int = 45


@dataclass
class DonutDefaults:
    """Default values for donut charts."""

    hole: float = 0.4
    chart_size_px: int = 600
    label_mode: str = "Percent"
    show_others: bool = False
    show_legend: bool = True
    total_target_kw: float = 0.0
    title: str = "Donut - Average Load"


@dataclass
class ScatterDefaults:
    """Default values for scatter plots."""

    point_size: float = 30.0
    edge_width: float = 0.5
    point_type: str = "Circle"
    color_label: str = ""
    color_min: str = ""
    color_max: str = ""
    color_tick_step: str = ""


@dataclass
class HistogramDefaults:
    """Default values for histograms."""

    bins: int = 40
    line_width: float = 1.5


@dataclass
class SankeyDefaults:
    """Default values for Sankey charts."""

    unit: str = "W"
    title: str = "Sankey Diagram"


@dataclass
class SecondaryAxisDefaults:
    """Default values for a secondary Y axis."""

    enabled: bool = False
    label: str = "Secondary value"
    unit: str = ""
    tick_step: float = 0.0
    min_value: float = 0.0
    max_value: float = 100.0


@dataclass
class ExportDefaults:
    """Default values for exports."""

    filename: str = "export"
    formats: List[str] = field(default_factory=lambda: ["PDF", "PNG"])
    separate_files: bool = False


PLOT_DEFAULTS = PlotDefaults()
BAR_DEFAULTS = BarPlotDefaults()
BOX_DEFAULTS = BoxPlotDefaults()
DONUT_DEFAULTS = DonutDefaults()
SCATTER_DEFAULTS = ScatterDefaults()
HISTOGRAM_DEFAULTS = HistogramDefaults()
SANKEY_DEFAULTS = SankeyDefaults()
SECONDARY_AXIS_DEFAULTS = SecondaryAxisDefaults()
EXPORT_DEFAULTS = ExportDefaults()


# -----------------------------------------------------------------------------
# UI configuration
# -----------------------------------------------------------------------------
APP_TITLE = "Factory-X Energy Data Visualizer"
LOGO_FILENAME = "FX_logo_top_left.png"


@dataclass(frozen=True, slots=True)
class TabSpec:
    """Describes a tab with an internal title and visible label."""

    title: str
    label: str


TAB_SPECS = [
    TabSpec("Data Processing", ":material/settings: Data Processing"),
    TabSpec("Line Plots", ":material/trending_up: Line Plots"),
    TabSpec("Bar Charts", ":material/bar_chart: Bar Charts"),
    TabSpec("Box Plots", ":material/insights: Box Plots"),
    TabSpec("Pie and Donut Charts", ":material/pie_chart: Pie and Donut Charts"),
    TabSpec("Scatter Plot", ":material/scatter_plot: Scatter Plot"),
    TabSpec("Histogram", ":material/equalizer: Histogram"),
    TabSpec("Sankey", ":material/account_tree: Sankey"),
]


# -----------------------------------------------------------------------------
# Sampling limits for performance
# -----------------------------------------------------------------------------
MAX_PREVIEW_ROWS = 1000
MAX_PLOT_ROWS = 1_000_000
MAX_SUMMARY_ROWS = 1_000_000
