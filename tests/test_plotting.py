from __future__ import annotations

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")

from app.plotting import plot_bar, plot_boxplot, plot_donut, plot_histogram, plot_line, plot_sankey_energy_flow, plot_scatter


def test_plot_boxplot_uses_average_per_elapsed_interval() -> None:
    df_by_file = {
        "a.csv": pd.DataFrame(
            {"motor": [2.0, 4.0, 6.0, 10.0]},
            index=pd.to_timedelta([0, 0, 1, 1], unit="s"),
        )
    }

    fig = plot_boxplot(
        df_by_file=df_by_file,
        components=["motor"],
        title="Box Plot",
        figsize=(4, 3),
        axis_fontsize=10,
        axis_title_fontsize=12,
        colors={"motor": "#4B5BA9"},
        line_width=1.0,
        label_rotation=0,
        ylim=None,
        y_unit="W",
        legend_inside=False,
        y_tick_step=None,
        y_label="Power P",
        box_width=0.5,
    )

    median_y = fig.axes[0].lines[4].get_ydata()[0]
    assert median_y == 5.5


def test_plot_scatter_applies_shared_labels_ranges_and_color_scale() -> None:
    fig = plot_scatter(
        df=pd.DataFrame(
            {
                "x": [0.0, 5.0, 10.0],
                "y": [1.0, 2.0, 3.0],
                "color": [10.0, 20.0, 30.0],
            }
        ),
        x_col="x",
        y_col="y",
        color_col="color",
        figsize=(4, 3),
        axis_fontsize=10,
        axis_title_fontsize=12,
        point_size=30.0,
        edge_width=0.5,
        marker="s",
        x_label="Voltage",
        y_label="Current",
        x_unit="V",
        y_unit="A",
        color_label="Temperature",
        xlim=(0.0, 20.0),
        ylim=(0.0, 5.0),
        x_tick_step=10.0,
        y_tick_step=2.5,
        color_min=0.0,
        color_max=40.0,
        color_tick_step=20.0,
    )

    ax = fig.axes[0]
    colorbar_ax = fig.axes[1]
    scatter = ax.collections[0]

    assert ax.get_xlabel() == "Voltage [V]"
    assert ax.get_ylabel() == "Current [A]"
    assert tuple(ax.get_xlim()) == (0.0, 20.0)
    assert tuple(ax.get_ylim()) == (0.0, 5.0)
    assert scatter.norm.vmin == 0.0
    assert scatter.norm.vmax == 40.0
    assert list(colorbar_ax.get_yticks()) == [0.0, 20.0, 40.0]


def test_plot_histogram_uses_even_manual_bins_and_ignores_values_outside_range() -> None:
    fig = plot_histogram(
        series=pd.Series([1.0, 4.0, 9.0, 15.0]),
        title="Histogram",
        figsize=(4, 3),
        axis_fontsize=10,
        axis_title_fontsize=12,
        bins=5,
        line_width=1.0,
        color="#4B5BA9",
        x_label="Selected Range",
        y_label="Distribution",
        xlim=(0.0, 10.0),
        ylim=None,
        x_unit="kW",
        y_unit="%",
        x_tick_step=2.0,
        y_tick_step=25.0,
        bin_edges=np.linspace(0.0, 10.0, 6),
    )

    ax = fig.axes[0]
    left_edges = [round(patch.get_x(), 6) for patch in ax.patches]
    widths = [round(patch.get_width(), 6) for patch in ax.patches]
    heights = [patch.get_height() for patch in ax.patches]

    assert ax.get_xlabel() == "Selected Range"
    assert ax.get_ylabel() == "Distribution"
    assert tuple(ax.get_xlim()) == (0.0, 10.0)
    assert left_edges == [0.0, 2.0, 4.0, 6.0, 8.0]
    assert widths == [2.0, 2.0, 2.0, 2.0, 2.0]
    assert round(sum(heights), 6) == 100.0


