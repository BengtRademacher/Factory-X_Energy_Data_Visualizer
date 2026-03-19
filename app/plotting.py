"""Plotting helpers for Matplotlib and Plotly charts."""

from __future__ import annotations

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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


def plot_line(
    combined_df,
    x_values,
    file_boundaries,
    components,
    title,
    colors,
    figsize,
    line_width,
    axis_fontsize,
    axis_title_fontsize,
    xlim,
    ylim,
    x_unit,
    y_unit,
    x_tick_step=None,
    y_tick_step=None,
    x_label="Time t",
    y_label="Power P",
    stacked=False,
    secondary_components=None,
    secondary_colors=None,
    secondary_y_unit=None,
    secondary_y_label="Secondary value",
    secondary_y_tick_step=None,
    secondary_ylim=None,
):
    if not components or combined_df.empty:
        return None

    fig, ax = plt.subplots(figsize=figsize)
    time_sec = pd.Series(x_values).reset_index(drop=True)
    if len(time_sec) != len(combined_df):
        return None

    legend_handles = []
    legend_labels = []
    plotted_series = []
    cumulative_values = np.zeros(len(combined_df), dtype=float)
    for component in components:
        if component not in combined_df.columns:
            continue

        component_values = pd.to_numeric(combined_df[component], errors="coerce").fillna(0.0).to_numpy(dtype=float)
        if stacked:
            cumulative_values = cumulative_values + component_values
            plotted_values = cumulative_values.copy()
        else:
            plotted_values = component_values

        plotted_series.append((component, plotted_values))

    if stacked:
        for component, plotted_values in reversed(plotted_series):
            ax.fill_between(
                time_sec,
                0,
                plotted_values,
                color=colors.get(component, "#333333"),
                linewidth=0,
                alpha=1.0,
                zorder=1,
            )

    for component, plotted_values in plotted_series:
        line = ax.plot(
            time_sec,
            plotted_values,
            label=component,
            color=colors.get(component, "#333333"),
            linewidth=line_width,
            zorder=3,
        )
        legend_handles.extend(line)
        legend_labels.append(component)

    ax.set_title(title, fontsize=20, fontweight="bold", pad=20)
    ax.set_xlabel(x_label, fontsize=axis_title_fontsize)
    ax.set_ylabel(y_label, fontsize=axis_title_fontsize)
    ax.tick_params(axis="both", which="major", labelsize=axis_fontsize, length=0)
    ax.yaxis.grid(True, linestyle="-", color="black", linewidth=1, alpha=1)
    ax.xaxis.grid(True, linestyle="-", color="black", linewidth=1, alpha=1)

    x_left = xlim[0] if xlim else 0
    x_right = xlim[1] if xlim else time_sec.max()
    ax.set_xlim(left=x_left, right=x_right)
    if ylim:
        y_bottom, y_top = ylim
        ax.set_ylim(bottom=y_bottom, top=y_top)
    else:
        y_bottom = 0
        ax.set_ylim(bottom=0)

    ax.margins(x=0, y=0)
    annotate_file_sections(ax, file_boundaries, float(time_sec.max()), annotation_fontsize=axis_fontsize)

    current_xlim = ax.get_xlim()
    current_ylim = ax.get_ylim()
    format_axis_with_unit(
        ax.xaxis,
        x_unit,
        axis_fontsize,
        min_value=x_left,
        max_value=current_xlim[1],
        tick_step=x_tick_step,
        thousands_for_ints=True,
    )
    format_axis_with_unit(
        ax.yaxis,
        y_unit,
        axis_fontsize,
        min_value=y_bottom,
        max_value=current_ylim[1],
        tick_step=y_tick_step,
        thousands_for_ints=True,
    )
    ax.set_xlim(left=x_left, right=x_right)
    ax.set_ylim(bottom=y_bottom, top=(y_top if ylim else ax.get_ylim()[1]))

    secondary_components = secondary_components or []
    if secondary_components:
        ax2 = ax.twinx()
        secondary_colors = secondary_colors or {}
        first_color = secondary_colors.get(secondary_components[0], "#999999")
        for component in secondary_components:
            if component in combined_df.columns:
                line = ax2.plot(
                    time_sec,
                    combined_df[component].fillna(0),
                    label=component,
                    color=secondary_colors.get(component, "#999999"),
                    linewidth=line_width,
                    linestyle="--",
                )
                legend_handles.extend(line)
                legend_labels.append(component)
        ax2.set_ylabel(secondary_y_label, fontsize=axis_title_fontsize, color=first_color)
        ax2.tick_params(axis="y", which="major", labelsize=axis_fontsize, length=0, colors=first_color)
        if secondary_ylim and len(secondary_ylim) == 2:
            secondary_y_bottom, secondary_y_max = secondary_ylim
            ax2.set_ylim(secondary_y_bottom, secondary_y_max)
        else:
            secondary_y_bottom, secondary_y_max = ax2.get_ylim()
        format_axis_with_unit(
            ax2.yaxis,
            secondary_y_unit or "",
            axis_fontsize,
            min_value=secondary_y_bottom,
            max_value=secondary_y_max,
            tick_step=secondary_y_tick_step,
            thousands_for_ints=True,
        )
        if secondary_ylim and len(secondary_ylim) == 2:
            ax2.set_ylim(secondary_y_bottom, secondary_y_max)
        for spine in ax2.spines.values():
            spine.set_linewidth(1.5)

    if legend_handles:
        ax.legend(
            legend_handles,
            legend_labels,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.15),
            ncol=max(1, min(3, len(legend_labels))),
        )

    for spine in ax.spines.values():
        spine.set_linewidth(1.5)

    ax.set_xmargin(0)
    ax.set_ymargin(0)
    ax.autoscale(enable=False)
    fig.tight_layout()
    return fig


