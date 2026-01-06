import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from matplotlib.ticker import FuncFormatter

plt.rcParams['font.family'] = 'Arial'

def format_axis_with_unit(axis_obj, unit_str, axis_fontsize, min_value=None, max_value=None, tick_step=None, thousands_for_ints=False):
    """
    Setzt optional feste Major-Ticks (inkl. max als letztem Tick) und
    einen Formatter, der die vorletzte Tick-Position als Einheit anzeigt
    und alle anderen Ticks numerisch formatiert. Keine manuellen set_ticklabels.
    """
    # Optional feste Ticks setzen, damit letzter Tick sicher das Maximum ist
    if min_value is not None and max_value is not None:
        if max_value < min_value:
            min_value, max_value = max_value, min_value
        if tick_step and tick_step > 0:
            # Handle negative ranges
            if min_value < 0:
                ticks = np.arange(min_value, max_value + tick_step, tick_step)
            else:
                ticks = np.arange(min_value, max_value, tick_step)
            if len(ticks) == 0 or not np.isclose(ticks[-1], max_value):
                ticks = np.append(ticks, max_value)
            # Stelle sicher, dass min_value enthalten ist
            if not any(np.isclose(ticks, min_value)):
                ticks = np.insert(ticks, 0, min_value)
            axis_obj.set_ticks(ticks)
        else:
            # Bestehende Ticks holen, dann auf exakte Grenzen pinnen
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
        # Einheit als vorletzter Tick, letzter Tick immer numerisch
        ticks = axis_obj.get_ticklocs()
        if len(ticks) >= 2 and np.isclose(value, ticks[-2]) and unit_str:
            return unit_str
        # Bevorzugt ganzzahlige Darstellung, sonst kompakt ohne unnötige Nachkommastellen
        # Handle negatives properly
        rounded = np.round(value)
        if np.isclose(value, rounded):
            if thousands_for_ints:
                return f"{int(rounded):,}".replace(",", ".")
            return str(int(rounded))
        return f"{value:.2f}".rstrip('0').rstrip('.')

    axis_obj.set_major_formatter(FuncFormatter(_format_tick))
    axis_obj.set_tick_params(labelsize=axis_fontsize)


def annotate_file_sections(ax, boundaries, total_duration, annotation_fontsize):
    """Zeichnet Trennlinien und Dateinamen-Annotationen in den Plot."""
    if len(boundaries) <= 1:
        return
    ylim = ax.get_ylim()
    for i, (filename, start_time) in enumerate(boundaries):
        # Vertikale Trennlinie
        if i > 0:
            ax.axvline(x=start_time, linestyle='--', color='grey', linewidth=1)
        # Annotation für den Dateinamen
        next_time = boundaries[i + 1][1] if i + 1 < len(boundaries) else total_duration
        mid_point = start_time + (next_time - start_time) / 2
        # Platziere den Text leicht unterhalb der oberen Grenze
        y_text = ylim[1] - (ylim[1] - ylim[0]) * 0.03
        ax.text(mid_point, y_text, f"  {filename.split('.')[0]}  ", 
                ha='center', va='top', fontsize=annotation_fontsize, 
                bbox=dict(boxstyle="round,pad=0.3,rounding_size=2", fc="white", ec="none", alpha=1.0))
    ax.set_ylim(ylim)


