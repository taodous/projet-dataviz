"""Load and clean the 2026 survey answers.

Data flow:
    data/raw/survey_results_public_2026.csv   (downloaded, ~120 MB)
        -> load_raw()          read with pandas
        -> clean()             add derived columns (Zone, UsesAI)
        -> data/processed/survey_2026.parquet  (fast reload on the next start)

Caching in memory is done by the app (st.cache_data), not here.
"""

from __future__ import annotations

import html
from pathlib import Path

import pandas as pd

from so_ai.download import PROJECT_ROOT, RAW_DIR, download_2026
from so_ai.population import add_zone

RAW_FILE = RAW_DIR / "survey_results_public_2026.csv"
SCHEMA_FILE = RAW_DIR / "survey_results_schema_2026.csv"
PROCESSED_FILE = PROJECT_ROOT / "data" / "processed" / "survey_2026.parquet"

# Answer that marks a respondent who does not use AI at work (AISelect, multi-select).
NO_AI_ANSWER = "I don’t use AI tools"


def load_raw(path: Path = RAW_FILE) -> pd.DataFrame:
    """Read the raw CSV. Every column is kept as published."""
    return pd.read_csv(path, low_memory=False, encoding="utf-8")


def add_uses_ai(df: pd.DataFrame) -> pd.DataFrame:
    """Add UsesAI: "Yes" / "No" from AISelect, missing when AISelect is missing.

    AISelect is multi-select: a respondent uses AI at work unless they picked
    "I don't use AI tools".
    """
    out = df.copy()
    answered = out["AISelect"].notna()
    no_ai = out["AISelect"].fillna("").str.contains(NO_AI_ANSWER, regex=False)
    out["UsesAI"] = pd.NA
    out.loc[answered & no_ai, "UsesAI"] = "No"
    out.loc[answered & ~no_ai, "UsesAI"] = "Yes"
    return out


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Return the survey with the derived columns used across the app."""
    out = add_zone(df)
    out = add_uses_ai(out)
    return out


def load_survey(use_cache_file: bool = True) -> pd.DataFrame:
    """Return the cleaned 2026 survey, downloading the raw file if needed.

    The cleaned table is written to data/processed/ as Parquet, so the next
    start skips the CSV parsing.
    """
    if use_cache_file and PROCESSED_FILE.exists():
        return pd.read_parquet(PROCESSED_FILE)

    if not RAW_FILE.exists():
        download_2026()

    df = clean(load_raw())
    if use_cache_file:
        PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(PROCESSED_FILE, index=False)
    return df


def load_schema(path: Path = SCHEMA_FILE) -> pd.DataFrame:
    """Return the question texts (one row per column of the answers file)."""
    if not path.exists():
        download_2026()
    return pd.read_csv(path, encoding="utf-8")


def question_text(schema: pd.DataFrame, column: str) -> str:
    """Return the question wording for one column, or the column name if unknown."""
    row = schema.loc[schema["column"] == column, "question"]
    return html.unescape(str(row.iloc[0])) if len(row) else column
