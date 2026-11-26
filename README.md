# AI at work: France vs. the EU (Stack Overflow Developer Survey 2026)

A Streamlit analytics app, built as the final project of the ECE course *Data Visualisation*.

- **Theme:** AI
- **Sponsor:** [Numeum](https://numeum.fr), the trade association of French digital companies
- **Message of the main dashboard:** respondents in France use AI at work less, avoid it more
  and have learned it at work less often than respondents in the rest of the EU. Their
  reasons are concerns (skills, ethics, environment), not lack of access, so employer-led
  training and clear responsible-use guidance are the lever.

> The survey is answered by volunteers. All figures describe **respondents**, not all developers.

## Run it from a fresh clone

Requires Python 3.10 or later and about 300 MB of disk space for the data.

```bash
git clone https://github.com/taodous/projet-dataviz.git
cd projet-dataviz

python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate

pip install -r requirements.txt          # also installs our package src/so_ai in editable mode
python scripts/download_data.py          # downloads the 2026 survey into data/raw/ (~120 MB)
streamlit run app/Home.py
```

The download step is optional: if `data/raw/` is empty, the app downloads the data on its first start.
The first start also writes a Parquet copy to `data/processed/` so the next starts are faster.

Run the tests:

```bash
pytest
```

## Repository layout

```
app/            interface only: Home.py (main dashboard), components.py, pages/1_..5_ (one per axis)
src/so_ai/      analysis only (no Streamlit): download, data, population, analysis, dashboard, axes/
scripts/        download_data.py
notebooks/      exploration notebooks
docs/           architecture.md (read first), mockup.md
tests/          tests of the analysis functions
data/           raw/ and processed/, git-ignored, never committed
```

See [`docs/architecture.md`](docs/architecture.md) for the features, the data flow, the cache and the session state.

## Group and axes

| Axis | Question for Numeum | Owner | Branch |
| --- | --- | --- | --- |
| 1. Adoption and usage | Who uses AI at work, which tools, and how often? | TBD | `axis/adoption` |
| 2. Trust and verification | How far do respondents trust AI output, and how do they check it? | TBD | `axis/trust` |
| 3. Productivity by task | For which development tasks does AI help, and for which does it not? | TBD | `axis/productivity` |
| 4. Employers and governance | How do organisations frame, equip and measure AI use? | TBD | `axis/organisations` |
| 5. Skills and reluctance | How do respondents learn AI, and what holds them back? | TBD | `axis/skills` |

## Data

Stack Overflow Developer Survey 2026, public answers (`survey_results_public.csv`) and schema,
from the [Stack Overflow survey archive](https://github.com/StackExchange/Survey/tree/main/packages/archive/2026).
Official results: <https://survey.stackoverflow.co/2026>. The 2025 survey is not used.
