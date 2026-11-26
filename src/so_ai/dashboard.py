"""Indicators of the main dashboard.

Message for Numeum (computed live by the app from these indicators):
    Respondents in France are more reluctant about AI than respondents in the rest of
    the EU: fewer use it at work, more of them avoid it, and fewer learned it at work.
    Their reasons are concerns (skills, ethics, environment), not lack of access.

Each indicator is a share of respondents who gave a set of "positive" answers to
one question, computed per zone (France / EU excl. France / rest of the world).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from so_ai.analysis import answer_shares_by_group, share_of
from so_ai.population import ZONES


@dataclass(frozen=True)
class Indicator:
    key: str
    label: str           # short label shown on the chart
    column: str          # survey column
    positive: tuple      # answers counted as "yes"
    question: str        # plain-English reminder of what was asked


INDICATORS = [
    Indicator(
        "uses_ai", "Use AI tools at work", "UsesAI", ("Yes",),
        "Do you currently use AI tools or AI agents in your role at work?",
    ),
    Indicator(
        "not_avoid", "Do not avoid AI", "AIAvoid", ("I do not avoid using AI at work or school",),
        "Do you try to avoid using AI tools or agents at work or school?",
    ),
    Indicator(
        "favorable", "Favorable to AI", "AISentiment", ("Very favorable", "Somewhat favorable"),
        "Attitude toward using AI tools or agents as part of your work",
    ),
    Indicator(
        "learned_at_work", "Learned AI at work", "LearnAI",
        ("Yes, at work", "Yes, both on my own and at work"),
        "In the last year, did you spend time learning AI programming or AI-enabled tooling?",
    ),
    Indicator(
        "trust_many", "Trust AI for many tasks", "AITrust",
        ("I trust it for many tasks, but not important work decisions",
         "I trust it for many tasks, including important work decisions"),
        "How much do you trust the output from AI tools or agents?",
    ),
    Indicator(
        "org_guidance", "Employer gives tools + guidance", "AIUse",
        ("My organization provides approved AI tools and guidance for how to use them",),
        "How are AI tools or agents used at your organization?",
    ),
]

INDICATOR_BY_KEY = {i.key: i for i in INDICATORS}


def indicators_by_zone(df: pd.DataFrame, zones: list[str] = ZONES) -> pd.DataFrame:
    """One row per (indicator, zone) with share (0-1) and n (respondents who answered)."""
    rows = []
    for ind in INDICATORS:
        for zone in zones:
            share, n = share_of(df[df["Zone"] == zone], ind.column, list(ind.positive))
            rows.append({"key": ind.key, "indicator": ind.label, "column": ind.column,
                         "zone": zone, "share": share, "n": n})
    return pd.DataFrame(rows)


def gap(table: pd.DataFrame, key: str, a: str, b: str) -> float:
    """Difference in percentage points between zone a and zone b for one indicator."""
    rows = table[table["key"] == key].set_index("zone")["share"]
    return float((rows[a] - rows[b]) * 100)


def avoid_reasons_by_zone(df: pd.DataFrame, zones: list[str] = ZONES) -> pd.DataFrame:
    """Answers to AIAvoid (single choice) per zone: group, answer, count, n, share."""
    return answer_shares_by_group(df, "AIAvoid", "Zone", groups=zones)
