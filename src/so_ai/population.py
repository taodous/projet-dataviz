"""Shared population logic: who is behind each figure.

Every page of the app uses this module to:
  1. filter respondents (apply_filters),
  2. keep only those who answered the question shown (answered),
  3. write the population caption with a computed n (caption).

Rules (see CLAUDE.md):
  - The sample is made of volunteers: we write "respondents", never "developers".
  - Missing answers are EXCLUDED from the denominator of every share. "Not sure"
    or "Prefer not to say" are real answers and are kept.
  - n is always computed from the filtered data, never hard-coded.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from so_ai import SURVEY_NAME

# ---------------------------------------------------------------- geography
FRANCE = "France"
EU_EXCL_FR = "EU (excl. France)"
REST_OF_WORLD = "Rest of the world"
NO_COUNTRY = "Country not given"
ZONES = [FRANCE, EU_EXCL_FR, REST_OF_WORLD]  # display order

# The 27 EU member states, spelled as in the survey's Country column.
EU_COUNTRIES = [
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark",
    "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy",
    "Latvia", "Lithuania", "Luxembourg", "Malta", "Netherlands", "Poland", "Portugal",
    "Romania", "Slovakia", "Slovenia", "Spain", "Sweden",
]

# Below this many answers we show the group but warn that it is too small to conclude.
SMALL_GROUP = 30

VOLUNTEER_WARNING = (
    "The Stack Overflow survey is answered by volunteers who chose to take an online "
    "survey. Its respondents are not a random sample of developers, so figures describe "
    "the respondents only, not all developers in France or elsewhere."
)

MISSING_RULE = (
    "Missing answers are excluded: each share is computed among the respondents "
    "who answered the question shown."
)


def zone_of(country: object) -> str:
    """Map a Country answer to one of the comparison zones."""
    if pd.isna(country):
        return NO_COUNTRY
    if country == FRANCE:
        return FRANCE
    if country in EU_COUNTRIES:
        return EU_EXCL_FR
    return REST_OF_WORLD


def add_zone(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with a Zone column (France / EU excl. France / rest / not given)."""
    out = df.copy()
    out["Zone"] = out["Country"].map(zone_of)
    return out


# ---------------------------------------------------------------- filters
@dataclass
class Filters:
    """Population filters. An empty list means "no filter on this column"."""

    zones: list[str] = field(default_factory=list)
    countries: list[str] = field(default_factory=list)
    employment: list[str] = field(default_factory=list)
    code_main: list[str] = field(default_factory=list)
    age: list[str] = field(default_factory=list)

    # column in the data -> attribute name
    COLUMNS = {
        "Zone": "zones",
        "Country": "countries",
        "Employment": "employment",
        "CodeMain": "code_main",
        "Age": "age",
    }

    # short labels for the caption
    LABELS = {
        "zones": "zone",
        "countries": "country",
        "employment": "employment",
        "code_main": "coding role",
        "age": "age",
    }


def apply_filters(df: pd.DataFrame, filters: Filters) -> pd.DataFrame:
    """Keep the rows that match every non-empty filter."""
    mask = pd.Series(True, index=df.index)
    for column, attr in Filters.COLUMNS.items():
        values = getattr(filters, attr)
        if values:
            mask &= df[column].isin(values)
    return df[mask]


def answered(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Keep only the respondents who answered `column` (missing answers excluded)."""
    return df[df[column].notna()]


def n_respondents(df: pd.DataFrame, column: str | None = None) -> int:
    """Number of respondents, or of respondents who answered `column`."""
    if column is None:
        return int(len(df))
    return int(df[column].notna().sum())


def describe_filters(filters: Filters) -> str:
    """Human-readable summary of the active filters, for captions."""
    parts = []
    for attr, label in Filters.LABELS.items():
        values = getattr(filters, attr)
        if values:
            shown = ", ".join(values) if len(values) <= 3 else f"{len(values)} selected"
            parts.append(f"{label}: {shown}")
    return "; ".join(parts) if parts else "all respondents"


def caption(df: pd.DataFrame, population: str, column: str | None = None) -> str:
    """Population caption required under every figure.

    Format: "Stack Overflow Developer Survey 2026, <population>, n = <count> respondents".
    `column` restricts n to the respondents who answered that question.
    """
    n = n_respondents(df, column)
    who = population
    if column is not None:
        who += f", who answered {column}"
    return f"{SURVEY_NAME}, {who}, n = {n:,} respondents"


def is_small(n: int) -> bool:
    """True when a group is too small to draw conclusions from."""
    return n < SMALL_GROUP