def plot_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    *,
    color_col: str | None,
    figsize: tuple,
    axis_fontsize: int,
    axis_title_fontsize: int,
    point_size: float,
    edge_width: float,
    marker: str,
    x_label: str,
    y_label: str,
    x_unit: str | None,
    y_unit: str | None,
    color_label: str | None,
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
    x_tick_step: float | None = None,
    y_tick_step: float | None = None,
    color_min: float | None = None,
    color_max: float | None = None,
    color_tick_step: float | None = None,
):
    if df.empty or x_col not in df or y_col not in df:
        return None

    x = pd.to_numeric(df[x_col], errors="coerce")
    y = pd.to_numeric(df[y_col], errors="coerce")
    mask = x.notna() & y.notna()
    if not mask.any():
        return None

    x = x[mask]
    y = y[mask]
    color_series = df[color_col][mask] if color_col and color_col in df.columns else None

    fig, ax = plt.subplots(figsize=figsize)
    scatter_kwargs = {
        "s": point_size,
        "linewidth": edge_width,
        "alpha": 0.85,
        "edgecolors": "black" if edge_width > 0 else "none",
        "marker": marker,
    }

    if color_series is not None:
        if pd.api.types.is_numeric_dtype(color_series):
            scatter_norm = {}
            if color_min is not None:
                scatter_norm["vmin"] = color_min
            if color_max is not None:
                scatter_norm["vmax"] = color_max

            sc = ax.scatter(x, y, c=color_series, cmap="viridis", **scatter_kwargs, **scatter_norm)
            cbar = fig.colorbar(sc, ax=ax, pad=0.01)
            cbar.set_label(color_label or color_col, fontsize=axis_title_fontsize)

            cmin = float(color_min) if color_min is not None else float(color_series.min())
            cmax = float(color_max) if color_max is not None else float(color_series.max())
            if color_tick_step is not None and color_tick_step > 0:
                tick_locs = _build_even_ticks(cmin, cmax, color_tick_step)
            else:
                tick_locs = cbar.ax.get_yticks()
                tick_locs = tick_locs[(tick_locs > cmin) & (tick_locs < cmax)]
                tick_locs = np.sort(np.unique(np.concatenate(([cmin], tick_locs, [cmax]))))
            cbar.ax.set_yticks(tick_locs)
            cbar.ax.tick_params(labelsize=axis_fontsize, length=0)
            cbar.outline.set_linewidth(1.5)
            for tick_loc in tick_locs:
                cbar.ax.axhline(y=tick_loc, color="black", linewidth=1, linestyle="-")
        else:
            categories = color_series.fillna("n/a").astype(str)
            unique_categories = categories.unique()
            cmap = plt.cm.get_cmap("tab20", len(unique_categories))
            for index, category in enumerate(unique_categories):
                cat_mask = categories == category
                ax.scatter(x[cat_mask], y[cat_mask], color=cmap(index), label=category, **scatter_kwargs)
            ax.legend(title=color_label or color_col, fontsize=axis_fontsize * 0.8, title_fontsize=axis_title_fontsize)
    else:
        ax.scatter(x, y, color="#4B5BA9", **scatter_kwargs)

    ax.set_xlabel(_format_label_with_unit(x_label, x_unit), fontsize=axis_title_fontsize)
    ax.set_ylabel(_format_label_with_unit(y_label, y_unit), fontsize=axis_title_fontsize)
    ax.set_title(f"Scatter - {x_col} vs. {y_col}", fontsize=20, fontweight="bold", pad=20)
    ax.tick_params(axis="both", which="major", labelsize=axis_fontsize, length=0)
    ax.grid(True, linestyle="-", color="black", linewidth=1, alpha=1)

    if xlim:
        ax.set_xlim(left=xlim[0], right=xlim[1])
    if ylim:
        ax.set_ylim(bottom=ylim[0], top=ylim[1])

    x_min, x_max = ax.get_xlim() if xlim else (float(x.min()), float(x.max()))
    y_min, y_max = ax.get_ylim() if ylim else (float(y.min()), float(y.max()))
    format_axis_with_unit(
        ax.xaxis,
        x_unit or "",
        axis_fontsize,
        min_value=x_min,
        max_value=x_max,
        tick_step=x_tick_step,
        thousands_for_ints=True,
    )
    format_axis_with_unit(
        ax.yaxis,
        y_unit or "",
        axis_fontsize,
        min_value=y_min,
        max_value=y_max,
        tick_step=y_tick_step,
        thousands_for_ints=True,
    )
    ax.set_xlim(left=x_min, right=x_max)
    ax.set_ylim(bottom=y_min, top=y_max)

    for spine in ax.spines.values():
        spine.set_linewidth(1.5)

    fig.tight_layout()
    return fig


