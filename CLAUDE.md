# CLAUDE.md: Stack Overflow 2026 Analytics App

Final project of the ECE course "Data Visualisation (English)" (DataScientist.fr).
A group of 5 builds a Streamlit analytics app on the Stack Overflow Developer Survey 2026,
for a sponsor of the French market. Read this file before any change.

## Project frame (to fill in by the group)

| Item | Value |
| --- | --- |
| Theme | AI |
| Sponsor | Numeum (trade association of French digital companies) |
| Message of the main dashboard | Respondents in France use AI at work less, avoid it more and learned it at work less often than EU peers; concerns, not access, drive it, so employer-led training and responsible-use guidance are the lever. |
| Axis 1 / owner | Adoption and usage (`axis/adoption`) / TBD |
| Axis 2 / owner | Trust and verification (`axis/trust`) / TBD |
| Axis 3 / owner | Productivity by task (`axis/productivity`) / TBD |
| Axis 4 / owner | Employers and governance (`axis/organisations`) / TBD |
| Axis 5 / owner | Skills and reluctance (`axis/skills`) / TBD |
| Compare with 2025 | No |

Every analysis choice serves the sponsor and the theme above. Ask before adding a view that does not.

## What the app must do

1. Open on a **main dashboard** that carries **one message** for the sponsor.
2. Offer **five axes** of deeper analysis, one per member. Each axis has its **own filters and views**,
   designed so the reader can explore their own questions. Streamlit pages are allowed.
3. Show the **population behind every figure**: who, which year, how many respondents.
4. Use the **2026** data. Optional: compare with 2025, only through an explicit harmonisation (see below).

## Non-negotiable requirements

- All work is on GitHub, in a repository created by the group and shared with the trainer from day 1.
- The app runs **from a fresh clone** with the commands in the README. Test this before each merge.
- The technical architecture is documented in the repository (see `docs/architecture.md`).
- **The analysis is separated from the interface.**
- The main dashboard carries a message; each of the 5 axes has its own filters and views.
- Every figure shows its population.
- Every 2025 comparison relies on an explicit harmonisation of questions and answers, written in the repo.

## Rigour rules (apply to every figure, table and sentence)

- **Population caption on every figure**: `Stack Overflow Developer Survey 2026, <population and filters>, n = <count> respondents`.
  The count `n` is computed from the filtered data, never hard-coded.
- **Volunteer sample**: respondents chose to answer an online survey. Say so in the app (dashboard and
  about section). Never write "X% of developers"; write "X% of respondents" (or "of the respondents in France", etc.).
- Show `n` next to small groups, and do not draw conclusions from very small groups.
- Missing answers: state how they are handled (excluded, shown as "No answer") and keep it consistent.
- Multi-select columns (values separated by `;`): split them explicitly; shares of multi-select answers do not sum to 100%.

## Data

- 2026 answers: `survey_results_public.csv`, questions: `survey_results_schema.csv`
  (Stack Overflow GitHub archive, `packages/archive/2026`).
- Download URL (Git LFS, ~120 MB):
  `https://media.githubusercontent.com/media/StackExchange/Survey/main/packages/archive/2026/survey_results_public.csv`.
  Never use the GitHub "raw" link: it only returns the LFS pointer.
- 2025 (optional): same archive, folder `packages/archive/2025`, files `results.csv`, `schema.csv`, questionnaire.
- Official results for reference: `survey.stackoverflow.co/2026` (and `/2025`).
- **The data is never committed.** The project downloads it with a script (e.g. `scripts/download_data.py`)
  into `data/raw/`, which is in `.gitignore`. Derived files (e.g. Parquet subsets) go to `data/processed/`, also ignored.

## Architecture rules

- `src/<package>/` holds the analysis: loading, cleaning, population filters, aggregations.
  Pure functions that take a DataFrame and return a DataFrame or a number. **No `import streamlit` here.**
