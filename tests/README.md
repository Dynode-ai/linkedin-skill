# Tests

All fixtures are synthetic. "Priya Raman" and "Maya Chen" are fictional people, and no real LinkedIn data is stored in this repo.

```bash
python tests/make_fixtures.py          # generate a fake data archive (.zip) and analytics export (.xlsx)
python -m unittest discover tests -v   # script regression tests
```

| Path | What it is |
|---|---|
| `make_fixtures.py` | Builds `fixtures/priya/`: a LinkedIn-style data archive (Profile, Positions, Skills, Shares, Comments, Connections with the real "Notes:" preamble, Recommendations) and a 5-sheet `AggregateAnalytics_*.xlsx` (Discovery, Engagement, Top posts as two side-by-side tables, Followers, Demographics). Post IDs encode timestamps the way LinkedIn's do, and share and activity URNs differ, as in real exports. |
| `test_scripts.py` | Checks the post checker (AI tells, bait, placeholders, the fold, field limits) and the data pipeline (zip and xlsx parsing, the text-to-metrics join, stats, voice, dashboard, post dating). |
| `fixtures/maya/` | A job seeker's profile (PDF-export text) and two target job descriptions, for audit evals. |
| `fixtures/*.md` | A sloppy AI-style post and a good post, for checker tests. |
| `evals/evals.json` | End-to-end prompts used to compare Claude with and without the skill. |

## End-to-end evals

Each eval runs a headless Claude Code session in a scratch folder, once with the plugin loaded and once without:

```bash
claude -p "<prompt from evals.json>" --plugin-dir ./plugins/linkedin --allowedTools "Read,Write,Edit,Glob,Grep,Bash,WebSearch,WebFetch,Skill"
```

Copy the eval's input files into the scratch folder first (`.zip`/`.xlsx` go in `data/`).
