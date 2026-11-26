"""Interface helpers shared by Home.py and every axis page.

This is the only place that touches st.cache_data and st.session_state for
shared state. The analysis itself is in src/so_ai/.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from so_ai import population as pop
from so_ai.data import load_schema, load_survey

# Categorical colours, fixed per zone (colour follows the entity, never its rank).
ZONE_COLORS = {
    pop.FRANCE: "#257de0",         # blue
    pop.EU_EXCL_FR: "#f47230",     # orange
    pop.REST_OF_WORLD: "#00b894",  # aqua
}
NEUTRAL = "#9c9c9c"
TEXT = "#191919"
TEXT_SECONDARY = "#666666"
GRID = "#e6e6e6"


# ------------------------------------------------------------------ data (cached)
@st.cache_data(show_spinner="Loading the 2026 survey (first start downloads ~120 MB)...")
def get_survey() -> pd.DataFrame:
    """Cleaned survey, loaded once per server process."""
    return load_survey()


@st.cache_data
def get_schema() -> pd.DataFrame:
    return load_schema()


# ------------------------------------------------------------------ shared filters
# Widget state is lost when a page that does not show the widget is opened, so the
# selected values are copied into separate "shared_*" keys that survive page changes.
SHARED_FILTERS = {
    # session key : (data column, label)
    "employment": ("Employment", "Employment status"),
    "code_main": ("CodeMain", "Relation to code"),
    "age": ("Age", "Age group"),
}


def _sync(key: str) -> None:
    st.session_state[f"shared_{key}"] = st.session_state[f"widget_{key}"]


def sidebar_filters(df: pd.DataFrame) -> pop.Filters:
    """Draw the shared population filters in the sidebar and return them.

    The same selection is kept when the reader moves between pages.
    """
    st.sidebar.header("Population")
    st.sidebar.caption("Shared by every page. Leave empty to keep all respondents.")
    values = {}
    for key, (column, label) in SHARED_FILTERS.items():
        options = sorted(df[column].dropna().unique())
        st.session_state.setdefault(f"shared_{key}", [])
        st.session_state[f"widget_{key}"] = st.session_state[f"shared_{key}"]
        values[key] = st.sidebar.multiselect(
            label, options, key=f"widget_{key}", on_change=_sync, args=(key,)
        )
    st.sidebar.divider()
    st.sidebar.caption(pop.VOLUNTEER_WARNING)
    return pop.Filters(**values)


# ------------------------------------------------------------------ captions
def population_caption(df: pd.DataFrame, filters: pop.Filters, column: str | None = None,
                       extra: str | None = None) -> None:
    """Show the required caption under a figure: survey, population, computed n."""
    who = pop.describe_filters(filters)
    if extra:
        who = f"{extra}, {who}"
    st.caption(pop.caption(df, who, column))


def small_group_warning(n_by_group: dict[str, int]) -> None:
    """Warn when one of the groups shown is too small to conclude from."""
    small = {g: n for g, n in n_by_group.items() if pop.is_small(n)}
    if small:
        listed = ", ".join(f"{g} (n = {n})" for g, n in small.items())
        st.warning(f"Small groups, do not draw conclusions: {listed}.")


# ------------------------------------------------------------------ chart styling
def style(fig: go.Figure, height: int = 360, x_title: str = "", y_title: str = "") -> go.Figure:
    """Common Plotly layout: recessive grid, readable labels, legend on top."""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=20, t=40, b=10),
        font=dict(color=TEXT, size=13),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title=None),
        hoverlabel=dict(bgcolor="white", font_color=TEXT),
    )
    fig.update_xaxes(title=x_title, gridcolor=GRID, zeroline=False, color=TEXT_SECONDARY)
    fig.update_yaxes(title=y_title, gridcolor=GRID, zeroline=False, color=TEXT_SECONDARY)
    return fig


def dot_plot(table: pd.DataFrame, y: str, x: str, color: str, order: list[str],
             colors: dict[str, str], hover_n: str = "n") -> go.Figure:
    """Dot plot: one row per category on y, one dot per group (share in % on x).

    Rows linked by a thin grey line so the gap between groups reads at a glance.
    """
    fig = go.Figure()
    for cat in order:
        row = table[table[y] == cat]
        fig.add_trace(go.Scatter(
            x=row[x] * 100, y=[cat] * len(row), mode="lines",
            line=dict(color=GRID, width=2), hoverinfo="skip", showlegend=False,
        ))
    # Draw the first group (France) last so it sits on top when dots overlap;
    # the legend is reversed back so it still reads France first.
    for group, col in reversed(colors.items()):
        part = table[table[color] == group].set_index(y).reindex(order).reset_index()
        fig.add_trace(go.Scatter(
            x=part[x] * 100, y=part[y], mode="markers", name=group,
            marker=dict(size=13, color=col, line=dict(color="white", width=2)),
            customdata=part[[hover_n]].values,
            hovertemplate=f"<b>%{{y}}</b><br>{group}: %{{x:.1f}}% of respondents"
                          "<br>n = %{customdata[0]:,} respondents<extra></extra>",
        ))
    fig.update_yaxes(categoryorder="array", categoryarray=list(reversed(order)))
    fig.update_xaxes(ticksuffix="%", range=[0, 100])
    fig.update_layout(legend_traceorder="reversed")
    return fig


def grouped_bars(table: pd.DataFrame, category: str, value: str, group: str,
                 order: list[str], colors: dict[str, str]) -> go.Figure:
    """Horizontal grouped bars (share in %) with the n of each group in the tooltip."""
    fig = go.Figure()
    # Horizontal groups stack from the bottom: add France last so it is the top bar.
    for g, col in reversed(colors.items()):
        part = table[table[group] == g].set_index(category).reindex(order).reset_index()
        fig.add_trace(go.Bar(
            y=part[category], x=part[value] * 100, name=g, orientation="h",
            marker=dict(color=col, cornerradius=4),
            customdata=part[["count", "n"]].values,
            hovertemplate=f"<b>%{{y}}</b><br>{g}: %{{x:.1f}}%"
                          "<br>%{customdata[0]:,} of %{customdata[1]:,} respondents<extra></extra>",
        ))
    fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.08, legend_traceorder="reversed")
    fig.update_yaxes(categoryorder="array", categoryarray=list(reversed(order)))
    fig.update_xaxes(ticksuffix="%")
    return fig


def axis_header(title: str, owner: str, question: str) -> None:
    """Title block of an axis page."""
    st.title(title)
    st.markdown(f"**Question for Numeum:** {question}")
    st.caption(f"Axis owner: {owner}")
