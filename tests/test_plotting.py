from __future__ import annotations

import pandas as pd

from app.plotting import plot_bar, plot_boxplot, plot_sankey_energy_flow


def test_plot_bar_supports_english_sum_mode() -> None:
    df_by_file = {
        "a.csv": pd.DataFrame({"motor": [1, 2]}),
        "b.csv": pd.DataFrame({"motor": [3, 4]}),
    }

    fig = plot_bar(
        df_by_file=df_by_file,
        components=["motor"],
        title="Bar Chart",
        mode="Sum",
        label_rotation=0,
        colors={"motor": "#4B5BA9"},
        hide_x_labels=False,
        figsize=(4, 3),
        line_width=1.0,
        axis_fontsize=10,
        axis_title_fontsize=12,
        ylim=None,
        y_unit="W",
        bar_width=0.5,
        y_tick_step=None,
        y_label="Power P",
        x_label="Files",
    )

    heights = [patch.get_height() for patch in fig.axes[0].patches]
    assert heights == [3.0, 7.0]


def test_plot_sankey_supports_english_modes() -> None:
    frame = pd.DataFrame({"electric": [1, 3], "pneumatic": [2, 6]})

    fig_average = plot_sankey_energy_flow(
        df=frame,
        selected_electric=["electric"],
        selected_pneumatic=["pneumatic"],
        productive_vars=["electric"],
        mode="Average",
        figsize=(4, 3),
        axis_fontsize=10,
        title="Average",
        colors={"Electric": "#4B5BA9", "Pneumatic": "#01A579"},
        unit="W",
    )
    fig_sum = plot_sankey_energy_flow(
        df=frame,
        selected_electric=["electric"],
        selected_pneumatic=["pneumatic"],
        productive_vars=["electric"],
        mode="Sum",
        figsize=(4, 3),
        axis_fontsize=10,
        title="Sum",
        colors={"Electric": "#4B5BA9", "Pneumatic": "#01A579"},
        unit="W",
    )

    average_total_label = fig_average.data[0]["node"]["label"][0]
    sum_total_label = fig_sum.data[0]["node"]["label"][0]

    assert "6 W" in average_total_label
    assert "12 W" in sum_total_label


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
