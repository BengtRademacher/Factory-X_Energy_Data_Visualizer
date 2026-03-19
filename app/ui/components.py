from __future__ import annotations

from dataclasses import dataclass
from html import escape
import re

import streamlit as st

from app.config import COLOR_PALETTE, DEFAULT_COLORS


_CUSTOM_COLOR_LABEL = "Custom..."
_HEX_PATTERN = re.compile(r"^#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$")


@dataclass(frozen=True, slots=True)
class ColorTarget:
    """Describes one target in the shared color selector."""

    id: str
    label: str
    default_color: str


def get_valid_multiselect_state(key: str, options: list[str]) -> list[str]:
    """Trim stored multiselect values to the currently valid options."""
    current = st.session_state.get(key, [])
    if not isinstance(current, list):
        current = list(current) if current else []

    valid = [value for value in current if value in options]
    if valid != current:
        st.session_state[key] = valid
    return valid


def get_valid_selectbox_state(key: str, options: list[str], fallback: str) -> str:
    """Ensure a selectbox state value is still valid."""
    current = st.session_state.get(key, fallback)
    if current not in options:
        st.session_state[key] = fallback
        return fallback
    return current


def build_color_targets(labels: list[str], start_index: int = 0) -> list[ColorTarget]:
    """Build color targets with stable palette defaults."""
    return [
        ColorTarget(
            id=label,
            label=label,
            default_color=DEFAULT_COLORS[(start_index + index) % len(DEFAULT_COLORS)],
        )
        for index, label in enumerate(labels)
    ]


def render_component_color_section(
    section_key: str,
    targets: list[ColorTarget],
    title: str = "Colors",
    expanded: bool = False,
) -> dict[str, str]:
    """Render a complete color configuration section."""
    storage_key = f"{section_key}_colors"
    existing_colors = st.session_state.get(storage_key, {})
    if not isinstance(existing_colors, dict):
        existing_colors = {}

    active_target_ids = {target.id for target in targets}
    active_colors = {
        target_id: _normalize_hex_color(color, DEFAULT_COLORS[0])
        for target_id, color in existing_colors.items()
        if target_id in active_target_ids
    }

    _remove_stale_color_state(section_key, active_target_ids, existing_colors.keys())

    if not targets:
        st.session_state[storage_key] = active_colors
        return active_colors

    section_colors: dict[str, str] = {}
    with st.expander(title, expanded=expanded, icon=":material/palette:"):
        for target in targets:
            widget_key = _widget_color_key(section_key, target.id)

            if widget_key not in st.session_state and target.id in active_colors:
                st.session_state[widget_key] = active_colors[target.id]

            color = render_color_selector(
                target_id=target.id,
                label=target.label,
                default_color=target.default_color,
                state_key=widget_key,
            )
            section_colors[target.id] = color

    st.session_state[storage_key] = section_colors
    return section_colors