def test_plot_line_stacked_uses_multiselect_order_for_cumulative_lines() -> None:
    fig = plot_line(
        combined_df=pd.DataFrame(
            {
                "base": [1.0, 2.0, 3.0],
                "middle": [10.0, 20.0, 30.0],
                "top": [100.0, 200.0, 300.0],
            }
        ),
        x_values=pd.Series([0.0, 1.0, 2.0]),
        file_boundaries=[],
        components=["middle", "base", "top"],
        title="Line Plot",
        colors={"base": "#4B5BA9", "middle": "#006DB9", "top": "#01A579"},
        figsize=(4, 3),
        line_width=1.0,
        axis_fontsize=10,
        axis_title_fontsize=12,
        xlim=None,
        ylim=None,
        x_unit="s",
        y_unit="W",
        stacked=True,
    )

    ax = fig.axes[0]
    line_data = {line.get_label(): list(line.get_ydata()) for line in ax.lines}

    assert line_data["middle"] == [10.0, 20.0, 30.0]
    assert line_data["base"] == [11.0, 22.0, 33.0]
    assert line_data["top"] == [111.0, 222.0, 333.0]


def test_plot_line_stacked_draws_overlapping_zero_based_fills() -> None:
    fig = plot_line(
        combined_df=pd.DataFrame(
            {
                "a": [1.0, 2.0, 3.0],
                "b": [4.0, np.nan, 6.0],
            }
        ),
        x_values=pd.Series([0.0, 1.0, 2.0]),
        file_boundaries=[],
        components=["a", "b"],
        title="Line Plot",
        colors={"a": "#4B5BA9", "b": "#006DB9"},
        figsize=(4, 3),
        line_width=1.0,
        axis_fontsize=10,
        axis_title_fontsize=12,
        xlim=None,
        ylim=None,
        x_unit="s",
        y_unit="W",
        stacked=True,
    )

    ax = fig.axes[0]
    fill_collections = ax.collections

    assert len(fill_collections) == 2

    top_fill_vertices = fill_collections[0].get_paths()[0].vertices
    bottom_fill_vertices = fill_collections[1].get_paths()[0].vertices

    assert 0.0 in top_fill_vertices[:, 1]
    assert 0.0 in bottom_fill_vertices[:, 1]
    assert top_fill_vertices[:, 1].max() == 9.0
    assert bottom_fill_vertices[:, 1].max() == 3.0


def test_plot_line_without_stacking_preserves_raw_component_lines() -> None:
    fig = plot_line(
        combined_df=pd.DataFrame({"a": [1.0, 2.0], "b": [4.0, 5.0]}),
        x_values=pd.Series([0.0, 1.0]),
        file_boundaries=[],
        components=["a", "b"],
        title="Line Plot",
        colors={"a": "#4B5BA9", "b": "#006DB9"},
        figsize=(4, 3),
        line_width=1.0,
        axis_fontsize=10,
        axis_title_fontsize=12,
        xlim=None,
        ylim=None,
        x_unit="s",
        y_unit="W",
        stacked=False,
    )

    ax = fig.axes[0]
    line_data = {line.get_label(): list(line.get_ydata()) for line in ax.lines}

    assert len(ax.collections) == 0
    assert line_data["a"] == [1.0, 2.0]
    assert line_data["b"] == [4.0, 5.0]


def test_plot_line_stacked_keeps_secondary_axis_separate() -> None:
    fig = plot_line(
        combined_df=pd.DataFrame(
            {
                "a": [1.0, 2.0, 3.0],
                "b": [3.0, 4.0, 5.0],
                "secondary": [10.0, 20.0, 30.0],
            }
        ),
        x_values=pd.Series([0.0, 1.0, 2.0]),
        file_boundaries=[],
        components=["a", "b"],
        title="Line Plot",
        colors={"a": "#4B5BA9", "b": "#006DB9"},
        figsize=(4, 3),
        line_width=1.0,
        axis_fontsize=10,
        axis_title_fontsize=12,
        xlim=None,
        ylim=None,
        x_unit="s",
        y_unit="W",
        stacked=True,
        secondary_components=["secondary"],
        secondary_colors={"secondary": "#E50037"},
        secondary_y_unit="A",
        secondary_y_label="Secondary",
        secondary_y_tick_step=10.0,
        secondary_ylim=(0.0, 40.0),
    )

    primary_ax, secondary_ax = fig.axes
    primary_line_data = {line.get_label(): list(line.get_ydata()) for line in primary_ax.lines}
    secondary_line_data = {line.get_label(): list(line.get_ydata()) for line in secondary_ax.lines}

    assert primary_line_data["a"] == [1.0, 2.0, 3.0]
    assert primary_line_data["b"] == [4.0, 6.0, 8.0]
    assert secondary_line_data["secondary"] == [10.0, 20.0, 30.0]
    assert tuple(secondary_ax.get_ylim()) == (0.0, 40.0)


