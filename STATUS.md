# STATUS

Paperwork Renewal Tracker CLI — status report.

## What was built

A local-first Python CLI for tracking document renewals, built for Asdale
Dynamics, LLC.

Package: `paperwork-renewal-tracker` (console command `paperwork-tracker`).

Source layout:
- `paperwork_tracker/dates.py` — pure date/alert logic (days until expiry,
  expired, due today, due soon, needs-attention, alert-window start,
  four-way status classify). Deterministic via an optional `as_of` date.
- `paperwork_tracker/models.py` — `Document` dataclass with validation,
  JSON (de)serialization, and the four supported types:
  license, registration, insurance, passport.
- `paperwork_tracker/storage.py` — local JSON storage with atomic writes
  (temp file + os.replace). Platform-appropriate default data dir, overridable
  with `--data` or the `PAPERWORK_TRACKER_DATA` env var.
- `paperwork_tracker/export.py` — CSV export (id, type, name, issue_date,
  expiry_date, alert_days, alert_start, notes, status).
- `paperwork_tracker/cli.py` — argparse CLI: add, list, show, alert, delete,
  export, plus --version and --data.
- `tests/test_dates.py` — 35 tests covering the date/alert logic, including
  boundary dates, leap years, year boundaries, and invalid alert_days.
- `pyproject.toml` — setuptools build, pytest config, console script entry
  point.
- `LICENSE` — MIT, copyright line exactly:
  `Copyright (c) 2026 Asdale Dynamics, LLC`.
- `README.md` — beginner-friendly usage guide crediting Asdale Dynamics, LLC.
- `.gitignore` — standard Python/gitignore entries.
- `STATUS.md` — this file.

No API keys, no secrets, no personal data, no network calls, no
`.github/workflows`.

## How to run

Install:

```bash
pip install .
```

(Or install into a venv to avoid touching system packages.)

Run the command:

```bash
paperwork-tracker --help
paperwork-tracker add --type license --name "Driver License" \
  --issue 2023-01-15 --expiry 2025-01-15 --alert-days 30
paperwork-tracker list
paperwork-tracker alert
paperwork-tracker export --output renewals.csv
paperwork-tracker show <document-id>
paperwork-tracker delete <document-id>
```

Use `--data /path/to/file.json` (or set `PAPERWORK_TRACKER_DATA`) to store
records in a custom location instead of the default.

Run tests:

```bash
pip install pytest
pytest
```

Build:

```bash
python -m build
```

## Verification results

- `pytest`: 35 passed (date/alert logic, boundaries, leap year, invalid
  inputs).
- `python -m py_compile` on all package modules: OK.
- `python -m build`: produced `dist/paperwork_renewal_tracker-1.0.0.tar.gz`
  and `dist/paperwork_renewal_tracker-1.0.0-py3-none-any.whl`.
- CLI smoke test (temp data dir): add / list / show / alert / export /
  delete all behave correctly; CSV export includes all columns and derived
  status; atomic JSON storage round-trips.

## Known gaps

- No `import` command to bulk-load records from CSV (export exists, import
  does not).
- No config file; storage path is set via `--data` or env var only.
- No per-command colored output or interactive prompts (kept plain for
  beginner friendliness).
- `mypy`/static type checking not run (mypy not installed in this
  environment); types are annotated but not statically verified.
- Default storage location follows XDG conventions on Linux but has not been
  tested on Windows or macOS.
