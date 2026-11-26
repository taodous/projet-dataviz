# Architecture

This is the first document to read. It maps each feature of the app to the files and functions
that carry it, and describes the data flow, the cache and the session state.

## Principle: analysis separated from the interface

| Layer | Folder | Contains | Never contains |
| --- | --- | --- | --- |
| Analysis | `src/so_ai/` | download, loading, cleaning, population filters, aggregations; pure functions `DataFrame -> DataFrame or number` | `import streamlit`, caching |
| Interface | `app/` | page layout, widgets, Plotly charts, captions, cache, session state | computations on the survey (beyond calling `so_ai`) |

`src/so_ai` is installed as a package (`pip install -r requirements.txt` runs `pip install -e .`),
so both the app and the tests import it with `from so_ai import ...`.

## Main features

| Feature | Files | Functions |
| --- | --- | --- |
| Download the data | `src/so_ai/download.py`, `scripts/download_data.py` | `download_2026()`, `download_file()` |
| Load and clean the data | `src/so_ai/data.py` | `load_survey()`, `load_raw()`, `clean()`, `add_uses_ai()`, `load_schema()`, `question_text()` |
| Population logic (shared by every page) | `src/so_ai/population.py` | `add_zone()`, `Filters`, `apply_filters()`, `answered()`, `n_respondents()`, `describe_filters()`, `caption()`, `is_small()`, texts `VOLUNTEER_WARNING` and `MISSING_RULE` |
| Generic aggregations | `src/so_ai/analysis.py` | `split_multiselect()`, `answer_shares()`, `answer_shares_by_group()`, `share_of()` |
| Main dashboard (message for Numeum) | `src/so_ai/dashboard.py`, `app/Home.py` | `INDICATORS`, `indicators_by_zone()`, `gap()`, `avoid_reasons_by_zone()` |
| Shared filters, captions, chart style | `app/components.py` | `get_survey()`, `sidebar_filters()`, `population_caption()`, `small_group_warning()`, `style()`, `dot_plot()`, `grouped_bars()`, `axis_header()` |
| Axis 1 to 5 | `src/so_ai/axes/<axis>.py`, `app/pages/<n>_<axis>.py` | written by each axis owner on `axis/<name>` |

## Data flow

```
GitHub archive (Git LFS, media.githubusercontent.com)
   |  download.download_2026()          scripts/download_data.py, or automatically at first app start
   v
data/raw/survey_results_public_2026.csv   (30,903 rows x 212 columns, git-ignored)
   |  data.load_raw()                   pandas.read_csv
   |  data.clean()                      + Zone (France / EU excl. France / rest of the world / country not given)
   |                                    + UsesAI (Yes / No, from the multi-select AISelect)
   v
data/processed/survey_2026.parquet        (written once, re-read on later starts, git-ignored)
   |  data.load_survey()
   v
app/components.get_survey()               st.cache_data: one copy in memory per server process
   |  population.apply_filters(df, Filters from the sidebar)
   v
filtered DataFrame
   |  dashboard.indicators_by_zone() / analysis.answer_shares...() / axes.<axis>.*()
   v
aggregated table (share, count, n)  ->  Plotly chart + population.caption() with the computed n
```

## Population rules (implemented in `population.py`)

- Caption under every figure: `Stack Overflow Developer Survey 2026, <population and filters>, n = <count> respondents`,
  with `n` computed from the filtered data (`n_respondents()` / `caption()`).
- Volunteer sample: `VOLUNTEER_WARNING` is shown on the dashboard, in the sidebar of every page and in the About section.
  Wording is always "respondents", never "developers".
- Missing answers are **excluded** from the denominator: each share is computed among respondents who
  answered the question shown (`answered()`, `share_of()`, `answer_shares()`). "Not sure" is kept as an answer.
- Zone comparisons leave out the respondents who did not answer the country question (shown as `Country not given`).
- Groups under `SMALL_GROUP` (30) respondents trigger a warning (`components.small_group_warning()`).
- Multi-select columns are split with `split_multiselect()`; their shares do not sum to 100% (`answer_shares(..., multi=True)`).

## Cache

| What | Where | Why |
| --- | --- | --- |
| Cleaned survey DataFrame | `components.get_survey()` with `st.cache_data` | parse the data once per server process |
| Question texts | `components.get_schema()` with `st.cache_data` | idem |
| Cleaned survey on disk | `data/processed/survey_2026.parquet` | faster restart (~1 s instead of parsing the CSV) |

Nothing is cached inside `src/so_ai`. Delete `data/processed/` after changing `clean()`.

## Session state

Only UI state is stored in `st.session_state`:

| Key | Content |
| --- | --- |
| `shared_employment`, `shared_code_main`, `shared_age` | values selected in the shared sidebar filters; they survive page changes |
| `widget_employment`, `widget_code_main`, `widget_age` | the widgets' own keys; Streamlit clears them when a page without the widget is shown, so `sidebar_filters()` restores them from `shared_*` |

Axis-specific filters stay local to their page (widget keys prefixed with the axis name, e.g. `trust_...`).

## How to add an axis view (for axis owners)

1. On your branch `axis/<name>`, write pure functions in `src/so_ai/axes/<name>.py` (reuse `analysis` and `population`).
2. Test them in `tests/test_<name>.py` with a small hand-made DataFrame.
3. In `app/pages/<n>_<Axis>.py`: call `ui.sidebar_filters()`, add your own filters, call your functions,
   draw the chart with `ui.style()`, and put `ui.population_caption(...)` under every figure.
4. Update this document (features table) in the same commit.
