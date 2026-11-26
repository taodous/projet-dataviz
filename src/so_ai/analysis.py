"""Generic aggregations shared by the dashboard and the five axes.

All shares are computed among the respondents who answered the question
(missing answers excluded, see population.MISSING_RULE).

Multi-select columns store several answers separated by ";". They are split
explicitly with split_multiselect(); their shares do not sum to 100%.
"""

from __future__ import annotations

import pandas as pd

SEPARATOR = ";"


def split_multiselect(series: pd.Series) -> pd.Series:
    """One row per (respondent, answer). The index keeps the respondent's row label.

    Example: "A;B" becomes two rows "A" and "B" with the same index.
    Missing answers are dropped.
    """
    s = series.dropna().astype(str).str.split(SEPARATOR).explode().str.strip()
    return s[s != ""]


def answer_shares(
    df: pd.DataFrame,
    column: str,
    multi: bool = False,
    order: list[str] | None = None,
) -> pd.DataFrame:
    """Count and share of each answer among the respondents who answered `column`.

    Returns columns: answer, count, n, share (0-1).
    - single choice: shares sum to 1.
    - multi-select (multi=True): share = respondents who picked the answer / n,
      so shares do not sum to 1.
    `order` fixes the row order (e.g. a Likert scale); otherwise rows are sorted by share.
    """
    answers = df[column].dropna()
    n = int(len(answers))
    if multi:
        # One row per (respondent, answer); a respondent counts once per answer.
        pairs = split_multiselect(answers)
        pairs = pd.DataFrame({"respondent": pairs.index, "answer": pairs.values}).drop_duplicates()
        counts = pairs["answer"].value_counts()
    else:
        counts = answers.astype(str).value_counts()
    out = counts.rename("count").rename_axis("answer").reset_index()
    out["n"] = n
    out["share"] = out["count"] / n if n else 0.0
    if order is not None:
        out = out.set_index("answer").reindex(order).fillna({"count": 0, "share": 0.0, "n": n}).reset_index()
        out["count"] = out["count"].astype(int)
        out["n"] = out["n"].astype(int)
    else:
        out = out.sort_values("share", ascending=False, ignore_index=True)
    return out


def answer_shares_by_group(
    df: pd.DataFrame,
    column: str,
    group_col: str,
    multi: bool = False,
    order: list[str] | None = None,
    groups: list[str] | None = None,
) -> pd.DataFrame:
    """answer_shares() computed separately inside each group of `group_col`.

    Returns columns: group, answer, count, n, share. n is the group's own count
    of respondents who answered `column`.
    """
    frames = []
    group_values = groups if groups is not None else sorted(df[group_col].dropna().unique())
    for g in group_values:
        part = answer_shares(df[df[group_col] == g], column, multi=multi, order=order)
        part.insert(0, "group", g)
        frames.append(part)
    if not frames:
        return pd.DataFrame(columns=["group", "answer", "count", "n", "share"])
    return pd.concat(frames, ignore_index=True)


def share_of(df: pd.DataFrame, column: str, positive: list[str], multi: bool = False) -> tuple[float, int]:
    """Share of respondents who gave one of the `positive` answers, and the n behind it.

    Returns (share between 0 and 1, n). The share is NaN when n = 0.
    """
    answers = df[column].dropna().astype(str)
    n = int(len(answers))
    if n == 0:
        return float("nan"), 0
    if multi:
        hit = answers.str.split(SEPARATOR).apply(lambda items: any(i.strip() in positive for i in items))
    else:
        hit = answers.isin(positive)
    return float(hit.mean()), n