def render_panel_header(
    title: str,
    description: str | None = None,
    *,
    eyebrow: str | None = None,
    metrics: list[tuple[str, object]] | None = None,
) -> None:
    """Render a stylized section header with optional KPI chips."""
    title_html = escape(title)
    description_html = (
        f'<p class="fx-panel-copy">{escape(description)}</p>'
        if description
        else ""
    )
    eyebrow_html = f'<div class="fx-panel-eyebrow">{escape(eyebrow)}</div>' if eyebrow else ""
    metrics_html = _build_metric_chips_markup(metrics)

    st.markdown(
        (
            '<div class="fx-panel-header">'
            f"{eyebrow_html}"
            f'<div class="fx-panel-title">{title_html}</div>'
            f"{description_html}"
            f"{metrics_html}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_group_intro(
    title: str,
    description: str,
    *,
    variant: str = "default",
) -> None:
    """Render a compact intro block for grouped controls."""
    class_name = "fx-sidebar-group"
    if variant == "advanced":
        class_name += " fx-sidebar-group--advanced"

    st.markdown(
        (
            f'<div class="{class_name}">'
            f'<div class="fx-sidebar-group-title">{escape(title)}</div>'
            f'<p class="fx-sidebar-group-copy">{escape(description)}</p>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_color_selector(
    target_id: str,
    label: str,
    default_color: str,
    state_key: str | None = None,
) -> str:
    """Render a single shared color selector.

    Also supports the legacy call signature
    ``render_color_selector(label, key, default_color)`` for backward compatibility.
    """
    if state_key is None:
        state_key = label
        label = target_id

    normalized_default = _normalize_hex_color(default_color, DEFAULT_COLORS[0])
    current_color = _normalize_hex_color(st.session_state.get(state_key, normalized_default), normalized_default)

    hex_to_name = {value.lower(): name for name, value in COLOR_PALETTE.items()}
    option_map = {f"\u25a0 {name}": name for name in COLOR_PALETTE}
    custom_option = f"\u25a0 {_CUSTOM_COLOR_LABEL}"
    options = list(option_map.keys()) + [custom_option]

    selected_name = hex_to_name.get(current_color.lower())
    inferred_option = custom_option if selected_name is None else f"\u25a0 {selected_name}"
    option_key = _widget_option_key(state_key)
    if st.session_state.get(option_key) not in options:
        st.session_state[option_key] = inferred_option

    selected_option = st.selectbox(label, options=options, key=option_key)

    if selected_option == custom_option:
        picker_key = _widget_picker_key(state_key)
        if picker_key not in st.session_state:
            st.session_state[picker_key] = current_color

        color = st.color_picker("Custom color", value=current_color, key=picker_key)
        display_label = f"{label} ({_CUSTOM_COLOR_LABEL})"
    else:
        palette_name = option_map[selected_option]
        color = COLOR_PALETTE[palette_name]
        st.session_state[state_key] = color
        st.session_state[_widget_picker_key(state_key)] = color
        display_label = f"{label} ({palette_name})"

    normalized_color = _normalize_hex_color(color, normalized_default)
    st.session_state[state_key] = normalized_color
    _render_color_preview(target_id=target_id, label=display_label, hex_color=normalized_color)
    return normalized_color


def _remove_stale_color_state(
    section_key: str,
    active_target_ids: set[str],
    existing_target_ids,
) -> None:
    """Remove color state for targets that are no longer active."""
    for target_id in existing_target_ids:
        if target_id in active_target_ids:
            continue
        widget_key = _widget_color_key(section_key, target_id)
        st.session_state.pop(widget_key, None)
        st.session_state.pop(_widget_option_key(widget_key), None)
        st.session_state.pop(_widget_picker_key(widget_key), None)


def _widget_color_key(section_key: str, target_id: str) -> str:
    """Build the session-state key for a color selection."""
    return f"{section_key}_color_{target_id}"


def _widget_option_key(state_key: str) -> str:
    """Build the session-state key for the palette dropdown."""
    return f"sel_{state_key}"


def _widget_picker_key(state_key: str) -> str:
    """Build the session-state key for the custom color picker."""
    return f"picker_{state_key}"


def _render_color_preview(target_id: str, label: str, hex_color: str) -> None:
    """Render a readable preview swatch for the current color."""
    text_color = _get_contrast_text_color(hex_color)
    st.markdown(
        (
            f'<div data-testid="color-preview-{_sanitize_html_attr(target_id)}" '
            f'style="background:{hex_color}; color:{text_color}; padding:0.65rem 0.8rem; '
            "border-radius:0.6rem; margin:0.35rem 0 1rem 0; "
            'box-shadow: inset 0 0 0 1px rgba(0,0,0,0.12); font-weight:600;">'
            f"{label}<br><span style=\"font-size:0.85rem; font-weight:500;\">{hex_color}</span>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def _get_contrast_text_color(hex_color: str) -> str:
    """Choose black or white based on perceived brightness."""
    normalized = _normalize_hex_color(hex_color, "#000000").lstrip("#")
    red = int(normalized[0:2], 16)
    green = int(normalized[2:4], 16)
    blue = int(normalized[4:6], 16)
    luminance = (0.299 * red) + (0.587 * green) + (0.114 * blue)
    return "#000000" if luminance >= 186 else "#FFFFFF"


def _normalize_hex_color(color: str | None, fallback: str) -> str:
    """Normalize hex colors to #RRGGBB."""
    fallback_color = fallback if isinstance(fallback, str) else DEFAULT_COLORS[0]
    fallback_normalized = fallback_color.upper() if _HEX_PATTERN.match(fallback_color) else DEFAULT_COLORS[0]

    if not isinstance(color, str):
        return fallback_normalized

    candidate = color.strip()
    if not _HEX_PATTERN.match(candidate):
        return fallback_normalized

    if len(candidate) == 4:
        candidate = "#" + "".join(character * 2 for character in candidate[1:])

    return candidate.upper()


def _sanitize_html_attr(value: str) -> str:
    """Normalize arbitrary ids for HTML attribute usage."""
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", value)


def _build_metric_chips_markup(metrics: list[tuple[str, object]] | None) -> str:
    """Build HTML for one KPI chip row."""
    if not metrics:
        return ""

    chips: list[str] = []
    for label, value in metrics:
        if value is None or value == "":
            continue
        chips.append(
            '<span class="fx-kpi-chip">'
            f'<span class="fx-kpi-chip__label">{escape(str(label))}</span>'
            f'<span class="fx-kpi-chip__value">{escape(str(value))}</span>'
            "</span>"
        )

    if not chips:
        return ""

    return f'<div class="fx-kpi-row">{"".join(chips)}</div>'
