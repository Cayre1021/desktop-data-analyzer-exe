import pandas as pd
from matplotlib.figure import Figure

from services.chart.render import build_chart_series, draw_chart, draw_empty_chart_state


def test_build_chart_series_for_bar_chart_returns_x_and_y_lists():
    frame = pd.DataFrame([
        {"month": "Jan", "sales": 10},
        {"month": "Feb", "sales": 12},
    ])

    result = build_chart_series(frame, "month", "sales")

    assert result == {
        "x": ["Jan", "Feb"],
        "y": [10, 12],
    }


def test_build_chart_series_drops_non_numeric_values_from_y_axis():
    frame = pd.DataFrame([
        {"month": "Jan", "sales": "10"},
        {"month": "Feb", "sales": "bad"},
        {"month": "Mar", "sales": 12},
    ])

    result = build_chart_series(frame, "month", "sales")

    assert result == {
        "x": ["Jan", "Mar"],
        "y": [10.0, 12.0],
    }


def test_draw_chart_adds_one_axes_with_requested_title():
    figure = Figure()
    data = {"x": ["Jan", "Feb"], "y": [10, 12]}

    draw_chart(figure, data, "bar", "Monthly Sales")

    assert len(figure.axes) == 1
    assert figure.axes[0].get_title() == "Monthly Sales"


def test_draw_empty_chart_state_shows_message_in_axes_text():
    figure = Figure()

    draw_empty_chart_state(figure, "暂无可用图表")

    assert len(figure.axes) == 1
    assert figure.axes[0].texts[0].get_text() == "暂无可用图表"