def plot_line(
    combined_df,
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
    x_label="Zeit t",
    y_label="Leistung P",
    secondary_components=None,
    secondary_colors=None,
    secondary_y_unit=None,
    secondary_y_label="Sekundärwert",
    secondary_y_tick_step=None,
    secondary_ylim=None,
):
    if not components or combined_df.empty:
        return None  # Handled in main with st.info
    fig, ax = plt.subplots(figsize=figsize)
    
    # X-Achse in Sekunden umwandeln, damit Matplotlib korrekt arbeiten kann
    time_sec = combined_df['elapsedTime'].dt.total_seconds()
    legend_handles = []
    legend_labels = []
    for component in components:
        if component in combined_df.columns:
            line = ax.plot(
                time_sec,
                combined_df[component].fillna(0),
                label=component,
                color=colors.get(component, '#333333'),
                linewidth=line_width,
            )
            legend_handles.extend(line)
            legend_labels.append(component)

    ax.set_title(title, fontsize=20, fontweight='bold', pad=20)
    ax.set_xlabel(x_label, fontsize=axis_title_fontsize)
    ax.set_ylabel(y_label, fontsize=axis_title_fontsize)
    ax.tick_params(axis='both', which='major', labelsize=axis_fontsize, length=0)
    
    # Legende außerhalb des Plots platzieren
    # (Legende final nach sekundärer Achse setzen)

    ax.yaxis.grid(True, linestyle='-', color='black', linewidth=1, alpha=1)
    ax.xaxis.grid(True, linestyle='-', color='black', linewidth=1, alpha=1)
    
    # Achsengrenzen setzen und am (manuellen oder 0-)Ursprung verankern
    x_left = xlim[0] if xlim else 0
    x_right = xlim[1] if xlim else time_sec.max()
    ax.set_xlim(left=x_left, right=x_right)
    if ylim:
        y_bottom, y_top = ylim[0], ylim[1]
        ax.set_ylim(bottom=y_bottom, top=y_top)
    else:
        y_bottom = 0
        ax.set_ylim(bottom=0)

    # Keine zusätzlichen Ränder
    ax.margins(x=0, y=0)

    # Grenzen ebenfalls in Sekunden umrechnen für die Trennlinien
    boundaries_sec = [(fname, ts.total_seconds()) for fname, ts in file_boundaries]
    annotate_file_sections(ax, boundaries_sec, time_sec.max(), annotation_fontsize=axis_fontsize)
    
    # Formatierung inkl. fester Ticks: vorletzter Tick = Einheit, letzter = Zahl
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
    # Nach dem Setzen der Ticks die Grenzen erneut fixieren
    ax.set_xlim(left=x_left, right=x_right)
    if ylim:
        ax.set_ylim(bottom=y_bottom, top=y_top)
    else:
        ax.set_ylim(bottom=0)
    
    secondary_components = secondary_components or []
    if secondary_components:
        ax2 = ax.twinx()
        secondary_colors = secondary_colors or {}
        first_color = secondary_colors.get(secondary_components[0], '#999999') if secondary_components else '#999999'
        for component in secondary_components:
            if component in combined_df.columns:
                line = ax2.plot(
                    time_sec,
                    combined_df[component].fillna(0),
                    label=component,
                    color=secondary_colors.get(component, '#999999'),
                    linewidth=line_width,
                    linestyle='--',
                )
                legend_handles.extend(line)
                legend_labels.append(component)
        ax2.set_ylabel(secondary_y_label, fontsize=axis_title_fontsize, color=first_color)
        ax2.tick_params(axis='y', which='major', labelsize=axis_fontsize, length=0, colors=first_color)
        if secondary_ylim and len(secondary_ylim) == 2:
            secondary_y_bottom, secondary_y_max = secondary_ylim
            ax2.set_ylim(secondary_y_bottom, secondary_y_max)
        else:
            y2_limits = ax2.get_ylim()
            secondary_y_bottom, secondary_y_max = y2_limits[0], y2_limits[1]
        format_axis_with_unit(
            ax2.yaxis,
            secondary_y_unit or '',
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
    else:
        ax2 = None

    if legend_handles:
        ax.legend(legend_handles, legend_labels, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=max(1, min(3, len(legend_labels))))

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
    x_unit: str | None,
    y_unit: str | None,
    color_label: str | None,
):
    if df.empty or x_col not in df or y_col not in df:
        return None

    x = pd.to_numeric(df[x_col], errors='coerce')
    y = pd.to_numeric(df[y_col], errors='coerce')
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
        "edgecolors": 'black' if edge_width > 0 else 'none',
    }

    if color_series is not None:
        if pd.api.types.is_numeric_dtype(color_series):
            sc = ax.scatter(x, y, c=color_series, cmap='viridis', **scatter_kwargs)
            cbar = fig.colorbar(sc, ax=ax, pad=0.01)
            cbar.set_label(color_label or color_col, fontsize=axis_title_fontsize)
            
            # Ticks sicherstellen: Min und Max beschriften
            cmin, cmax = float(color_series.min()), float(color_series.max())
            tick_locs = cbar.ax.get_yticks()
            # Filter ticks to be within range and include min/max
            tick_locs = tick_locs[(tick_locs > cmin) & (tick_locs < cmax)]
            tick_locs = np.sort(np.unique(np.concatenate(([cmin], tick_locs, [cmax]))))
            cbar.ax.set_yticks(tick_locs)
            
            cbar.ax.tick_params(labelsize=axis_fontsize, length=0)
            
            # Colorbar styling: 1.5pt border and horizontal lines at tick positions
            cbar.outline.set_linewidth(1.5)
            for tick_loc in tick_locs:
                cbar.ax.axhline(y=tick_loc, color='black', linewidth=1, linestyle='-')
        else:
            categories = color_series.fillna("n/a").astype(str)
            unique_categories = categories.unique()
            cmap = plt.cm.get_cmap('tab20', len(unique_categories))
            for idx, category in enumerate(unique_categories):
                cat_mask = categories == category
                ax.scatter(x[cat_mask], y[cat_mask], color=cmap(idx), label=category, **scatter_kwargs)
            ax.legend(title=color_label or color_col, fontsize=axis_fontsize * 0.8, title_fontsize=axis_title_fontsize)
    else:
        ax.scatter(x, y, color='#4B5BA9', **scatter_kwargs)

    ax.set_xlabel(x_col if x_unit is None else f"{x_col} [{x_unit}]", fontsize=axis_title_fontsize)
    ax.set_ylabel(y_col if y_unit is None else f"{y_col} [{y_unit}]", fontsize=axis_title_fontsize)
    ax.set_title(f"Scatter – {x_col} vs. {y_col}", fontsize=20, fontweight='bold', pad=20)
    ax.tick_params(axis='both', which='major', labelsize=axis_fontsize, length=0)
    
    # Grid: 1pt black
    ax.grid(True, linestyle='-', color='black', linewidth=1, alpha=1)

    x_min, x_max = float(x.min()), float(x.max())
    y_min, y_max = float(y.min()), float(y.max())
    format_axis_with_unit(ax.xaxis, x_unit or '', axis_fontsize, min_value=x_min, max_value=x_max, thousands_for_ints=True)
    format_axis_with_unit(ax.yaxis, y_unit or '', axis_fontsize, min_value=y_min, max_value=y_max, thousands_for_ints=True)

    for spine in ax.spines.values():
        spine.set_linewidth(1.5)

    fig.tight_layout()
    return fig

