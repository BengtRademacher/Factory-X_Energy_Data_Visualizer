from __future__ import annotations

import inspect
from contextlib import nullcontext
from types import SimpleNamespace

import pandas as pd
import streamlit as st

from app.ui import components
from app.ui.components import (
    ColorTarget,
    _render_color_preview,
    render_color_selector,
    render_component_color_section,
)
from app.ui.tabs import bar_plots, box_plots, donut_plots, histogram_plots, line_plots, sankey_plots, scatter_plots


def setup_function() -> None:
    st.session_state.clear()


def _install_streamlit_stubs(monkeypatch) -> None:
    def fake_selectbox(label, options, key, **kwargs):
        value = st.session_state.get(key, options[0])
        st.session_state[key] = value
        return value

    def fake_color_picker(label, value, key, **kwargs):
        selected = st.session_state.get(key, value)
        st.session_state[key] = selected
        return selected

    monkeypatch.setattr(components.st, "selectbox", fake_selectbox)
    monkeypatch.setattr(components.st, "color_picker", fake_color_picker)
    monkeypatch.setattr(components.st, "markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr(components.st, "expander", lambda *args, **kwargs: nullcontext())


def _install_line_plot_stubs(monkeypatch):
    recorded: dict[str, list] = {
        "checkboxes": [],
        "containers": [],
        "multiselects": [],
        "text_inputs": [],
        "number_inputs": [],
        "captions": [],
        "warnings": [],
        "color_sections": [],
    }

    class DummyContext:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class DummyColumn:
        def number_input(self, label, key, **kwargs):
            recorded["number_inputs"].append((label, key, kwargs))
            value = st.session_state.get(key, kwargs.get("value", 0.0))
            st.session_state[key] = value
            return value

        def text_input(self, label, key, **kwargs):
            recorded["text_inputs"].append((label, key, kwargs))
            value = st.session_state.get(key, kwargs.get("value", ""))
            st.session_state[key] = value
            return value

    def fake_checkbox(label, key, **kwargs):
        recorded["checkboxes"].append((label, key, kwargs))
        value = st.session_state.get(key, False)
        st.session_state[key] = value
        return value

    def fake_container(**kwargs):
        recorded["containers"].append(kwargs)
        return DummyContext()

    def fake_multiselect(label, options, default, key, **kwargs):
        recorded["multiselects"].append((label, list(options), list(default), key, kwargs))
        value = st.session_state.get(key, default)
        st.session_state[key] = value
        return value

    def fake_text_input(label, key, **kwargs):
        recorded["text_inputs"].append((label, key, kwargs))
        value = st.session_state.get(key, kwargs.get("value", ""))
        st.session_state[key] = value
        return value

    def fake_number_input(label, key, **kwargs):
        recorded["number_inputs"].append((label, key, kwargs))
        value = st.session_state.get(key, kwargs.get("value", 0.0))
        st.session_state[key] = value
        return value

    def fake_columns(spec):
        count = spec if isinstance(spec, int) else len(spec)
        return [DummyColumn() for _ in range(count)]

    def fake_caption(text, **kwargs):
        recorded["captions"].append((text, kwargs))

    def fake_warning(message, **kwargs):
        recorded["warnings"].append((message, kwargs))

    def fake_color_section(section_key, targets, title="Colors", expanded=False):
        target_labels = [target.label for target in targets]
        recorded["color_sections"].append((section_key, target_labels, title, expanded))
        return {target.id: target.default_color for target in targets}

    monkeypatch.setattr(line_plots.st, "checkbox", fake_checkbox)
    monkeypatch.setattr(line_plots.st, "container", fake_container)
    monkeypatch.setattr(line_plots.st, "multiselect", fake_multiselect)
    monkeypatch.setattr(line_plots.st, "text_input", fake_text_input)
    monkeypatch.setattr(line_plots.st, "number_input", fake_number_input)
    monkeypatch.setattr(line_plots.st, "columns", fake_columns)
    monkeypatch.setattr(line_plots.st, "caption", fake_caption)
    monkeypatch.setattr(line_plots.st, "warning", fake_warning)
    monkeypatch.setattr(line_plots, "render_component_color_section", fake_color_section)

    return SimpleNamespace(**recorded)


def test_render_color_selector_resolves_palette_color(monkeypatch):
    _install_streamlit_stubs(monkeypatch)
    st.session_state["sel_line_color_motor"] = "\u25a0 Purple"

    color = render_color_selector(
        target_id="motor",
        label="Motor",
        default_color="#006DB9",
        state_key="line_color_motor",
    )

    assert color == "#4B5BA9"
    assert st.session_state["line_color_motor"] == "#4B5BA9"


def test_render_color_selector_keeps_custom_color(monkeypatch):
    _install_streamlit_stubs(monkeypatch)
    st.session_state["sel_line_color_motor"] = "\u25a0 Custom..."
    st.session_state["line_color_motor"] = "#123abc"

    color = render_color_selector(
        target_id="motor",
        label="Motor",
        default_color="#006DB9",
        state_key="line_color_motor",
    )

    assert color == "#123ABC"
    assert st.session_state["line_color_motor"] == "#123ABC"


def test_render_color_selector_supports_legacy_call_signature(monkeypatch):
    _install_streamlit_stubs(monkeypatch)
    st.session_state["sel_line_color_motor"] = "\u25a0 Purple"

    color = render_color_selector("Motor", "line_color_motor", "#006DB9")

    assert color == "#4B5BA9"
    assert st.session_state["line_color_motor"] == "#4B5BA9"


def test_render_color_preview_uses_contrast_text(monkeypatch):
    captured: list[str] = []
    monkeypatch.setattr(components.st, "markdown", lambda html, **kwargs: captured.append(html))

    _render_color_preview(target_id="motor", label="Motor", hex_color="#FFFFFF")
    _render_color_preview(target_id="motor", label="Motor", hex_color="#003366")

    assert "color:#000000" in captured[0]
    assert "color:#FFFFFF" in captured[1]


def test_render_component_color_section_removes_stale_entries(monkeypatch):
    _install_streamlit_stubs(monkeypatch)
    st.session_state["demo_colors"] = {"A": "#111111", "B": "#222222"}
    st.session_state["demo_color_A"] = "#111111"
    st.session_state["demo_color_B"] = "#222222"
    st.session_state["sel_demo_color_B"] = "\u25a0 Custom..."

    colors = render_component_color_section(
        "demo",
        [ColorTarget(id="A", label="A", default_color="#4B5BA9")],
    )

    assert colors == {"A": "#111111"}
    assert st.session_state["demo_colors"] == {"A": "#111111"}
    assert "demo_color_B" not in st.session_state
    assert "sel_demo_color_B" not in st.session_state


def test_plot_tabs_use_central_color_section():
    modules = [bar_plots, box_plots, donut_plots, histogram_plots, line_plots, sankey_plots]

    for module in modules:
        source = inspect.getsource(module)
        assert "render_component_color_section" in source
        assert "_render_color_picker" not in source

    sankey_source = inspect.getsource(sankey_plots)
    assert "_render_sankey_colors" not in sankey_source


def test_sankey_plotly_chart_kwargs_prefer_width(monkeypatch):
    monkeypatch.setattr(
        sankey_plots.inspect,
        "signature",
        lambda _: SimpleNamespace(parameters={"width": object(), "config": object()}),
    )

    kwargs = sankey_plots._plotly_chart_kwargs()

    assert kwargs == {"config": {}, "width": "stretch"}


def test_sankey_plotly_chart_kwargs_fall_back_to_container_width(monkeypatch):
    monkeypatch.setattr(
        sankey_plots.inspect,
        "signature",
        lambda _: SimpleNamespace(parameters={"use_container_width": object(), "config": object()}),
    )

    kwargs = sankey_plots._plotly_chart_kwargs()

    assert kwargs == {"config": {}, "use_container_width": True}


def test_render_secondary_axis_returns_empty_dict_when_disabled(monkeypatch):
    recorder = _install_line_plot_stubs(monkeypatch)
    st.session_state["secondary_axis_enabled"] = False

    result = line_plots._render_secondary_axis(["motor", "pump"])

    assert result == {}
    assert recorder.containers == []
    assert recorder.multiselects == []
    assert recorder.text_inputs == []
    assert recorder.number_inputs == []
    assert recorder.color_sections == [("secondary_axis", [], "Secondary Colors", False)]


def test_render_secondary_axis_renders_container_and_returns_valid_ylim(monkeypatch):
    recorder = _install_line_plot_stubs(monkeypatch)
    st.session_state["secondary_axis_enabled"] = True
    st.session_state["secondary_axis_components"] = ["pump"]
    st.session_state["secondary_axis_label"] = "Pressure"
    st.session_state["secondary_axis_unit"] = "bar"
    st.session_state["secondary_axis_tick_step"] = 5.0
    st.session_state["secondary_axis_min"] = 10.0
    st.session_state["secondary_axis_max"] = 30.0

    result = line_plots._render_secondary_axis(["pump", "fan"])

    assert recorder.containers == [{"border": True}]
    assert recorder.multiselects[0][0] == "Secondary Components"
    assert [entry[0] for entry in recorder.text_inputs] == [
        "Secondary Label",
        "Secondary Unit",
        "Secondary Tick Step",
        "Secondary Min",
        "Secondary Max",
    ]
    assert recorder.number_inputs == []
    assert recorder.captions == [("Range", {})]
    assert recorder.color_sections == [("secondary_axis", ["pump"], "Secondary Colors", False)]
    assert result["secondary_components"] == ["pump"]
    assert result["secondary_y_label"] == "Pressure"
    assert result["secondary_y_unit"] == "bar"
    assert result["secondary_y_tick_step"] == 5.0
    assert result["secondary_ylim"] == (10.0, 30.0)


def test_render_secondary_axis_warns_for_invalid_ylim(monkeypatch):
    recorder = _install_line_plot_stubs(monkeypatch)
    st.session_state["secondary_axis_enabled"] = True
    st.session_state["secondary_axis_tick_step"] = 5.0
    st.session_state["secondary_axis_min"] = 30.0
    st.session_state["secondary_axis_max"] = 10.0

    result = line_plots._render_secondary_axis(["pump"])

    assert result["secondary_ylim"] is None
    assert recorder.warnings == [("Secondary Max must be greater than Secondary Min.", {})]


def test_render_secondary_axis_parses_text_inputs_with_decimal_comma(monkeypatch):
    _install_line_plot_stubs(monkeypatch)
    st.session_state["secondary_axis_enabled"] = True
    st.session_state["secondary_axis_tick_step_ui"] = "2,5"
    st.session_state["secondary_axis_min_ui"] = "10,5"
    st.session_state["secondary_axis_max_ui"] = "30,5"

    result = line_plots._render_secondary_axis(["pump"])

    assert result["secondary_y_tick_step"] == 2.5
    assert result["secondary_ylim"] == (10.5, 30.5)
    assert st.session_state["secondary_axis_tick_step"] == 2.5
    assert st.session_state["secondary_axis_min"] == 10.5
    assert st.session_state["secondary_axis_max"] == 30.5


def test_scatter_tab_uses_shared_axis_settings_and_numeric_color_scale(monkeypatch):
    recorded = {"text_inputs": [], "selectboxes": [], "plot_kwargs": None, "column_specs": []}

    class DummyColumn:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def text_input(self, label, key=None, value="", **kwargs):
            recorded["text_inputs"].append(label)
            current = st.session_state.get(key, value)
            st.session_state[key] = current
            return current

    def fake_columns(spec):
        recorded["column_specs"].append(spec)
        count = spec if isinstance(spec, int) else len(spec)
        return [DummyColumn() for _ in range(count)]

    def fake_selectbox(label, options, key=None, **kwargs):
        recorded["selectboxes"].append(label)
        value = st.session_state.get(key, options[0])
        st.session_state[key] = value
        return value

    def fake_text_input(label, key=None, value="", **kwargs):
        recorded["text_inputs"].append(label)
        current = st.session_state.get(key, value)
        st.session_state[key] = current
        return current

    def fake_number_input(label, key=None, **kwargs):
        current = st.session_state.get(key, kwargs.get("min_value", 0.0))
        st.session_state[key] = current
        return current

    def fake_plot_scatter(*args, **kwargs):
        from matplotlib.figure import Figure

        recorded["plot_kwargs"] = kwargs
        return Figure()

    monkeypatch.setattr(scatter_plots.st, "columns", fake_columns)
    monkeypatch.setattr(scatter_plots.st, "markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr(scatter_plots.st, "selectbox", fake_selectbox)
    monkeypatch.setattr(scatter_plots.st, "number_input", fake_number_input)
    monkeypatch.setattr(scatter_plots.st, "text_input", fake_text_input)
    monkeypatch.setattr(scatter_plots.st, "divider", lambda *args, **kwargs: None)
    monkeypatch.setattr(scatter_plots.st, "caption", lambda *args, **kwargs: None)
    monkeypatch.setattr(scatter_plots.st, "info", lambda *args, **kwargs: None)
    monkeypatch.setattr(scatter_plots.st, "warning", lambda *args, **kwargs: None)
    monkeypatch.setattr(scatter_plots.st, "pyplot", lambda *args, **kwargs: None)
    monkeypatch.setattr(scatter_plots, "plot_scatter", fake_plot_scatter)

    st.session_state["scatter_x_select"] = "x"
    st.session_state["scatter_y_select"] = "y"
    st.session_state["scatter_color_select"] = "color"
    st.session_state["scatter_point_type"] = "Diamond"
    st.session_state["scatter_point_size"] = 25.0
    st.session_state["scatter_edge_width"] = 0.5
    st.session_state["scatter_color_label"] = "Legend"
    st.session_state["scatter_color_min"] = "1"
    st.session_state["scatter_color_max"] = "9"
    st.session_state["scatter_color_tick_step"] = "2"

    processed = type(
        "Processed",
        (),
        {"has_data": True, "combined_frame": pd.DataFrame({"x": [1.0, 2.0], "y": [3.0, 4.0], "color": [5.0, 6.0]})},
    )()
    options = {
        "ranges_valid": True,
        "numeric_plot_columns": ["x", "y", "color"],
        "axis_annotation_fontsize": 10,
        "axis_title_fontsize": 12,
        "x_axis_label": "Shared X",
        "y_axis_label": "Shared Y",
        "x_unit": "s",
        "y_unit": "W",
        "x_tick_step": 1.0,
        "y_tick_step": 5.0,
        "set_x_range": True,
        "set_y_range": True,
        "x_min": 0.0,
        "x_max": 10.0,
        "y_min": 0.0,
        "y_max": 20.0,
    }

    scatter_plots.render(processed, options)

    assert "Point Type" in recorded["selectboxes"]
    assert "X Unit" not in recorded["text_inputs"]
    assert "Y Unit" not in recorded["text_inputs"]
    assert "Color Legend" in recorded["text_inputs"]
    assert "Color Min" in recorded["text_inputs"]
    assert "Color Max" in recorded["text_inputs"]
    assert "Color Tick Step" in recorded["text_inputs"]
    assert 2 in recorded["column_specs"]
    assert recorded["plot_kwargs"]["marker"] == "D"
    assert recorded["plot_kwargs"]["x_label"] == "Shared X"
    assert recorded["plot_kwargs"]["y_label"] == "Shared Y"
    assert recorded["plot_kwargs"]["x_unit"] == "s"
    assert recorded["plot_kwargs"]["y_unit"] == "W"
    assert recorded["plot_kwargs"]["color_min"] == 1.0
    assert recorded["plot_kwargs"]["color_max"] == 9.0
    assert recorded["plot_kwargs"]["color_tick_step"] == 2.0