- `app/` holds the interface only: layout, widgets, charts, captions. It calls functions from `src/`.
- One shared module for the population logic (filters, `n` computation, caption text). All axes use it.
- Caching: load and clean the data once with `st.cache_data`. Do not cache in `src/`.
- Session state: only UI state (selected filters, shared filters between pages) in `st.session_state`.
- Notebooks for exploration live in `notebooks/` and are committed (outputs cleared if large).
- Suggested layout (one possible shape, adapt it):

```
app/            Home.py (main dashboard), pages/1_<axis>.py ... pages/5_<axis>.py
src/<package>/  data.py, population.py, harmonisation.py, axes/<axis>.py
scripts/        download_data.py
notebooks/      exploration notebooks, one per member if useful
docs/           architecture.md, harmonisation_2025_2026.md, mockup
tests/          tests of the analysis functions
data/           raw/ and processed/ (git-ignored)
```

## Documentation to keep up to date

- `README.md`: purpose, sponsor and message, setup and run commands from a fresh clone
  (environment, data download, `streamlit run ...`), group members and their axis.
- `docs/architecture.md` (the first document the jury reads):
  main features; for each feature the files and functions that carry it; data flow from the raw file
  to each view; what is cached; what is kept in session state.
- `docs/harmonisation_2025_2026.md` (only if 2025 is used): for each compared question, the 2025 and 2026
  column names, the answer mapping, and the answers dropped or merged. The mapping is also in code.

## Git workflow

- The **common core** (download, loading, population logic, main dashboard) is built together on `main`.
- Each axis lives on its own branch (e.g. `axis/<name>`), carried by its owner, then merged into `main`.
- The history is graded: it must show who did what. Small, clear commits with conventional messages
  (`feat:`, `fix:`, `docs:`, `refactor:`).
- When helping a member on their axis, work on that member's branch. Do not commit one member's axis
  under another member's name, and do not squash the history.
- Never commit data files, secrets or large notebook outputs.

## Working rules for Claude

- Keep code simple and commented: every member must be able to explain the whole app at the defence,
  and the jury asks for a live change.
- Before adding a chart, check: does it serve the sponsor message, does it show its population caption,
  is the logic in `src/`?
- Prefer clear chart types (bar, line, dot plot) with sorted categories, readable labels and units.
- After a change, run the app and the tests; check the fresh-clone path when touching setup or data loading.
- Update `docs/architecture.md` in the same commit as any new feature, file or data flow change.

## Steps of the project

1. Take over the subject: explore the 2026 data, its documentation and the official results.
2. Frame: sponsor, dashboard message, five axes and owners, mockup.
3. Design the architecture: features, files, data flow, cache, session data.
4. Build the common core: loading, population, shared logic, main dashboard.
5. Deepen: one axis per member.
6. Check and document: population shown everywhere, reproducibility, choices explained.
7. Bonus: deploy online (e.g. Streamlit Community Cloud; the app downloads or prepares the data at start).

## Deliverables (one member submits for the group)

1. Link to the GitHub repository, shared with the trainer: app, README, architecture doc,
   exploration notebooks, harmonisation (if 2025 is used). No data committed.
2. Two screenshots: the main dashboard, and one of the five axes.
3. Bonus: public link of the deployed app.

## Defence and grading

- Defence: 20 minutes. Demo 5 min (main dashboard and its message, then one axis live).
  Questions 15 min: each member explains their axis, then a part of the app drawn at random;
  the jury checks the history and asks for a live change.
- Grading: app 15 points, defence 5 points, online deployment +3 bonus.
  Both grades carry an individual coefficient based on each member's involvement.

## Definition of done (check before the submission)

- [ ] Fresh clone, README commands only: the app starts and the data downloads.
- [ ] Main dashboard states one message for the sponsor.
- [ ] Five axes, each with its own filters and views, each with a clear owner in the history.
- [ ] Every figure has a population caption with a computed `n`.
- [ ] Volunteer-sample warning visible; no "share of all developers" wording.
- [ ] No Streamlit import in `src/`; analysis functions are tested.
- [ ] `docs/architecture.md` matches the code.
- [ ] 2025 comparisons (if any) follow `docs/harmonisation_2025_2026.md`.
- [ ] No data, secrets or heavy outputs in the repository.