def plot_sum(df, file_boundaries, title, colors, figsize, line_width, axis_fontsize, axis_title_fontsize, xlim, ylim, x_unit, y_unit, x_label="Zeit t", y_label="Summierter Wert", x_tick_step=None, y_tick_step=None):
    if df.empty:
        return None
    fig, ax = plt.subplots(figsize=figsize)

    # X-Achse in Sekunden (oder numerisch) umwandeln, falls TimedeltaIndex
    if isinstance(df.index, pd.TimedeltaIndex):
        x_values = df.index.total_seconds()  # type: ignore
    else:
        x_values = df.index

    # Grid VOR den Flächen zeichnen, damit diese obenauf liegen
    ax.xaxis.grid(True, linestyle='-', color='black', linewidth=1, alpha=1)
    ax.yaxis.grid(True, linestyle='-', color='black', linewidth=1, alpha=1)

    color_list = [colors.get(col, '#CCCCCC') for col in df.columns] if isinstance(colors, dict) else colors
    ax.stackplot(x_values, df.T, colors=color_list, alpha=1, zorder=2)
    ax.legend(df.columns, loc='best', fontsize=axis_fontsize * 0.8)
    ax.set_title(title, fontsize=20, fontweight='bold', pad=20)
    ax.set_xlabel(x_label, fontsize=axis_title_fontsize)
    ax.set_ylabel(y_label, fontsize=axis_title_fontsize)
    ax.tick_params(axis='both', which='major', labelsize=axis_fontsize, length=0)

    # Achsengrenzen setzen und am (manuellen oder 0-)Ursprung verankern
    x_left = xlim[0] if xlim else 0
    x_right = xlim[1] if xlim else (np.max(x_values) if len(x_values) else 0)
    ax.set_xlim(left=x_left, right=x_right)
    if ylim:
        y_bottom, y_top = ylim[0], ylim[1]
        ax.set_ylim(bottom=y_bottom, top=y_top)
    else:
        y_bottom = 0
        ax.set_ylim(bottom=0)

    ax.margins(x=0, y=0)

    # Grenzen und Annotationen wie im Linienplot
    if len(x_values):
        boundaries_sec = [(fname, ts.total_seconds()) for fname, ts in file_boundaries]
        annotate_file_sections(ax, boundaries_sec, float(np.max(x_values)), annotation_fontsize=axis_fontsize)

    # Ticks und Formatter
    _, x_max = ax.get_xlim()
    _, y_max = ax.get_ylim()
    format_axis_with_unit(ax.xaxis, x_unit, axis_fontsize, min_value=x_left, max_value=x_max, tick_step=x_tick_step)
    format_axis_with_unit(ax.yaxis, y_unit, axis_fontsize, min_value=y_bottom, max_value=y_max, tick_step=y_tick_step)
    ax.set_xlim(left=x_left, right=x_right)
    if ylim:
        ax.set_ylim(bottom=y_bottom, top=y_top)
    else:
        ax.set_ylim(bottom=0)

    for spine in ax.spines.values():
        spine.set_linewidth(1.5)
    ax.set_xmargin(0)
    ax.set_ymargin(0)
    ax.autoscale(enable=False)
    fig.tight_layout()
    return fig

