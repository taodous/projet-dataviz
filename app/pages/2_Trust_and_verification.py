"""Axis 2: Trust and verification (interface only; analysis in src/so_ai/axes/trust.py)."""

import streamlit as st

import components as ui
from so_ai import population as pop

st.set_page_config(page_title="Trust and verification | SO Survey 2026", layout="wide")

df_all = ui.get_survey()
filters = ui.sidebar_filters(df_all)
df = pop.apply_filters(df_all, filters)

ui.axis_header("Axis 2: Trust and verification", owner="TBD", question="How far do respondents trust AI output, and how do they check it?")

st.info("This axis is being built by its owner on the branch `axis/trust`.")
st.markdown("Planned survey columns: `AITrust`, `AIComplex`, `AIWorkNext`, `Disruption`, `KnowledgeSourceAI`, `KnowAgentTrust`.")
ui.population_caption(df, filters)