def plot_sum(
    df,
    file_boundaries,
    title,
    colors,
    figsize,
    line_width,
    axis_fontsize,
    axis_title_fontsize,
    xlim,
    ylim,
    x_unit,
    y_unit,
    x_label="Time t",
    y_label="Summed Value",
    x_tick_step=None,
    y_tick_step=None,
):
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=figsize)
    x_values = df.index.total_seconds() if isinstance(df.index, pd.TimedeltaIndex) else df.index

    ax.xaxis.grid(True, linestyle="-", color="black", linewidth=1, alpha=1)
    ax.yaxis.grid(True, linestyle="-", color="black", linewidth=1, alpha=1)

    color_list = [colors.get(col, "#CCCCCC") for col in df.columns] if isinstance(colors, dict) else colors
    ax.stackplot(x_values, df.T, colors=color_list, alpha=1, zorder=2)
    ax.legend(df.columns, loc="best", fontsize=axis_fontsize * 0.8)
    ax.set_title(title, fontsize=20, fontweight="bold", pad=20)
    ax.set_xlabel(x_label, fontsize=axis_title_fontsize)
    ax.set_ylabel(y_label, fontsize=axis_title_fontsize)
    ax.tick_params(axis="both", which="major", labelsize=axis_fontsize, length=0)

    x_left = xlim[0] if xlim else 0
    x_right = xlim[1] if xlim else (np.max(x_values) if len(x_values) else 0)
    ax.set_xlim(left=x_left, right=x_right)
    if ylim:
        y_bottom, y_top = ylim
        ax.set_ylim(bottom=y_bottom, top=y_top)
    else:
        y_bottom = 0
        ax.set_ylim(bottom=0)

    ax.margins(x=0, y=0)

    if len(x_values):
        boundaries_sec = [(fname, ts.total_seconds()) for fname, ts in file_boundaries]
        annotate_file_sections(ax, boundaries_sec, float(np.max(x_values)), annotation_fontsize=axis_fontsize)

    _, x_max = ax.get_xlim()
    _, y_max = ax.get_ylim()
    format_axis_with_unit(ax.xaxis, x_unit, axis_fontsize, min_value=x_left, max_value=x_max, tick_step=x_tick_step)
    format_axis_with_unit(ax.yaxis, y_unit, axis_fontsize, min_value=y_bottom, max_value=y_max, tick_step=y_tick_step)
    ax.set_xlim(left=x_left, right=x_right)
    ax.set_ylim(bottom=y_bottom, top=(y_top if ylim else ax.get_ylim()[1]))

    for spine in ax.spines.values():
        spine.set_linewidth(1.5)
    ax.set_xmargin(0)
    ax.set_ymargin(0)
    ax.autoscale(enable=False)
    fig.tight_layout()
    return fig


