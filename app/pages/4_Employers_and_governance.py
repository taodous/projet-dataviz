"""Axis 4: Employers and governance (interface only; analysis in src/so_ai/axes/organisations.py)."""

import streamlit as st

import components as ui
from so_ai import population as pop

st.set_page_config(page_title="Employers and governance | SO Survey 2026", layout="wide")

df_all = ui.get_survey()
filters = ui.sidebar_filters(df_all)
df = pop.apply_filters(df_all, filters)

ui.axis_header("Axis 4: Employers and governance", owner="TBD", question="How do organisations frame, equip and measure AI use?")

st.info("This axis is being built by its owner on the branch `axis/organisations`.")
st.markdown("Planned survey columns: `AIUse`, `AITry`, `AIAdopt`, `AIToken`, `OrgSize`, `Industry`, `TechBudget`.")
ui.population_caption(df, filters)
