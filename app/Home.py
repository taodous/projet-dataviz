"""Main dashboard: one message for Numeum.

Run from the repository root:
    streamlit run app/Home.py

Layout only: every number comes from so_ai.dashboard / so_ai.population.
"""

import pandas as pd
import streamlit as st

import components as ui
from so_ai import population as pop
from so_ai.dashboard import INDICATORS, avoid_reasons_by_zone, gap, indicators_by_zone

st.set_page_config(page_title="AI at work, France vs EU | SO Survey 2026", layout="wide")

df_all = ui.get_survey()
filters = ui.sidebar_filters(df_all)
df = pop.apply_filters(df_all, filters)

# ---------------------------------------------------------------- headline
table = indicators_by_zone(df)
gap_avoid = gap(table, "not_avoid", pop.FRANCE, pop.EU_EXCL_FR)
gap_use = gap(table, "uses_ai", pop.FRANCE, pop.EU_EXCL_FR)
gap_learn = gap(table, "learned_at_work", pop.FRANCE, pop.EU_EXCL_FR)

st.title("AI at work: respondents in France hold back more than their EU peers")
st.markdown(
    "**Message for Numeum.** Respondents in France use AI at work less, avoid it more and "
    "have learned it at work less often than respondents in the rest of the EU. "
    "Their reasons are concerns about skills, ethics and the environment, not lack of access. "
    "Employer-led training and clear responsible-use guidance are the lever."
)
st.info(pop.VOLUNTEER_WARNING, icon="ℹ️")


def tile(col, key: str, title: str, gap_pp: float) -> None:
    """Stat tile: France share, EU share, gap in percentage points, and both n."""
    rows = table[table["key"] == key].set_index("zone")
    fr, eu = rows.loc[pop.FRANCE], rows.loc[pop.EU_EXCL_FR]
    col.metric(title, f"{fr.share:.0%} in France", f"{gap_pp:+.0f} pts vs EU ({eu.share:.0%})")
    col.caption(f"n = {fr.n:,} in France, {eu.n:,} in the rest of the EU (respondents who answered {fr.column})")


c1, c2, c3 = st.columns(3)
tile(c1, "uses_ai", "Use AI tools at work", gap_use)
tile(c2, "not_avoid", "Do not try to avoid AI", gap_avoid)
tile(c3, "learned_at_work", "Learned AI at work last year", gap_learn)

st.divider()

# ---------------------------------------------------------------- figure 1: indicators
st.subheader("1. Six AI indicators, France vs. the rest of the EU and the world")
st.markdown("Share of respondents giving the answer shown, among those who answered each question.")
order = [i.label for i in INDICATORS]
fig = ui.dot_plot(table, y="indicator", x="share", color="zone", order=order, colors=ui.ZONE_COLORS)
st.plotly_chart(ui.style(fig, height=400, x_title="Share of respondents who answered (%)"),
                use_container_width=True)

n_min = table.groupby("zone")["n"].min().to_dict()
ui.small_group_warning(n_min)
n_fr = table[table.zone == pop.FRANCE].set_index("indicator")["n"]
st.caption(
    f"{pop.caption(df[df.Zone != pop.NO_COUNTRY], pop.describe_filters(filters) + ', by zone of residence')}. "
    f"Each indicator has its own n (respondents who answered it), from {int(n_fr.min()):,} to "
    f"{int(n_fr.max()):,} in France; hover a dot for its n. {pop.MISSING_RULE}"
)
with st.expander("Definitions and data table"):
    st.markdown("\n".join(
        f"- **{i.label}** (`{i.column}`): {i.question} Counted: {', '.join(i.positive)}." for i in INDICATORS
    ))
    st.dataframe(
        table.assign(share=lambda t: (t.share * 100).round(1))
             .rename(columns={"share": "share (%)"})[["indicator", "zone", "share (%)", "n"]],
        hide_index=True, use_container_width=True,
    )

st.divider()

# ---------------------------------------------------------------- figure 2: why avoid
st.subheader("2. Why respondents avoid AI: concerns, not lack of training")
st.markdown("Answer to *“Do you try to avoid using AI tools or agents at work or school?”* (one choice).")
reasons = avoid_reasons_by_zone(df)
reason_order = (reasons[reasons.group == pop.FRANCE].sort_values("share", ascending=False)["answer"].tolist())
fig2 = ui.grouped_bars(reasons, "answer", "share", "group", reason_order, ui.ZONE_COLORS)
st.plotly_chart(ui.style(fig2, height=430, x_title="Share of respondents who answered (%)"),
                use_container_width=True)
n_reason = reasons.groupby("group")["n"].first().reindex(pop.ZONES).fillna(0).astype(int)
ui.small_group_warning(n_reason.to_dict())
st.caption(
    pop.caption(pop.answered(df[df.Zone != pop.NO_COUNTRY], "AIAvoid"),
                pop.describe_filters(filters) + ", by zone of residence", "AIAvoid")
    + f" (France {n_reason[pop.FRANCE]:,}, EU excl. France {n_reason[pop.EU_EXCL_FR]:,}, "
      f"rest of the world {n_reason[pop.REST_OF_WORLD]:,}). Shares sum to 100% within each zone."
)

st.divider()

# ---------------------------------------------------------------- about
with st.expander("About the data and the method"):
    no_country = pop.n_respondents(df_all[df_all.Zone == pop.NO_COUNTRY])
    st.markdown(f"""
- **Source:** Stack Overflow Developer Survey 2026, public answers file (`survey_results_public.csv`),
  {pop.n_respondents(df_all):,} respondents in total.
- **Volunteer sample:** {pop.VOLUNTEER_WARNING}
- **Zones:** from the question *“Where do you live?”*. *EU (excl. France)* is the 26 other member states.
  {no_country:,} respondents did not answer the country question (it comes late in the survey);
  they are left out of the zone comparisons.
- **Missing answers:** {pop.MISSING_RULE} "Not sure" answers are kept as answers.
- **Small groups:** groups under {pop.SMALL_GROUP} respondents are flagged and should not be interpreted.
- **Explore further:** the five axis pages in the sidebar each have their own filters.
""")