def plot_bar(
    df_by_file,
    components,
    title,
    label_rotation,
    colors,
    hide_x_labels,
    figsize,
    line_width,
    axis_fontsize,
    axis_title_fontsize,
    ylim,
    y_unit,
    bar_width=0.6,
    y_tick_step=None,
    y_label="Power P",
    x_label="",
):
    if not components or not df_by_file:
        return None

    fig, ax = plt.subplots(figsize=figsize)
    component_values = {component: [] for component in components}
    file_labels = [name.split(".")[0] for name in df_by_file.keys()]

    for _, df in df_by_file.items():
        for component in components:
            series = pd.to_numeric(df[component], errors="coerce") if component in df else pd.Series(dtype=float)
            value = float(series.mean())
            component_values[component].append(value if not np.isnan(value) else 0.0)

    n_files = len(file_labels)
    indices = np.arange(n_files)
    bottom = np.zeros(n_files)

    ax.yaxis.grid(True, linestyle="-", color="black", linewidth=1, alpha=1, zorder=0)

    for component in components:
        values = np.array(component_values[component])
        ax.bar(
            indices,
            values,
            width=float(bar_width),
            label=component,
            bottom=bottom,
            color=colors.get(component, "#CCCCCC"),
            edgecolor="black",
            linewidth=line_width,
            zorder=3,
        )
        bottom += values

    ax.set_title(title, fontsize=20, fontweight="bold", pad=20)
    ax.set_ylabel(y_label, fontsize=axis_title_fontsize)
    ax.set_xlabel(x_label, fontsize=axis_title_fontsize)
    ax.tick_params(axis="y", labelsize=axis_fontsize, length=0)
    ax.set_xticks(indices)
    ax.set_xticklabels(file_labels, rotation=label_rotation, ha="right" if label_rotation > 0 else "center")
    if hide_x_labels:
        ax.set_xticklabels([])
        ax.set_xlabel("")
    ax.tick_params(axis="x", length=0)
    ax.legend(loc="best")

    if ylim:
        y_bottom, y_top = ylim
        ax.set_ylim(bottom=y_bottom, top=y_top)
    else:
        max_y = bottom.max() if n_files else 0
        y_bottom = 0
        ax.set_ylim(bottom=0, top=max_y * 1.1 if max_y > 0 else 1)

    if n_files:
        width = float(bar_width)
        left_edge = indices[0] - width / 2.0
        right_edge = indices[-1] + width / 2.0
        pad = 0.6 * width
        ax.set_xlim(left=left_edge - pad, right=right_edge + pad)
    else:
        ax.set_xlim(-0.5, 0.5)

    ax.margins(x=0, y=0)
    _, y_max = ax.get_ylim()
    format_axis_with_unit(ax.yaxis, y_unit, axis_fontsize, min_value=y_bottom, max_value=y_max, tick_step=y_tick_step)
    ax.set_ylim(bottom=y_bottom, top=ax.get_ylim()[1])

    for spine in ax.spines.values():
        spine.set_linewidth(1.5)
    ax.set_xmargin(0)
    ax.set_ymargin(0)
    ax.autoscale(enable=False)
    fig.tight_layout()
    return fig


