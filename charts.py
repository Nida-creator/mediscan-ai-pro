"""
charts.py
MediScan AI Pro — Tech Member 3 (Data + Parser)

Generates Plotly health trend charts from report history.
All functions are PURE — no Streamlit calls inside.
Just return Plotly Figure objects.
"""

import plotly.graph_objects as go


def make_trend_chart(dates, values, label, normal_min, normal_max):
    """
    Build a Plotly line chart for a single health metric over time.

    Args:
        dates       : list of date strings or report labels  e.g. ['2024-01-10', '2024-03-15']
        values      : list of numeric values matching dates  e.g. [95, 110, 88]
        label       : name of the metric                     e.g. 'Glucose'
        normal_min  : lower bound of the normal/healthy range
        normal_max  : upper bound of the normal/healthy range

    Returns:
        plotly.graph_objects.Figure
    """
    fig = go.Figure()

    # ── Green normal-range band ──────────────────────────────────────────
    fig.add_hrect(
        y0=normal_min,
        y1=normal_max,
        fillcolor="green",
        opacity=0.1,
        line_width=0,
        annotation_text="Normal Range",
        annotation_position="top left",
        annotation=dict(font_size=11, font_color="green"),
    )

    # ── Main trend line ──────────────────────────────────────────────────
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=values,
            mode="lines+markers",
            name=label,
            line=dict(color="#1D9E75", width=2),
            marker=dict(size=8, color="#1D9E75"),
            hovertemplate=f"<b>{label}</b><br>Date: %{{x}}<br>Value: %{{y}}<extra></extra>",
        )
    )

    # ── Layout ───────────────────────────────────────────────────────────
    fig.update_layout(
        title=dict(text=f"{label} Over Time", font=dict(size=16)),
        xaxis_title="Date / Report",
        yaxis_title=label,
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=350,
        margin=dict(l=50, r=30, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    )

    return fig


def make_multi_metric_chart(dates, metrics_dict, normal_ranges=None):
    """
    Build a single Plotly chart with MULTIPLE health metrics overlaid.

    Args:
        dates         : list of date/label strings (shared x-axis)
        metrics_dict  : dict  { 'Glucose': [95, 110], 'WBC': [6.2, 7.1], ... }
        normal_ranges : dict  { 'Glucose': (70, 100), 'WBC': (4.5, 11.0) }  (optional)

    Returns:
        plotly.graph_objects.Figure
    """
    COLORS = ["#1D9E75", "#E07B54", "#5B8DB8", "#A569BD", "#F4D03F"]
    normal_ranges = normal_ranges or {}
    fig = go.Figure()

    for idx, (label, values) in enumerate(metrics_dict.items()):
        color = COLORS[idx % len(COLORS)]

        if label in normal_ranges:
            lo, hi = normal_ranges[label]
            fig.add_hrect(
                y0=lo, y1=hi,
                fillcolor=color, opacity=0.06,
                line_width=0,
            )

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=values,
                mode="lines+markers",
                name=label,
                line=dict(color=color, width=2),
                marker=dict(size=7, color=color),
                hovertemplate=f"<b>{label}</b><br>Date: %{{x}}<br>Value: %{{y}}<extra></extra>",
            )
        )

    fig.update_layout(
        title=dict(text="Health Metrics Over Time", font=dict(size=16)),
        xaxis_title="Date / Report",
        yaxis_title="Value",
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=400,
        margin=dict(l=50, r=30, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    )

    return fig


if __name__ == "__main__":
    sample_dates   = ["Report 1", "Report 2", "Report 3", "Report 4"]
    sample_glucose = [95, 112, 88, 103]
    fig = make_trend_chart(sample_dates, sample_glucose, "Glucose", 70, 100)
    fig.show()
    print("charts.py OK — make_trend_chart() works fine.")