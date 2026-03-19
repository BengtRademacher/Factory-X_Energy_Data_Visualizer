"""Plotly chart functions."""

from __future__ import annotations

import numpy as np
import pandas as pd


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
    component_means: pd.Series | None = None,
):
    """Create a data-driven Sankey diagram based on selected components."""
    try:
        import plotly.graph_objects as go
    except Exception:
        return None

    if component_means is None and (df is None or df.empty):
        return None

    def get_value(column_name: str) -> float:
        if component_means is not None:
            return float(component_means.get(column_name, 0.0) or 0.0)
        numeric = pd.to_numeric(df[column_name], errors="coerce").dropna()
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

    available_columns = set(component_means.index) if component_means is not None else set(df.columns)
    selected_electric = [column for column in selected_electric if column in available_columns]
    selected_pneumatic = [column for column in selected_pneumatic if column in available_columns]
    selected_vars = list(selected_electric) + list(selected_pneumatic)
    if not selected_vars:
        return None

    nodes = ["Total Power", "Electric", "Pneumatic"] + selected_electric + selected_pneumatic + ["Productive", "Unproductive"]
    index_by_node = {node: index for index, node in enumerate(nodes)}

    link_source, link_target, link_value, link_color = [], [], [], []

    sum_electric = sum(get_value(var) for var in selected_electric)
    sum_pneumatic = sum(get_value(var) for var in selected_pneumatic)

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
        value = get_value(var)
        if value > 0:
            link_source.append(index_by_node["Electric"])
            link_target.append(index_by_node[var])
            link_value.append(value)
            link_color.append(hex_to_rgba(colors.get(var, group_color_electric), 0.6))

    for var in selected_pneumatic:
        value = get_value(var)
        if value > 0:
            link_source.append(index_by_node["Pneumatic"])
            link_target.append(index_by_node[var])
            link_value.append(value)
            link_color.append(hex_to_rgba(colors.get(var, group_color_pneumatic), 0.6))

    productive_set = set(productive_vars)
    for var in selected_vars:
        value = get_value(var)
        if value <= 0:
            continue
        default_color = group_color_electric if var in selected_electric else group_color_pneumatic
        if var in productive_set:
            link_source.append(index_by_node[var])
            link_target.append(index_by_node["Productive"])
            link_value.append(value)
            link_color.append(hex_to_rgba(colors.get(var, default_color), 0.8))
        else:
            link_source.append(index_by_node[var])
            link_target.append(index_by_node["Unproductive"])
            link_value.append(value)
            link_color.append(hex_to_rgba(colors.get(var, default_color), 0.3))

    px_width = int(max(300, figsize[0] * 80))
    px_height = int(max(300, figsize[1] * 80))

    node_values: dict[str, float] = {node: 0.0 for node in nodes}
    node_values["Electric"] = sum_electric
    node_values["Pneumatic"] = sum_pneumatic
    node_values["Total Power"] = sum_electric + sum_pneumatic

    productive_total = 0.0
    unproductive_total = 0.0
    for var in selected_vars:
        value = get_value(var)
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