def plot_bar_evp(
    df_by_file,
    elec_components,
    pneu_components,
    title,
    label_rotation,
    colors,
    hide_x_labels,
    figsize,
    line_width,
    axis_fontsize,
    axis_title_fontsize,
    ylim,
    y_unit,
    bar_width=0.6,
    y_tick_step=None,
    y_label="Power P",
    x_label="",
):
    if not elec_components or not pneu_components or not df_by_file:
        return None

    fig, ax = plt.subplots(figsize=figsize)
    file_labels = [name.split(".")[0] for name in df_by_file.keys()]
    n_files = len(file_labels)
    indices = np.arange(n_files)
    width = bar_width

    ax.yaxis.grid(True, linestyle="-", color="black", linewidth=1, alpha=1, zorder=0)

    bottom_elec = np.zeros(n_files)
    for component in elec_components:
        values = []
        for df in df_by_file.values():
            series = pd.to_numeric(df[component], errors="coerce") if component in df else pd.Series(dtype=float)
            value = float(series.mean())
            values.append(value if not np.isnan(value) else 0.0)

        ax.bar(
            indices - width / 2,
            values,
            float(width),
            label=component,
            bottom=bottom_elec,
            color=colors.get(component, "#CCCCCC"),
            edgecolor="black",
            linewidth=line_width,
            zorder=3,
        )
        bottom_elec += np.array(values)

    bottom_pneu = np.zeros(n_files)
    for component in pneu_components:
        values = []
        for df in df_by_file.values():
            series = pd.to_numeric(df[component], errors="coerce") if component in df else pd.Series(dtype=float)
            value = float(series.mean())
            values.append(value if not np.isnan(value) else 0.0)

        ax.bar(
            indices + width / 2,
            values,
            float(width),
            label=component,
            bottom=bottom_pneu,
            color=colors.get(component, "#CCCCCC"),
            edgecolor="black",
            linewidth=line_width,
            zorder=3,
        )
        bottom_pneu += np.array(values)

    ax.set_title(title, fontsize=20, fontweight="bold", pad=20)
    ax.set_ylabel(y_label, fontsize=axis_title_fontsize)
    ax.set_xlabel(x_label, fontsize=axis_title_fontsize)
    ax.tick_params(axis="y", labelsize=axis_fontsize, length=0)
    ax.set_xticks(indices)
    ax.set_xticklabels(file_labels, rotation=label_rotation, ha="right" if label_rotation > 0 else "center")

    if hide_x_labels:
        ax.set_xticklabels([])
        ax.set_xlabel("")

    ax.tick_params(axis="x", length=0)
    ax.legend(loc="best")

    if ylim:
        y_bottom, y_top = ylim
        ax.set_ylim(bottom=y_bottom, top=y_top)
    else:
        max_y = max(bottom_elec.max(), bottom_pneu.max()) if n_files else 0
        y_bottom = 0
        ax.set_ylim(bottom=0, top=max_y * 1.1 if max_y > 0 else 1)

    if n_files:
        width_value = float(width)
        left_edge = indices[0] - width_value
        right_edge = indices[-1] + width_value
        pad = 0.6 * width_value
        ax.set_xlim(left=left_edge - pad, right=right_edge + pad)
    else:
        ax.set_xlim(-0.5, 0.5)

    ax.margins(x=0, y=0)
    _, y_max = ax.get_ylim()
    format_axis_with_unit(ax.yaxis, y_unit, axis_fontsize, min_value=y_bottom, max_value=y_max, tick_step=y_tick_step)
    ax.set_ylim(bottom=y_bottom, top=ax.get_ylim()[1])

    for spine in ax.spines.values():
        spine.set_linewidth(1.5)

    ax.set_xmargin(0)
    ax.set_ymargin(0)
    ax.autoscale(enable=False)
    fig.tight_layout()
    return fig


def plot_boxplot(
    df_by_file,
    components,
    title,
    figsize,
    axis_fontsize,
    axis_title_fontsize,
    colors,
    line_width,
    label_rotation,
    ylim,
    y_unit,
    legend_inside=False,
    y_tick_step=None,
    y_label="Power P",
    box_width: float = 0.8,
):
    if not components:
        return None

    fig, ax = plt.subplots(figsize=figsize)
    data_to_plot = []
    plot_components = []
    for component in components:
        interval_means = []
        for df in df_by_file.values():
            if component not in df:
                continue

            series = pd.to_numeric(df[component], errors="coerce")
            if series.empty:
                continue

            # Box plots should always reflect the average value per elapsed-time interval.
            interval_mean = series.groupby(level=0).mean().dropna()
            if not interval_mean.empty:
                interval_means.append(interval_mean.reset_index(drop=True))

        all_values = pd.concat(interval_means, ignore_index=True) if interval_means else pd.Series(dtype=float)
        if not all_values.empty:
            data_to_plot.append(all_values)
            plot_components.append(component)

    if not data_to_plot:
        return None

    box = ax.boxplot(
        data_to_plot,
        patch_artist=True,
        tick_labels=plot_components,
        flierprops=dict(marker="o"),
        widths=box_width,
    )

    if isinstance(colors, dict):
        box_colors_map = {component: colors.get(component, "#CCCCCC") for component in plot_components}
    else:
        box_colors_map = {component: colors[index % len(colors)] for index, component in enumerate(plot_components)}

    for index, patch in enumerate(box["boxes"]):
        component_name = plot_components[index]
        patch.set_facecolor(box_colors_map[component_name])
        patch.set_edgecolor("black")
        patch.set_linewidth(line_width)

    for flier in box["fliers"]:
        flier.set(marker="o", markerfacecolor="white", markeredgecolor="black", markersize=7, markeredgewidth=1)

    for element in ["whiskers", "caps", "medians"]:
        for line in box[element]:
            line.set_color("black")
            line.set_linewidth(line_width)
            if element == "whiskers":
                line.set_linestyle("--")

    ax.set_title(title, fontsize=20, fontweight="bold", pad=20)
    ax.set_ylabel(y_label, fontsize=axis_title_fontsize)
    ax.tick_params(axis="y", labelsize=axis_fontsize, length=0)
    ax.tick_params(axis="x", labelsize=axis_fontsize, which="major", length=0)
    plt.setp(ax.get_xticklabels(), rotation=label_rotation, ha="right", rotation_mode="anchor")
    ax.yaxis.grid(True, linestyle="-", color="black", linewidth=1, alpha=1)
    legend_patches = [mpatches.Patch(color=box_colors_map[component], label=component) for component in plot_components]
    ax.legend(handles=legend_patches, loc="best")

    if ylim:
        y_bottom, y_top = ylim
        ax.set_ylim(bottom=y_bottom, top=y_top)
    else:
        y_bottom = 0
        ax.set_ylim(bottom=0)

    ax.margins(x=0, y=0)
    _, y_max = ax.get_ylim()
    format_axis_with_unit(ax.yaxis, y_unit, axis_fontsize, min_value=y_bottom, max_value=y_max, tick_step=y_tick_step)

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.5)
        spine.set_edgecolor("black")

    ax.set_xmargin(0)
    ax.set_ymargin(0)
    ax.autoscale(enable=False)
    fig.tight_layout()
    return fig