def plot_bar(df_by_file, components, title, mode, label_rotation, colors, hide_x_labels, figsize, line_width, axis_fontsize, axis_title_fontsize, ylim, y_unit, bar_width=0.6, y_tick_step=None, y_label="Leistung P", x_label=""):
    if not components or not df_by_file:
        return None
    fig, ax = plt.subplots(figsize=figsize)
    component_values = {comp: [] for comp in components}
    file_labels = [name.split('.')[0] for name in df_by_file.keys()]

    for filename, df in df_by_file.items():
        for comp in components:
            val = df[comp].sum() if mode == 'Summe' else df[comp].mean()
            component_values[comp].append(val)
    
    n_files = len(file_labels)
    indices = np.arange(n_files)
    bottom = np.zeros(n_files)

    # Gitternetz zuerst zeichnen
    ax.yaxis.grid(True, linestyle='-', color='black', linewidth=1, alpha=1, zorder=0)

    for comp in components:
        values = np.array(component_values[comp])
        ax.bar(indices, values, width=float(bar_width), label=comp, bottom=bottom, 
               color=colors.get(comp, '#CCCCCC'), edgecolor='black', linewidth=line_width, zorder=3)
        bottom += values

    ax.set_title(title, fontsize=20, fontweight='bold', pad=20)
    ax.set_ylabel(y_label, fontsize=axis_title_fontsize)
    ax.set_xlabel(x_label, fontsize=axis_title_fontsize)
    ax.tick_params(axis='y', labelsize=axis_fontsize, length=0)
    ax.set_xticks(indices)
    ax.set_xticklabels(file_labels, rotation=label_rotation, ha='right' if label_rotation > 0 else 'center')
    if hide_x_labels:
        ax.set_xticklabels([])
        ax.set_xlabel("")
    ax.tick_params(axis='x', length=0)
    ax.legend(loc='best')
    
    # Achsengrenzen setzen und am (manuellen oder 0-)Ursprung verankern
    if ylim:
        y_bottom, y_top = ylim[0], ylim[1]
        ax.set_ylim(bottom=y_bottom, top=y_top)
    else:
        # Setze das Y-Limit auf das Maximum der gestapelten Säulen
        max_y = bottom.max() if n_files else 0
        y_bottom = 0
        ax.set_ylim(bottom=0, top=max_y * 1.1 if max_y > 0 else 1)

    # X-Grenzen so setzen, dass außen 0.6 Säulenbreiten Platz bleibt
    if n_files:
        _w = float(bar_width)
        left_edge = indices[0] - _w / 2.0
        right_edge = indices[-1] + _w / 2.0
        pad = 0.6 * _w
        ax.set_xlim(left=left_edge - pad, right=right_edge + pad)
    else:
        ax.set_xlim(-0.5, 0.5)

    ax.margins(x=0, y=0)

    # Y-Ticks und Formatter festlegen
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

