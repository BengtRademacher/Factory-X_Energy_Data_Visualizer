# Matplotlib Default Parameters by Plot Type

This document captures every directive the plotting layer applies so another
agent can reproduce the exact visuals without reading the Python source.

## Global Configuration (applies to all matplotlib figures)

| Setting | Value | Source |
| ------- | ----- | ------ |
| `plt.rcParams['font.family']` | `['Aptos', 'Segoe UI', 'sans-serif']` | top-level of `app/plotting.py` |
| `mpl.rcParams['pdf.fonttype']` | `3` normally, overridden to `42` only during export | `export.reset_font_for_display()` / `set_font_for_export()` |
| `mpl.rcParams['ps.fonttype']` | `3` normally, `42` during export | same as above |
| `mpl.rcParams['svg.fonttype']` | `'path'` normally, `'none'` during export | same as above |

All figures returned by the plotting helpers:

- call `fig, ax = plt.subplots(figsize=context.dimensions.to_tuple())`.
- set every spine linewidth to `1.5` and `ax.autoscale(enable=False)`.
- enforce `ax.set_xmargin(0)` and `ax.set_ymargin(0)`.

Two shared helpers influence axis layout:

1. `format_axis_with_unit(axis_obj, unit_str, axis_fontsize, min_value, max_value, tick_step, thousands_for_ints)`
   - If `tick_step` is provided, ticks are generated with `np.arange(min, max, tick_step)` and the bounds are forced into the array. Otherwise, existing ticks are snapped so first tick equals `min_value` and last equals `max_value`.
   - Formatter logic renders the penultimate tick as the unit label and every other tick with either an integer (no thousands separators unless `thousands_for_ints=True`) or `f"{value:.2f}"` stripped of trailing zeros.
   - Tick label font size is set to `axis_fontsize`.
2. `annotate_file_sections(ax, boundaries, total_duration, annotation_fontsize)`
   - Draws vertical dashed lines (`linestyle='--'`, `color='grey'`, `linewidth=1`) at file boundaries and labels the midpoint with a white rounded box. Y position is 3% below the top of current y-limits.

`DataManager.sum_categories` returns a `TimedeltaIndex`; all plots expecting elapsed time convert that index to seconds using `.dt.total_seconds()`.

## Line Plots (`plot_line`)

Inputs:
- `combined_df`: must contain numeric columns for each component.
- `x_values`: resolved numeric X-axis values shared across the selected files.
- `file_boundaries`: list of `(filename: str, start_time: pd.Timedelta)` pairs.
- `components`: ordered list of column names.
- `colors`: dict mapping component → hex color; default fallback `'#333333'` per series.
- Context arguments derived from UI (`PlotContext`).

Styling steps:
- X data uses the resolved `x_values` series provided by the UI layer.
- Each component plotted using `ax.plot(time_sec, series.fillna(0), linewidth=context.style.line_width)`.
- Title and axis labels set to UI values (`fontsize=20`, title uses `fontweight='bold'`, `pad=20`).
- Grid lines: `ax.yaxis.grid(True, linestyle='-', color='black', linewidth=1, alpha=1)` and identical for x-axis.
- Legend placed below the chart with `bbox_to_anchor=(0.5, -0.15)`.
- X-limits: `(0 if no manual limit else provided, max time or manual value)`.
- Y-limits: `(0 or provided manual bounds)`.
- After formatting, `annotate_file_sections` called with boundary seconds.
- Tick formatting uses UI-provided `x_unit`, `y_unit`, `x_tick_step`, `y_tick_step`, and `thousands_for_ints=True` for both axes.

## Stacked Area Plots (`plot_sum`)

Inputs:
- `df`: index must be `TimedeltaIndex` or numeric; columns represent stacked categories.
- `file_boundaries`: same structure as line plots.
- `colors`: map column → color (if omitted, defaults to `'#CCCCCC'`).

Styling steps:
- Index converted to seconds if `TimedeltaIndex`.
- Y and X grid drawn before plotting.
- `ax.stackplot(x_values, df.T, colors=color_list, alpha=1, zorder=2)`.
- Legend uses `ax.legend(df.columns, loc='best', fontsize=context.style.axis_fontsize * 0.8)`.
- Axis titles/labels identical to line plots.
- X/Y limits computed same as line plots.
- `annotate_file_sections` executed when data available.
- Tick formatting identical to line plots but without thousands formatting on y-axis unless `thousands_for_ints` argument is set by caller (currently `False`).

## Bar Charts (`plot_bar`)

Inputs:
- `df_by_file`: mapping `filename -> DataFrame` indexed by `elapsedTime` (Timedelta) with numeric component columns.
- `components`: ordered list of columns to include.
- `colors`: dict component → color (fallback `'#CCCCCC'`).
- Additional layout options from UI (label rotation, bar width, hide labels).