def plot_histogram(
    series: pd.Series,
    title: str,
    figsize: tuple,
    axis_fontsize: int,
    axis_title_fontsize: int = 20,
    bins: int = 50,
    line_width: float = 1.5,
    color: str = "#4B5BA9",
    x_label: str = "Power P",
    y_label: str = "Percent",
    xlim: tuple | None = None,
    ylim: tuple | None = None,
    x_unit: str | None = None,
    y_unit: str | None = None,
    y_tick_step: float | None = None,
    x_tick_step: float | None = None,
    bin_edges: np.ndarray | None = None,
):
    if series.empty:
        return None

    fig, ax = plt.subplots(figsize=figsize)
    ax.yaxis.grid(True, linestyle="-", color="black", linewidth=1, alpha=1, zorder=0)
    ax.xaxis.grid(False)

    values = pd.to_numeric(series, errors="coerce").dropna().values
    if bin_edges is not None and len(bin_edges) >= 2:
        values = values[(values >= float(bin_edges[0])) & (values <= float(bin_edges[-1]))]
    n = len(values)
    hist_bins = bin_edges if bin_edges is not None else bins
    if n > 0:
        weights = np.ones(n) * (100.0 / n)
        ax.hist(values, bins=hist_bins, color=color, edgecolor="black", linewidth=line_width, weights=weights, zorder=3)
    else:
        ax.hist(values, bins=hist_bins, color=color, edgecolor="black", linewidth=line_width, zorder=3)

    ax.set_title(title, fontsize=20, fontweight="bold", pad=20)
    ax.set_xlabel(x_label, fontsize=axis_title_fontsize)
    ax.set_ylabel(y_label, fontsize=axis_title_fontsize)
    ax.tick_params(axis="both", which="major", labelsize=axis_fontsize, length=0)

    if xlim:
        ax.set_xlim(left=xlim[0], right=xlim[1])
    if ylim:
        ax.set_ylim(bottom=ylim[0], top=ylim[1])
    else:
        ax.set_ylim(bottom=0)

    ax.margins(x=0, y=0)
    x_min, x_max = ax.get_xlim()
    _, y_max = ax.get_ylim()
    format_axis_with_unit(ax.xaxis, x_unit or "", axis_fontsize, min_value=x_min, max_value=x_max, tick_step=x_tick_step)
    format_axis_with_unit(ax.yaxis, y_unit or "%", axis_fontsize, min_value=0, max_value=y_max, tick_step=y_tick_step)

    for spine in ax.spines.values():
        spine.set_linewidth(1.5)

    ax.set_xmargin(0)
    ax.set_ymargin(0)
    ax.autoscale(enable=False)
    fig.tight_layout()
    return fig


def _format_label_with_unit(label: str, unit: str | None) -> str:
    if unit:
        return f"{label} [{unit}]"
    return label


def _build_even_ticks(min_value: float, max_value: float, step: float) -> np.ndarray:
    if step <= 0:
        return np.array([min_value, max_value])

    ticks = np.arange(min_value, max_value + step, step)
    if len(ticks) == 0 or not np.isclose(ticks[-1], max_value):
        ticks = np.append(ticks, max_value)
    if not np.isclose(ticks[0], min_value):
        ticks = np.insert(ticks, 0, min_value)
    return np.sort(np.unique(ticks))


def _unit_to_kw_factor(unit: str | None) -> float:
    if not unit:
        return 1.0
    normalized = unit.strip().lower()
    if normalized in {"w", "watt", "watts"}:
        return 0.001
    if normalized in {"kw", "kilowatt", "kilowatts"}:
        return 1.0
    return 1.0