def plot_bar_evp(df_by_file, elec_components, pneu_components, title, mode, label_rotation, colors, hide_x_labels, figsize, line_width, axis_fontsize, axis_title_fontsize, ylim, y_unit, bar_width=0.6, y_tick_step=None, y_label="Leistung P", x_label=""):
    if not elec_components or not pneu_components or not df_by_file:
        return None
    fig, ax = plt.subplots(figsize=figsize)
    
    file_labels = [name.split('.')[0] for name in df_by_file.keys()]
    n_files = len(file_labels)
    indices = np.arange(n_files)
    width = bar_width

    ax.yaxis.grid(True, linestyle='-', color='black', linewidth=1, alpha=1, zorder=0)

    # Elektrische Komponenten plotten
    bottom_elec = np.zeros(n_files)
    for comp in elec_components:
        values = []
        for df in df_by_file.values():
            val = df[comp].sum() if mode == 'Summe' else df[comp].mean()
            values.append(val)
        
        ax.bar(indices - width/2, values, float(width), label=comp, bottom=bottom_elec,
               color=colors.get(comp, '#CCCCCC'), edgecolor='black', linewidth=line_width, zorder=3)
        bottom_elec += np.array(values)

    # Pneumatische Komponenten plotten
    bottom_pneu = np.zeros(n_files)
    for comp in pneu_components:
        values = []
        for df in df_by_file.values():
            val = df[comp].sum() if mode == 'Summe' else df[comp].mean()
            values.append(val)

        ax.bar(indices + width/2, values, float(width), label=comp, bottom=bottom_pneu,
               color=colors.get(comp, '#CCCCCC'), edgecolor='black', linewidth=line_width, zorder=3)
        bottom_pneu += np.array(values)

    ax.set_title(title, fontsize=20, fontweight='bold', pad=20)
    ax.set_ylabel(y_label, fontsize=axis_title_fontsize)
    ax.set_xlabel(x_label, fontsize=axis_title_fontsize)
    ax.tick_params(axis='y', labelsize=axis_fontsize, length=0)
    ax.set_xticks(indices)
    ax.set_xticklabels(file_labels, rotation=label_rotation, ha='right' if label_rotation > 0 else 'center')

    if hide_x_labels:
        ax.set_xticklabels([])
        ax.set_xlabel("")

    ax.tick_params(axis='x', length=0)
    ax.legend(loc='best')
    
    # Achsengrenzen setzen und am (manuellen oder 0-)Ursprung verankern
    if ylim:
        y_bottom, y_top = ylim[0], ylim[1]
        ax.set_ylim(bottom=y_bottom, top=y_top)
    else:
        # Setze das Y-Limit auf das Maximum der gestapelten Säulen
        max_y = max(bottom_elec.max(), bottom_pneu.max()) if n_files else 0
        y_bottom = 0
        ax.set_ylim(bottom=0, top=max_y * 1.1 if max_y > 0 else 1)
        
    # X-Grenzen so setzen, dass außen 0.6 Säulenbreiten Platz bleibt
    if n_files:
        _w = float(width)
        left_edge = indices[0] - _w
        right_edge = indices[-1] + _w
        pad = 0.6 * _w
        ax.set_xlim(left=left_edge - pad, right=right_edge + pad)
    else:
        ax.set_xlim(-0.5, 0.5)

    ax.margins(x=0, y=0)

    # Y-Ticks und Formatter festlegen
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