def test_plot_bar_unstacked_single_file_places_components_without_gaps() -> None:
    fig = plot_bar(
        df_by_file={"a.csv": pd.DataFrame({"motor": [999.0], "pump": [999.0]})},
        components=["motor", "pump"],
        title="Bar Chart",
        label_rotation=0,
        colors={"motor": "#4B5BA9", "pump": "#006DB9"},
        hide_x_labels=False,
        figsize=(4, 3),
        line_width=1.0,
        axis_fontsize=10,
        axis_title_fontsize=12,
        ylim=None,
        y_unit="W",
        bar_width=0.4,
        per_file_means=pd.DataFrame({"motor": [5.0], "pump": [7.0]}, index=["a.csv"]),
        stacked=False,
        aggregation_mode="Mean",
    )

    ax = fig.axes[0]
    patches = sorted(ax.patches, key=lambda patch: patch.get_x())

    assert np.isclose(patches[0].get_x() + patches[0].get_width(), patches[1].get_x())
    assert [tick.get_text() for tick in ax.get_xticklabels()] == ["motor", "pump"]
    assert ax.get_xlim()[0] < patches[0].get_x()
    assert ax.get_xlim()[1] > patches[-1].get_x() + patches[-1].get_width()


def test_plot_bar_unstacked_multiple_files_groups_components_by_file() -> None:
    fig = plot_bar(
        df_by_file={
            "a.csv": pd.DataFrame({"motor": [999.0], "pump": [999.0]}),
            "b.csv": pd.DataFrame({"motor": [999.0], "pump": [999.0]}),
        },
        components=["motor", "pump"],
        title="Bar Chart",
        label_rotation=0,
        colors={"motor": "#4B5BA9", "pump": "#006DB9"},
        hide_x_labels=False,
        figsize=(4, 3),
        line_width=1.0,
        axis_fontsize=10,
        axis_title_fontsize=12,
        ylim=None,
        y_unit="W",
        bar_width=0.4,
        per_file_means=pd.DataFrame({"motor": [5.0, 6.0], "pump": [7.0, 8.0]}, index=["a.csv", "b.csv"]),
        stacked=False,
        aggregation_mode="Mean",
    )

    ax = fig.axes[0]
    patches = sorted(ax.patches, key=lambda patch: patch.get_x())
    first_gap = patches[1].get_x() - (patches[0].get_x() + patches[0].get_width())
    second_gap = patches[2].get_x() - (patches[1].get_x() + patches[1].get_width())

    assert np.isclose(first_gap, 0.0)
    assert second_gap > 0.0
    assert [tick.get_text() for tick in ax.get_xticklabels()] == ["a", "b"]


def test_plot_bar_separate_bars_uses_row_values_instead_of_mean() -> None:
    fig = plot_bar(
        df_by_file={
            "a.csv": pd.DataFrame(
                {"motor": [1.0, 3.0]},
                index=pd.to_timedelta([0, 1], unit="s"),
            )
        },
        components=["motor"],
        title="Bar Chart",
        label_rotation=0,
        colors={"motor": "#4B5BA9"},
        hide_x_labels=False,
        figsize=(4, 3),
        line_width=1.0,
        axis_fontsize=10,
        axis_title_fontsize=12,
        ylim=None,
        y_unit="W",
        bar_width=0.4,
        stacked=False,
        aggregation_mode="Seperate Bars",
        x_source_column="elapsedTime",
    )

    ax = fig.axes[0]
    heights = [patch.get_height() for patch in sorted(ax.patches, key=lambda patch: patch.get_x())]

    assert heights == [1.0, 3.0]
    assert [tick.get_text() for tick in ax.get_xticklabels()] == ["0", "1"]


def test_plot_bar_applies_manual_ylim() -> None:
    fig = plot_bar(
        df_by_file={"a.csv": pd.DataFrame({"motor": [999.0]})},
        components=["motor"],
        title="Bar Chart",
        label_rotation=0,
        colors={"motor": "#4B5BA9"},
        hide_x_labels=False,
        figsize=(4, 3),
        line_width=1.0,
        axis_fontsize=10,
        axis_title_fontsize=12,
        ylim=(0.0, 50.0),
        y_unit="W",
        per_file_means=pd.DataFrame({"motor": [5.0]}, index=["a.csv"]),
    )

    assert tuple(fig.axes[0].get_ylim()) == (0.0, 50.0)