def plot_donut(
    combined_df: pd.DataFrame,
    components: list[str],
    colors: dict[str, str] | None,
    hole: float,
    label_mode: str,
    total_target_kw: float,
    show_others: bool,
    chart_size_px: int,
    title: str,
    axis_fontsize: int,
    show_legend: bool,
    source_unit: str | None = "W",
) -> plt.Figure | None:
    if not components or combined_df.empty:
        return None

    colors = colors or {}
    valid_components: list[str] = []
    values_kw: list[float] = []

    for component in components:
        if component not in combined_df.columns:
            continue
        series = pd.to_numeric(combined_df[component], errors="coerce")
        mean_value = float(series.mean(skipna=True)) if not series.empty else float("nan")
        if np.isnan(mean_value):
            continue
        mean_value = max(mean_value, 0.0)
        if mean_value == 0.0:
            continue
        valid_components.append(component)
        values_kw.append(mean_value)

    if not values_kw:
        return None

    conversion_factor = _unit_to_kw_factor(source_unit)
    values_kw = [value * conversion_factor for value in values_kw]
    base_total = sum(values_kw)
    if base_total <= 0:
        return None

    hole = float(np.clip(hole, 0.0, 0.95))
    wedge_width = max(0.01, 1.0 - hole)

    scale_factor = 1.0
    others_value = 0.0
    total_target_kw = float(total_target_kw)
    if total_target_kw > 0:
        if show_others and total_target_kw > base_total:
            others_value = total_target_kw - base_total
        else:
            scale_factor = total_target_kw / base_total

    scaled_values = [value * scale_factor for value in values_kw]

    entries: list[tuple[str, float, str]] = []
    color_cycle = plt.rcParams.get("axes.prop_cycle", None)
    color_list = color_cycle.by_key().get("color", []) if color_cycle else []

    for index, (component, value) in enumerate(zip(valid_components, scaled_values)):
        if value <= 0:
            continue
        color = colors.get(component)
        if not color:
            color = color_list[index % len(color_list)] if color_list else f"C{index}"
        entries.append((component, value, color))

    if show_others and others_value > 0:
        entries.append(("Others", others_value, colors.get("Others", "#888888")))

    if not entries:
        return None

    labels = [label for label, _, _ in entries]
    values = [value for _, value, _ in entries]
    slice_colors = [color for _, _, color in entries]
    total_sum = sum(values)
    if total_sum <= 0:
        return None

    figsize_in = max(chart_size_px, 300) / 100.0
    fig, ax = plt.subplots(figsize=(figsize_in, figsize_in))

    def _format_autopct(pct: float) -> str:
        if (label_mode or "").strip().lower() == "kw":
            absolute = pct * total_sum / 100.0
            return f"{absolute:.1f} kW" if absolute >= 10 else f"{absolute:.2f} kW"
        return f"{pct:.1f}%"

    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        startangle=90,
        colors=slice_colors,
        autopct=_format_autopct,
        pctdistance=0.75 if hole < 0.05 else (0.85 - hole * 0.5),
        textprops={"fontsize": axis_fontsize},
        wedgeprops={"width": wedge_width, "edgecolor": "white", "linewidth": 1.5},
    )

    ax.set_title(title, fontsize=20, fontweight="bold", pad=20)
    ax.axis("equal")

    for text in texts:
        text.set_fontsize(axis_fontsize)
    for autotext in autotexts:
        autotext.set_fontsize(axis_fontsize)

    if show_legend:
        ax.legend(
            wedges,
            labels,
            loc="center left",
            bbox_to_anchor=(1.0, 0.5),
            fontsize=axis_fontsize,
            frameon=False,
        )

    fig.tight_layout()
    return fig


