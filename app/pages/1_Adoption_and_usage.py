"""Axis 1: Adoption and usage (interface only; analysis in src/so_ai/axes/adoption.py)."""

import streamlit as st

import components as ui
from so_ai import population as pop

st.set_page_config(page_title="Adoption and usage | SO Survey 2026", layout="wide")

df_all = ui.get_survey()
filters = ui.sidebar_filters(df_all)
df = pop.apply_filters(df_all, filters)

ui.axis_header("Axis 1: Adoption and usage", owner="TBD", question="Who uses AI at work, which tools, and how often?")

st.info("This axis is being built by its owner on the branch `axis/adoption`.")
st.markdown("Planned survey columns: `AISelect`, `UsesAI`, `AIFreq_1..4`, `AIDaily`, `AIToolCount`, `AICodeAgentHaveWorkedWith`, `LLMHaveWorkedWith`.")
ui.population_caption(df, filters)
