"""Zentrale Konfiguration für den Factory-X_Energy_Data_Visualizer.

Alle Standardwerte für Plots, UI und Export sind hier definiert.
"""

from dataclasses import dataclass, field
from typing import List, Dict

# -----------------------------------------------------------------------------
# Farben
# -----------------------------------------------------------------------------
DEFAULT_COLORS = [
    '#4B5BA9', '#006DB9', '#007CC5', '#01A579',
    '#B1CB21', '#F9B31A', '#EF7100', '#E50037'
]

COMBINED_BAR_COLORS = [
    '#4B5BA9', '#006DB9', '#007CC5', '#01A579', '#B1CB21',
    '#F9B31A', '#EF7100', '#E50037', '#8E44AD', '#D35400', '#16A085'
]

# -----------------------------------------------------------------------------
# Vordefinierte Variablen (Komponenten)
# -----------------------------------------------------------------------------
VARS_ELEKTRISCH = [
    'Hauptversorgung', '24V-Versorgung', 'Antriebe', 'Bandfilteranlage',
    'Hebepumpe', 'Kühlung', 'KühlungSchaltschrank', 'Späneförderer',
    'NebelRauchabscheider'
]

VARS_PNEUMATISCH = [
    'AirPower_Hauptversorgung', 'AirPower_Blum', 'AirPower_Hauptventilblock',
    'AirPower_BlasluftKegelreinigung', 'AirPower_KlemmungTisch',
    'AirPower_NPS', 'AirPower_Werkzeugkühlung', 'AirPower_OlLuftschmierungSpindel',
    'AirPower_Sperrluft', 'AirPower_BlasluftSpindelMitte'
]


# -----------------------------------------------------------------------------
# Plot-Konfiguration
# -----------------------------------------------------------------------------
@dataclass
class PlotDefaults:
    """Standardwerte für alle Plot-Typen."""
    
    # Dimensionen (in mm)
    width: float = 300.0
    height: float = 150.0
    
    # Schrift
    font_family: str = 'Arial'
    title_fontsize: int = 20
    axis_fontsize: int = 16
    axis_title_fontsize: int = 20
    
    # Linien
    line_width: float = 2.0
    
    # Achsen
    x_label: str = "Zeit t"
    y_label: str = "Leistung P"
    x_unit: str = "s"
    y_unit: str = "W"
    x_tick_step: float = 100.0
    y_tick_step: float = 1000.0
    
    # Grenzen
    x_min: float = 0.0
    x_max: float = 100.0
    y_min: float = 0.0
    y_max: float = 100.0
    
    # Beschriftung
    label_rotation: int = 45


@dataclass
class BarPlotDefaults:
    """Standardwerte für Säulendiagramme."""
    bar_width: float = 0.25
    mode: str = "Mittelwert"  # "Mittelwert" oder "Summe"
    hide_x_labels: bool = False
    label_rotation: int = 45


@dataclass
class BoxPlotDefaults:
    """Standardwerte für Boxplots."""
    box_width: float = 0.8
    label_rotation: int = 45


@dataclass
class DonutDefaults:
    """Standardwerte für Donut-Diagramme."""
    hole: float = 0.4
    chart_size_px: int = 600
    label_mode: str = "Prozent"  # "Prozent" oder "kW"
    show_others: bool = False
    show_legend: bool = True
    total_target_kw: float = 0.0
    title: str = "Donut – Durchschnittslast"


@dataclass
class ScatterDefaults:
    """Standardwerte für Scatter-Plots."""
    point_size: float = 30.0
    edge_width: float = 0.5
    x_unit: str = ""
    y_unit: str = ""
    color_label: str = ""


@dataclass
class HistogramDefaults:
    """Standardwerte für Histogramme."""
    bins: int = 40
    line_width: float = 1.5


@dataclass
class SankeyDefaults:
    """Standardwerte für Sankey-Diagramme."""
    mode: str = "Mittelwert"
    unit: str = "W"
    title: str = "Sankey-Diagramm"


@dataclass
class SecondaryAxisDefaults:
    """Standardwerte für sekundäre Y-Achsen."""
    enabled: bool = False
    label: str = "Sekundärwert"
    unit: str = ""
    tick_step: float = 0.0
    min_value: float = 0.0
    max_value: float = 100.0


@dataclass
class ExportDefaults:
    """Standardwerte für den Export."""
    filename: str = "name"
    formats: List[str] = field(default_factory=lambda: ["PDF", "PNG"])
    separate_files: bool = False


# Singleton-Instanzen für einfachen Zugriff
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
# UI-Konfiguration
# -----------------------------------------------------------------------------
APP_TITLE = "Factory-X Energy Data Visualizer"
LOGO_FILENAME = "FX_logo_top_left.png"

# Tab-Namen
TAB_NAMES = [
    "Data Processing",
    "Linienplots",
    "Säulendiagramme",
    "Boxplots",
    "Torten und Donuts",
    "Scatter",
    "Histogramm",
    "Sankey",
]

# Material Icons für Tabs
TAB_ICONS = {
    "Data Processing": "settings",
    "Linienplots": "trending_up",
    "Säulendiagramme": "bar_chart",
    "Boxplots": "insights",
    "Torten und Donuts": "pie_chart",
    "Scatter": "scatter_plot",
    "Histogramm": "equalizer",
    "Sankey": "account_tree",
}


# -----------------------------------------------------------------------------
# Sampling-Limits für Performance
# -----------------------------------------------------------------------------
MAX_PREVIEW_ROWS = 1000
MAX_PLOT_ROWS = 1_000_000
MAX_SUMMARY_ROWS = 1_000_000