def test_plot_bar_unstacked_mean_bar_width_changes_visible_occupancy() -> None:
    common_kwargs = {
        "df_by_file": {"a.csv": pd.DataFrame({"motor": [999.0], "pump": [999.0]})},
        "components": ["motor", "pump"],
        "title": "Bar Chart",
        "label_rotation": 0,
        "colors": {"motor": "#4B5BA9", "pump": "#006DB9"},
        "hide_x_labels": False,
        "figsize": (4, 3),
        "line_width": 1.0,
        "axis_fontsize": 10,
        "axis_title_fontsize": 12,
        "ylim": None,
        "y_unit": "W",
        "per_file_means": pd.DataFrame({"motor": [5.0], "pump": [7.0]}, index=["a.csv"]),
        "stacked": False,
        "aggregation_mode": "Mean",
    }

    fig_small = plot_bar(bar_width=0.2, **common_kwargs)
    fig_large = plot_bar(bar_width=0.6, **common_kwargs)

    ax_small = fig_small.axes[0]
    ax_large = fig_large.axes[0]
    patches_small = sorted(ax_small.patches, key=lambda patch: patch.get_x())
    patches_large = sorted(ax_large.patches, key=lambda patch: patch.get_x())

    occupied_small = (patches_small[-1].get_x() + patches_small[-1].get_width()) - patches_small[0].get_x()
    occupied_large = (patches_large[-1].get_x() + patches_large[-1].get_width()) - patches_large[0].get_x()
    x_range_small = ax_small.get_xlim()[1] - ax_small.get_xlim()[0]
    x_range_large = ax_large.get_xlim()[1] - ax_large.get_xlim()[0]

    assert occupied_large > occupied_small
    assert (occupied_large / x_range_large) > (occupied_small / x_range_small)


def test_plot_bar_can_use_precomputed_file_means() -> None:
    fig = plot_bar(
        df_by_file={"a.csv": pd.DataFrame({"motor": [999.0]})},
        components=["motor"],
        title="Bar Chart",
        label_rotation=0,
        colors={"motor": "#4B5BA9"},
        hide_x_labels=False,
        figsize=(4, 3),
        line_width=1.0,
        axis_fontsize=10,
        axis_title_fontsize=12,
        ylim=None,
        y_unit="W",
        per_file_means=pd.DataFrame({"motor": [5.0]}, index=["a.csv"]),
    )

    bar_height = fig.axes[0].patches[0].get_height()
    assert bar_height == 5.0


def test_plot_boxplot_can_use_precomputed_interval_means() -> None:
    fig = plot_boxplot(
        df_by_file={"a.csv": pd.DataFrame({"motor": [999.0]}, index=pd.to_timedelta([0], unit="s"))},
        components=["motor"],
        title="Box Plot",
        figsize=(4, 3),
        axis_fontsize=10,
        axis_title_fontsize=12,
        colors={"motor": "#4B5BA9"},
        line_width=1.0,
        label_rotation=0,
        ylim=None,
        y_unit="W",
        interval_means_by_file={"a.csv": pd.DataFrame({"motor": [3.0, 7.0]})},
    )

    median_y = fig.axes[0].lines[4].get_ydata()[0]
    assert median_y == 5.0


def test_plot_donut_can_use_precomputed_component_means() -> None:
    fig = plot_donut(
        combined_df=pd.DataFrame(),
        components=["motor", "pump"],
        colors={"motor": "#4B5BA9", "pump": "#006DB9"},
        hole=0.4,
        label_mode="Percent",
        total_target_kw=0.0,
        show_others=False,
        chart_size_px=300,
        title="Donut",
        axis_fontsize=10,
        show_legend=False,
        source_unit="kW",
        component_means=pd.Series({"motor": 2.0, "pump": 6.0}),
    )

    assert fig is not None
    assert len(fig.axes[0].patches) == 2


def test_plot_sankey_can_use_precomputed_component_means() -> None:
    fig = plot_sankey_energy_flow(
        df=pd.DataFrame(),
        selected_electric=["motor"],
        selected_pneumatic=["valve"],
        productive_vars=["motor"],
        figsize=(4, 3),
        axis_fontsize=10,
        colors={"Electric": "#4B5BA9", "Pneumatic": "#01A579"},
        unit="W",
        component_means=pd.Series({"motor": 10.0, "valve": 5.0}),
    )

    assert fig is not None
    assert list(fig.data[0]["link"]["value"])[:2] == [10.0, 5.0]
