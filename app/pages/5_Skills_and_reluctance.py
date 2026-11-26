"""Axis 5: Skills and reluctance (interface only; analysis in src/so_ai/axes/skills.py)."""

import streamlit as st

import components as ui
from so_ai import population as pop

st.set_page_config(page_title="Skills and reluctance | SO Survey 2026", layout="wide")

df_all = ui.get_survey()
filters = ui.sidebar_filters(df_all)
df = pop.apply_filters(df_all, filters)

ui.axis_header("Axis 5: Skills and reluctance", owner="TBD", question="How do respondents learn AI, and what holds them back?")

st.info("This axis is being built by its owner on the branch `axis/skills`.")
st.markdown("Planned survey columns: `LearnAI`, `LearnAIHow`, `AIAvoid`, `AISentiment`, `WorkExp`, `Role`, `JobSat`.")
ui.population_caption(df, filters)