Styling steps:
- For each file, values aggregated using `mean()` and stacked (running `bottom` array).
- Bars drawn via `ax.bar(indices, values, width=bar_width, bottom=bottom, edgecolor='black', linewidth=context.style.line_width, zorder=3)`.
- Y-grid enabled before plotting, x-grid disabled.
- X ticks set to filenames stripped of extension, rotated according to UI. Optionally hidden.
- Y-limit: `0` to `max(bottom) * 1.1` when no manual override. X-limits padded by `0.6 * bar_width` on both sides (or ±0.5 when no data).
- Tick formatter for y-axis uses UI `y_unit`, `y_tick_step`.
- Legend auto-placed.

## Split Bar Charts (`plot_bar_evp`)

Same base configuration as stacked bars, with two passes:
- Electric components drawn centered at `indices - width/2`; pneumatic at `indices + width/2`.
- Aggregation uses the mean value per file.
- Separate running totals ensure stacked appearance within each electric/pneumatic group.
- Axes cleanup identical to `plot_bar`.

## Box Plots (`plot_boxplot`)

Inputs:
- `df_by_file`: same structure as bar charts.
- `components`: ordered list of columns; values concatenated across all files.
- `colors`: either dict component → color or list cycle.
- `legend_inside`: currently always `True` in calls.
- `box_width`: UI slider (default `0.8`).

Styling steps:
- Data concatenated via `pd.concat([...], ignore_index=True).dropna()` per component.
- `ax.boxplot(..., patch_artist=True, labels=plot_components, flierprops=dict(marker='o'), widths=box_width)`.
- Box faces filled with component color; edge color black, linewidth `context.style.line_width`.
- Whiskers/caps/medians colored black, whiskers dashed.
- Fliers: white face, black edge, marker size 7, edge width 1.
- Legend built from `matplotlib.patches.Patch` for each component (always shown, `loc='best'`).
- Y-grid enabled; axis labels and rotation like other plots.
- Y-limits default to `[0, current ylim upper]` if not provided.
- Tick formatting uses `format_axis_with_unit` on y-axis only.

## Histograms (`plot_histogram`)

Inputs:
- `series`: numeric `pd.Series`.
- `bins`: default `50`.
- `color`: defaults to `'#4B5BA9'`.
- Axis/label info from UI.

Styling steps:
- Remove `NaN` before plotting.
- If at least one value, compute weights = `np.ones(n) * (100.0 / n)` to show percentages; otherwise call `hist` without weights.
- Bars use black edge, linewidth = `line_width` argument (default `1.5`).
- Title and labels as usual.
- Y-grid enabled; x-grid disabled.
- X-limits set only if provided, Y-limit forced to start at zero when not provided.
- Tick formatting: x-axis uses provided unit (if any) with optional tick step; y-axis uses `'%'` default unit and optional tick step.

## Matplotlib Sankey (`plot_sankey`)

Inputs:
- `title`, `flows`, `labels`, `orientations`, `figsize`, `axis_fontsize`.
- Creates `Sankey(ax=ax, unit=None, format='%.2f')` and reuses default rcParams.
- After `sankey.finish()`, all spines set to linewidth `1.5` and axis is disabled via `ax.set_axis_off()`.
- `fig.tight_layout()` executed.

## Plotly Sankey (`plot_sankey_energy_flow`)

Inputs:
- `df`: combined dataframe with component columns.
- `selected_electric`, `selected_pneumatic`, `productive_vars`, `figsize`, `axis_fontsize`, `title`, `colors`, `unit`.

Derived settings:
- Figure pixel size: `width = max(300, figsize[0] * 80)`, `height = max(300, figsize[1] * 80)`.
- Node labels built as `f"{name}<br>{value formatted} {unit}"`.
- Link colors: convert hex (or fallback) to RGBA using helper with alpha `0.6` for group flows, `0.8` for productive, `0.3` for unproductive.
- Layout margins: `dict(l=10, r=10, t=30, b=10)`.
- Font: `dict(size=axis_fontsize)`.
- `arrangement='snap'`, node thickness `14`, padding `15`, node border transparent.

## Usage Blueprint

To reproduce any plot:
1. Ensure `plt.rcParams['font.family'] = 'Arial'` and the export overrides when required (only for written files).
2. Collect UI outputs (`plot_width`, `plot_height`, axis labels, units, tick steps, component colors) from `setup_sidebar()`.
3. Prepare component color mappings exactly as used in the UI (hex strings), ordering matters for deterministic legends.
4. Apply the steps described above for the specific plot helper, including grid configuration, limit handling, tick formatting, file annotations, and legend placement.

Following this recipe reproduces the on-screen charts and exported assets byte-for-byte (differences only arise if Matplotlib/Plotly versions diverge from the pinned requirements).