def plot_sankey_energy_flow(
    df: pd.DataFrame,
    selected_electric: list,
    selected_pneumatic: list,
    productive_vars: list,
    figsize: tuple,
    axis_fontsize: int,
    title: str = "Sankey Diagram: Total Power -> Electric/Pneumatic -> Productive/Unproductive",
    colors: dict | None = None,
    unit: str = "W",
):
    """Create a data-driven Sankey diagram based on selected components."""
    try:
        import plotly.graph_objects as go
    except Exception:
        return None

    if df is None or df.empty:
        return None

    def get_value(series: pd.Series) -> float:
        numeric = pd.to_numeric(series, errors="coerce").dropna()
        if numeric.empty:
            return 0.0
        return float(numeric.mean())

    def hex_to_rgba(color_hex: str, alpha: float = 0.6) -> str:
        try:
            color_hex = color_hex.lstrip("#")
            if len(color_hex) == 3:
                color_hex = "".join([char * 2 for char in color_hex])
            red = int(color_hex[0:2], 16)
            green = int(color_hex[2:4], 16)
            blue = int(color_hex[4:6], 16)
            return f"rgba({red},{green},{blue},{alpha})"
        except Exception:
            return f"rgba(0,0,0,{alpha})"

    selected_electric = [column for column in selected_electric if column in df.columns]
    selected_pneumatic = [column for column in selected_pneumatic if column in df.columns]
    selected_vars = list(selected_electric) + list(selected_pneumatic)
    if not selected_vars:
        return None

    nodes = ["Total Power", "Electric", "Pneumatic"] + selected_electric + selected_pneumatic + ["Productive", "Unproductive"]
    index_by_node = {node: index for index, node in enumerate(nodes)}

    link_source, link_target, link_value, link_color = [], [], [], []

    sum_electric = sum(get_value(df[var]) for var in selected_electric)
    sum_pneumatic = sum(get_value(df[var]) for var in selected_pneumatic)

    colors = colors or {}
    group_color_electric = colors.get("Electric") or colors.get("Elektrisch") or "#4B5BA9"
    group_color_pneumatic = colors.get("Pneumatic") or colors.get("Pneumatisch") or "#01A579"

    if sum_electric > 0:
        link_source.append(index_by_node["Total Power"])
        link_target.append(index_by_node["Electric"])
        link_value.append(sum_electric)
        link_color.append(hex_to_rgba(group_color_electric, 0.6))
    if sum_pneumatic > 0:
        link_source.append(index_by_node["Total Power"])
        link_target.append(index_by_node["Pneumatic"])
        link_value.append(sum_pneumatic)
        link_color.append(hex_to_rgba(group_color_pneumatic, 0.6))

    for var in selected_electric:
        value = get_value(df[var])
        if value > 0:
            link_source.append(index_by_node["Electric"])
            link_target.append(index_by_node[var])
            link_value.append(value)
            link_color.append(hex_to_rgba(colors.get(var, group_color_electric), 0.6))

    for var in selected_pneumatic:
        value = get_value(df[var])
        if value > 0:
            link_source.append(index_by_node["Pneumatic"])
            link_target.append(index_by_node[var])
            link_value.append(value)
            link_color.append(hex_to_rgba(colors.get(var, group_color_pneumatic), 0.6))

    productive_set = set(productive_vars)
    for var in selected_vars:
        value = get_value(df[var])
        if value <= 0:
            continue
        if var in productive_set:
            link_source.append(index_by_node[var])
            link_target.append(index_by_node["Productive"])
            link_value.append(value)
            link_color.append(hex_to_rgba(colors.get(var, group_color_electric if var in selected_electric else group_color_pneumatic), 0.8))
        else:
            link_source.append(index_by_node[var])
            link_target.append(index_by_node["Unproductive"])
            link_value.append(value)
            link_color.append(hex_to_rgba(colors.get(var, group_color_electric if var in selected_electric else group_color_pneumatic), 0.3))

    px_width = int(max(300, figsize[0] * 80))
    px_height = int(max(300, figsize[1] * 80))

    node_values: dict[str, float] = {node: 0.0 for node in nodes}
    node_values["Electric"] = sum_electric
    node_values["Pneumatic"] = sum_pneumatic
    node_values["Total Power"] = sum_electric + sum_pneumatic

    productive_total = 0.0
    unproductive_total = 0.0
    for var in selected_vars:
        value = get_value(df[var])
        node_values[var] = value
        if var in productive_set:
            productive_total += value
        else:
            unproductive_total += value
    node_values["Productive"] = productive_total
    node_values["Unproductive"] = unproductive_total

    def _fmt(value: float) -> str:
        if value >= 1000:
            return f"{value:,.0f}".replace(",", " ")
        if np.isclose(value, round(value)):
            return f"{int(round(value))}"
        return f"{value:.2f}".rstrip("0").rstrip(".")

    node_labels = [f"{node}<br>{_fmt(node_values.get(node, 0.0))} {unit}" for node in nodes]

    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=15,
                    thickness=14,
                    line=dict(color="rgba(0,0,0,0)", width=0),
                    label=node_labels,
                    color=["rgba(0,0,0,0)"] * len(nodes),
                ),
                link=dict(
                    source=link_source,
                    target=link_target,
                    value=link_value,
                    color=link_color,
                ),
            )
        ]
    )

    fig.update_layout(
        title=title,
        width=px_width,
        height=px_height,
        font=dict(size=axis_fontsize),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    return fig