def plot_boxplot(df_by_file, components, title, figsize, axis_fontsize, axis_title_fontsize, colors, line_width, label_rotation, ylim, y_unit, legend_inside=False, y_tick_step=None, y_label="Leistung P", box_width: float = 0.8):
    if not components:
        return None
    fig, ax = plt.subplots(figsize=figsize)
    
    data_to_plot = []
    plot_components = []
    for component in components:
        all_values = pd.concat([df[component] for df in df_by_file.values() if component in df], ignore_index=True).dropna()
        if not all_values.empty:
            data_to_plot.append(all_values)
            plot_components.append(component)

    if not data_to_plot: return None

    box = ax.boxplot(data_to_plot, patch_artist=True, labels=plot_components, flierprops=dict(marker='o'), widths=box_width)  # type: ignore[arg-type]
    
    # Farben zuweisen
    if isinstance(colors, dict):
        box_colors_map = {comp: colors.get(comp, '#CCCCCC') for comp in plot_components}
    else:
        box_colors_map = {comp: colors[i % len(colors)] for i, comp in enumerate(plot_components)}

    for i, patch in enumerate(box['boxes']):
        comp_name = plot_components[i]
        patch.set_facecolor(box_colors_map[comp_name])
        patch.set_edgecolor('black')
        patch.set_linewidth(line_width)

    for i, flier in enumerate(box['fliers']):
        flier.set(marker='o', markerfacecolor='white', markeredgecolor='black', markersize=7, markeredgewidth=1)
        
    for element in ['whiskers', 'caps', 'medians']:
        for line in box[element]:
            line.set_color('black')
            line.set_linewidth(line_width)
            if element == 'whiskers': line.set_linestyle('--')
    
    ax.set_title(title, fontsize=20, fontweight='bold', pad=20)
    ax.set_ylabel(y_label, fontsize=axis_title_fontsize)
    ax.tick_params(axis='y', labelsize=axis_fontsize, length=0)
    ax.tick_params(axis='x', labelsize=axis_fontsize, which='major', length=0)
    plt.setp(ax.get_xticklabels(), rotation=label_rotation, ha="right", rotation_mode="anchor")
    ax.yaxis.grid(True, linestyle='-', color='black', linewidth=1, alpha=1)
    legend_patches = [mpatches.Patch(color=box_colors_map[comp], label=comp) for comp in plot_components]
    
    # Legende standardmäßig im Plot
    ax.legend(handles=legend_patches, loc='best')
    
    # Achsengrenzen setzen und am (manuellen oder 0-)Ursprung verankern
    if ylim:
        y_bottom, y_top = ylim[0], ylim[1]
        ax.set_ylim(bottom=y_bottom, top=y_top)
    else:
        y_bottom = 0
        ax.set_ylim(bottom=0)

    ax.margins(x=0, y=0)

    # Y-Ticks und Formatter festlegen
    _, y_max = ax.get_ylim()
    format_axis_with_unit(ax.yaxis, y_unit, axis_fontsize, min_value=y_bottom, max_value=y_max, tick_step=y_tick_step)

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.5)
        spine.set_edgecolor('black')
    
    ax.set_xmargin(0)
    ax.set_ymargin(0)
    ax.autoscale(enable=False)
    fig.tight_layout()
    return fig 

def plot_histogram(series: pd.Series,
                   title: str,
                   figsize: tuple,
                   axis_fontsize: int,
                   axis_title_fontsize: int = 20,
                   bins: int = 50,
                   line_width: float = 1.5,
                   color: str = "#4B5BA9",
                   x_label: str = "Leistung P",
                   y_label: str = "Prozent",
                   xlim: tuple | None = None,
                   ylim: tuple | None = None,
                   x_unit: str | None = None,
                   y_unit: str | None = None,
                   y_tick_step: float | None = None,
                   x_tick_step: float | None = None):
    if series.empty:
        return None
    fig, ax = plt.subplots(figsize=figsize)
    
    # Grid BEFORE bars so bars are in foreground
    ax.yaxis.grid(True, linestyle='-', color='black', linewidth=1, alpha=1, zorder=0)
    ax.xaxis.grid(False)
    
    values = pd.to_numeric(series, errors="coerce").dropna().values
    n = len(values)
    if n > 0:
        weights = np.ones(n) * (100.0 / n)
        ax.hist(values, bins=bins, color=color, edgecolor='black', linewidth=line_width, weights=weights, zorder=3)
    else:
        ax.hist(values, bins=bins, color=color, edgecolor='black', linewidth=line_width, zorder=3)
    ax.set_title(title, fontsize=20, fontweight='bold', pad=20)
    ax.set_xlabel(x_label, fontsize=axis_title_fontsize)
    ax.set_ylabel(y_label, fontsize=axis_title_fontsize)
    ax.tick_params(axis='both', which='major', labelsize=axis_fontsize, length=0)

    if xlim:
        ax.set_xlim(left=xlim[0], right=xlim[1])
    if ylim:
        ax.set_ylim(bottom=ylim[0], top=ylim[1])
    else:
        ax.set_ylim(bottom=0)

    ax.margins(x=0, y=0)
    # Achsenformatierung (X optional, Y in Prozent)
    x_min, x_max = ax.get_xlim()
    _, y_max = ax.get_ylim()
    format_axis_with_unit(ax.xaxis, x_unit or '', axis_fontsize, min_value=x_min, max_value=x_max, tick_step=x_tick_step)
    format_axis_with_unit(ax.yaxis, y_unit or '%', axis_fontsize, min_value=0, max_value=y_max, tick_step=y_tick_step)

    for spine in ax.spines.values():
        spine.set_linewidth(1.5)

    ax.set_xmargin(0)
    ax.set_ymargin(0)
    ax.autoscale(enable=False)
    fig.tight_layout()
    return fig


