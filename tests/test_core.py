"""Tests of the analysis functions on small hand-made tables (no download needed)."""

import math

import pandas as pd
import pytest

from so_ai import population as pop
from so_ai.analysis import answer_shares, answer_shares_by_group, share_of, split_multiselect
from so_ai.dashboard import INDICATORS, gap, indicators_by_zone
from so_ai.data import add_uses_ai, clean


@pytest.fixture
def survey():
    return clean(pd.DataFrame({
        "Country": ["France", "France", "Germany", "India", None, "France"],
        "Employment": ["Employed", "Student", "Employed", "Employed", "Employed", "Employed"],
        "CodeMain": ["A", "A", "A", "B", "A", "A"],
        "Age": ["25-34 years old"] * 6,
        "AISelect": ["General-purpose AI chat tools", "I don’t use AI tools",
                     "AI coding assistants or coding agents;General-purpose AI chat tools",
                     None, "General-purpose AI chat tools", None],
        "AIAvoid": ["I do not avoid using AI at work or school", "Moral or ethical concerns",
                    "I do not avoid using AI at work or school", None, None, "Environmental concerns"],
        "AISentiment": ["Very favorable", None, "Neutral", "Somewhat favorable", None, "Very unfavorable"],
        "LearnAI": ["Yes, at work", "No", "Yes, on my own", None, None, "No"],
        "AITrust": [None] * 6,
        "AIUse": [None] * 6,
    }))


def test_zone_mapping(survey):
    assert survey["Zone"].tolist() == [pop.FRANCE, pop.FRANCE, pop.EU_EXCL_FR,
                                       pop.REST_OF_WORLD, pop.NO_COUNTRY, pop.FRANCE]


def test_uses_ai_keeps_missing_as_missing(survey):
    assert survey["UsesAI"].iloc[:3].tolist() == ["Yes", "No", "Yes"]
    assert pd.isna(survey["UsesAI"].iloc[3])
    assert survey["UsesAI"].isna().sum() == 2


def test_apply_filters_and_n(survey):
    f = pop.Filters(zones=[pop.FRANCE], employment=["Employed"])
    out = pop.apply_filters(survey, f)
    assert len(out) == 2
    assert pop.n_respondents(out, "AISentiment") == 2
    assert pop.n_respondents(out, "AISelect") == 1


def test_empty_filters_keep_everyone(survey):
    assert len(pop.apply_filters(survey, pop.Filters())) == len(survey)


def test_caption_has_computed_n(survey):
    text = pop.caption(survey[survey.Zone == pop.FRANCE], "respondents in France", "AISentiment")
    assert text.startswith("Stack Overflow Developer Survey 2026, respondents in France")
    assert text.endswith("n = 2 respondents")


def test_split_multiselect():
    s = split_multiselect(pd.Series(["A;B", None, "B"]))
    assert s.tolist() == ["A", "B", "B"]
    assert s.index.tolist() == [0, 0, 2]


def test_answer_shares_single_sums_to_one(survey):
    out = answer_shares(survey, "AIAvoid")
    assert out["n"].iloc[0] == 4
    assert math.isclose(out["share"].sum(), 1.0)


def test_answer_shares_multi_does_not_sum_to_one(survey):
    out = answer_shares(survey, "AISelect", multi=True).set_index("answer")
    assert out.loc["General-purpose AI chat tools", "count"] == 3
    assert out["n"].iloc[0] == 4
    assert out["share"].sum() > 1


def test_answer_shares_fixed_order_fills_zero(survey):
    out = answer_shares(survey, "AISentiment", order=["Very favorable", "Somewhat unfavorable"])
    assert out["answer"].tolist() == ["Very favorable", "Somewhat unfavorable"]
    assert out["count"].tolist() == [1, 0]


def test_share_of_excludes_missing(survey):
    share, n = share_of(survey[survey.Zone == pop.FRANCE], "AIAvoid",
                        ["I do not avoid using AI at work or school"])
    assert n == 3 and math.isclose(share, 1 / 3)


def test_share_of_empty_is_nan():
    share, n = share_of(pd.DataFrame({"x": [None]}), "x", ["a"])
    assert n == 0 and math.isnan(share)


def test_by_group(survey):
    out = answer_shares_by_group(survey, "LearnAI", "Zone", groups=[pop.FRANCE])
    assert set(out["group"]) == {pop.FRANCE}
    assert out.set_index("answer").loc["No", "count"] == 2


def test_indicators_by_zone_shape_and_gap(survey):
    table = indicators_by_zone(survey)
    assert len(table) == len(INDICATORS) * len(pop.ZONES)
    # not_avoid: France 1/3, EU 1/1 -> gap of -66.7 points
    assert math.isclose(gap(table, "not_avoid", pop.FRANCE, pop.EU_EXCL_FR), -200 / 3)


def test_add_uses_ai_detects_no_ai_in_multiselect():
    out = add_uses_ai(pd.DataFrame({"AISelect": ["X;I don’t use AI tools"]}))
    assert out["UsesAI"].iloc[0] == "No"
