"""Axis 3: Productivity by task (interface only; analysis in src/so_ai/axes/productivity.py)."""

import streamlit as st

import components as ui
from so_ai import population as pop

st.set_page_config(page_title="Productivity by task | SO Survey 2026", layout="wide")

df_all = ui.get_survey()
filters = ui.sidebar_filters(df_all)
df = pop.apply_filters(df_all, filters)

ui.axis_header("Axis 3: Productivity by task", owner="TBD", question="For which development tasks does AI help, and for which does it not?")

st.info("This axis is being built by its owner on the branch `axis/productivity`.")
st.markdown("Planned survey columns: `AIImpact_1..7`, `AISat_1..7`, `AIWorkCurrentlyUse`, `AIWorkExpectMore`, `KnowAgentDelegate`.")
ui.population_caption(df, filters)