def _unit_to_kw_factor(unit: str | None) -> float:
    if not unit:
        return 1.0
    normalized = unit.strip().lower()
    if normalized in {"w", "watt", "watts"}:
        return 0.001
    if normalized in {"kw", "kilowatt", "kilowatts"}:
        return 1.0
    return 1.0


def plot_donut(combined_df: pd.DataFrame,
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
               source_unit: str | None = "W") -> plt.Figure | None:
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
    color_cycle = plt.rcParams.get('axes.prop_cycle', None)
    color_list = color_cycle.by_key().get('color', []) if color_cycle else []

    for idx, (component, value) in enumerate(zip(valid_components, scaled_values)):
        if value <= 0:
            continue
        color = colors.get(component)
        if not color:
            if color_list:
                color = color_list[idx % len(color_list)]
            else:
                color = f"C{idx}"
        entries.append((component, value, color))

    if show_others and others_value > 0:
        other_color = colors.get("Others", "#888888")
        entries.append(("Others", others_value, other_color))

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
        if label_mode.lower() == "kw":
            absolute = pct * total_sum / 100.0
            if absolute >= 10:
                return f"{absolute:.1f} kW"
            return f"{absolute:.2f} kW"
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

    ax.set_title(title, fontsize=20, fontweight='bold', pad=20)
    ax.axis('equal')

    for text in texts:
        text.set_fontsize(axis_fontsize)
    for autotext in autotexts:
        autotext.set_fontsize(axis_fontsize)

    if show_legend:
        ax.legend(
            wedges,
            labels,
            loc='center left',
            bbox_to_anchor=(1.0, 0.5),
            fontsize=axis_fontsize,
            frameon=False,
        )

    fig.tight_layout()
    return fig

