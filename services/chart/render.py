import pandas as pd
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties


FONT_FAMILY = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]


def _chart_font() -> FontProperties:
    return FontProperties(family=FONT_FAMILY)


def build_chart_series(frame: pd.DataFrame, category_column: str, value_column: str) -> dict[str, list]:
    chart_frame = frame[[category_column, value_column]].dropna(subset=[category_column, value_column]).copy()
    chart_frame[value_column] = pd.to_numeric(chart_frame[value_column], errors="coerce")
    chart_frame = chart_frame.dropna(subset=[value_column])
    return {
        "x": chart_frame[category_column].astype(str).tolist(),
        "y": chart_frame[value_column].tolist(),
    }


def draw_chart(figure: Figure, data: dict[str, list], chart_type: str, title: str) -> None:
    figure.clear()
    axes = figure.add_subplot(111)
    if chart_type == "line":
        axes.plot(data["x"], data["y"], marker="o")
    else:
        axes.bar(data["x"], data["y"])
    font = _chart_font()
    axes.set_title(title, fontproperties=font)
    axes.tick_params(axis="x", rotation=30)
    for label in axes.get_xticklabels() + axes.get_yticklabels():
        label.set_fontproperties(font)
    figure.tight_layout()


def draw_empty_chart_state(figure: Figure, message: str) -> None:
    figure.clear()
    axes = figure.add_subplot(111)
    axes.set_xticks([])
    axes.set_yticks([])
    for spine in axes.spines.values():
        spine.set_visible(False)
    axes.text(0.5, 0.5, message, ha="center", va="center", fontsize=12, fontproperties=_chart_font())
    figure.tight_layout()