def plot_sankey_energy_flow(df: pd.DataFrame,
                            selected_elektrisch: list,
                            selected_pneumatisch: list,
                            productive_vars: list,
                            mode: str,
                            figsize: tuple,
                            axis_fontsize: int,
                            title: str = "Sankey-Diagramm: Gesamtleistung → Elektrisch/Pneumatisch → Produktiv/Unproduktiv",
                            colors: dict | None = None,
                            unit: str = "W"):
    """Erstellt ein datengetriebenes Sankey-Diagramm (Plotly) basierend auf den ausgewählten Komponenten.

    - mode: "Summe" oder "Durchschnitt"
    - figsize: (Breite, Höhe) in Zoll; wird auf Pixel (ca. 80 DPI) gemappt
    - axis_fontsize: globale Schriftgröße
    """
    try:
        import plotly.graph_objects as go  # lokal importieren, um harte Abhängigkeit zu vermeiden
    except Exception:
        return None

    if df is None or df.empty:
        return None

    def get_value(series: pd.Series) -> float:
        # Nur Mittelwert nutzen (Anforderung)
        return float(series.mean())

    def hex_to_rgba(color_hex: str, alpha: float = 0.6) -> str:
        try:
            color_hex = color_hex.lstrip('#')
            if len(color_hex) == 3:
                color_hex = ''.join([c*2 for c in color_hex])
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16)
            b = int(color_hex[4:6], 16)
            return f"rgba({r},{g},{b},{alpha})"
        except Exception:
            return f"rgba(0,0,0,{alpha})"

    selected_elektrisch = [c for c in selected_elektrisch if c in df.columns]
    selected_pneumatisch = [c for c in selected_pneumatisch if c in df.columns]
    selected_vars = list(selected_elektrisch) + list(selected_pneumatisch)

    if len(selected_vars) == 0:
        return None

    nodes = [
        "Gesamtleistung", "Elektrisch", "Pneumatisch"
    ] + selected_elektrisch + selected_pneumatisch + [
        "Produktiv", "Unproduktiv"
    ]
    idx = {node: i for i, node in enumerate(nodes)}

    links_source, links_target, links_value, links_color = [], [], [], []

    sum_elektrisch = sum([get_value(df[var]) for var in selected_elektrisch])
    sum_pneumatisch = sum([get_value(df[var]) for var in selected_pneumatisch])

    # Farben bestimmen
    colors = colors or {}
    group_color_elec = colors.get("Elektrisch", "#4B5BA9")
    group_color_pneu = colors.get("Pneumatisch", "#01A579")

    if sum_elektrisch > 0:
        links_source.append(idx["Gesamtleistung"]) ; links_target.append(idx["Elektrisch"]) ; links_value.append(sum_elektrisch)
        links_color.append(hex_to_rgba(group_color_elec, 0.6))
    if sum_pneumatisch > 0:
        links_source.append(idx["Gesamtleistung"]) ; links_target.append(idx["Pneumatisch"]) ; links_value.append(sum_pneumatisch)
        links_color.append(hex_to_rgba(group_color_pneu, 0.6))

    # Elektrisch → Einzelkomponenten
    for var in selected_elektrisch:
        val = get_value(df[var])
        if val > 0:
            links_source.append(idx["Elektrisch"]) ; links_target.append(idx[var]) ; links_value.append(val)
            links_color.append(hex_to_rgba(colors.get(var, group_color_elec), 0.6))

    # Pneumatisch → Einzelkomponenten
    for var in selected_pneumatisch:
        val = get_value(df[var])
        if val > 0:
            links_source.append(idx["Pneumatisch"]) ; links_target.append(idx[var]) ; links_value.append(val)
            links_color.append(hex_to_rgba(colors.get(var, group_color_pneu), 0.6))

    # Einzelkomponenten → Produktiv/Unproduktiv
    productive_set = set(productive_vars)
    for var in selected_vars:
        val = get_value(df[var])
        if val <= 0:
            continue
        if var in productive_set:
            links_source.append(idx[var]) ; links_target.append(idx["Produktiv"]) ; links_value.append(val)
            # Produktiv: gleiche Farbe wie Komponente, etwas deckender
            links_color.append(hex_to_rgba(colors.get(var, group_color_elec if var in selected_elektrisch else group_color_pneu), 0.8))
        else:
            links_source.append(idx[var]) ; links_target.append(idx["Unproduktiv"]) ; links_value.append(val)
            # Unproduktiv: gleiche Farbe wie Komponente, aber transparenter
            links_color.append(hex_to_rgba(colors.get(var, group_color_elec if var in selected_elektrisch else group_color_pneu), 0.3))

    px_width = int(max(300, figsize[0] * 80))
    px_height = int(max(300, figsize[1] * 80))

    # Knotenwerte (für Labels)
    node_values: dict[str, float] = {n: 0.0 for n in nodes}
    node_values["Elektrisch"] = sum_elektrisch
    node_values["Pneumatisch"] = sum_pneumatisch
    node_values["Gesamtleistung"] = sum_elektrisch + sum_pneumatisch
    productive_set = set(productive_vars)
    prod_total = 0.0
    unprod_total = 0.0
    for var in selected_elektrisch + selected_pneumatisch:
        v = get_value(df[var])
        node_values[var] = v
        if var in productive_set:
            prod_total += v
        else:
            unprod_total += v
    node_values["Produktiv"] = prod_total
    node_values["Unproduktiv"] = unprod_total

    # Labels mit Zeile darunter: Wert + Einheit
    def _fmt(v: float) -> str:
        if v >= 1000:
            return f"{v:,.0f}".replace(",", " ")
        if np.isclose(v, round(v)):
            return f"{int(round(v))}"
        return f"{v:.2f}".rstrip('0').rstrip('.')

    node_labels = [f"{n}<br>{_fmt(node_values.get(n, 0.0))} {unit}" for n in nodes]

    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            pad=15,
            thickness=14,
            line=dict(color="rgba(0,0,0,0)", width=0),
            label=node_labels,
            color=["rgba(0,0,0,0)"] * len(nodes),
        ),
        link=dict(
            source=links_source,
            target=links_target,
            value=links_value,
            color=links_color,
        ),
    )])

    fig.update_layout(
        title=title,
        width=px_width,
        height=px_height,
        font=dict(size=axis_fontsize),
        margin=dict(l=10, r=10, t=30, b=10),
    )

    return fig

from app.plotting import *


