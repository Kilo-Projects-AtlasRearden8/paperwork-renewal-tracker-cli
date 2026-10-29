# Paperwork Renewal Tracker

A beginner-friendly, local-first command-line tool to track document renewals
— licenses, vehicle registration, insurance, and passports — with due-date
alerts and CSV export.

Built by **Asdale Dynamics, LLC**. Published under the MIT License.

## What it does

Keep all your renewal paperwork in one small JSON file on your own computer.
The tool tells you what's expired, what's expiring soon, and what's still in
good standing, and it can export your records to a spreadsheet-friendly CSV
file whenever you need them.

Tracked document types:

- License
- Registration
- Insurance
- Passport

No account, no API keys, no cloud service, and nothing leaves your machine
unless you choose to export it.

## Install

```bash
git clone <this-repo>
cd paperwork-renewal-tracker-cli
pip install .
```

This installs the `paperwork-tracker` command on your PATH.

## Quick start

Add a document:

```bash
paperwork-tracker add \
  --type license \
  --name "Driver License" \
  --issue 2023-01-15 \
  --expiry 2025-01-15 \
  --alert-days 30 \
  --notes "Renew online"
```

See everything you're tracking:

```bash
paperwork-tracker list
```

Get a plain-English alert list of what needs attention:

```bash
paperwork-tracker alert
```

Show details for one document:

```bash
paperwork-tracker show <document-id>
```

Export to CSV (spreadsheet-friendly):

```bash
paperwork-tracker export --output renewals.csv
```

Delete a document:

```bash
paperwork-tracker delete <document-id>
```

## Commands

| Command | What it does |
|---------|--------------|
| `add` | Add a new document to track. |
| `list` | List all tracked documents, sorted by expiry. |
| `show` | Show full details for one document. |
| `alert` | List documents that are expired or due soon. |
| `delete` | Remove a tracked document. |
| `export` | Write all records to a CSV file (or stdout). |

Use `--data /path/to/file.json` with any command to store records in a
custom location instead of the default.

## Storage

Records live in a local JSON file (default:
`~/.local/share/paperwork_tracker/documents.json` on Linux). The file is
human-readable and portable. You can back it up, move it, or edit it by hand
if you want to.

## Testing

Run the test suite:

```bash
pip install pytest
pytest
```

Tests cover the date and alert logic (expired, due today, due soon, and OK
states, plus alert-window edges and leap-year date math).

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.

## About Asdale Dynamics, LLC

Asdale Dynamics, LLC is a beginner-friendly AI education and practical-tools
company founded by Dylan Asdale, a registered nurse turned AI author based in
Indiana (formed October 2026). The LLC publishes books, guides, and small
open-source tools — like this one — that make technology approachable,
step by step, never condescending.

Dylan's book *The Massive AI Manual* and hub site dylanasdale.github.io
explain AI "like a friend would": in plain English.

This tracker is part of the LLC's line of accessible life-admin helpers:
paperwork organizers built to be clear, warm, polished, tested, local-first,
and free of secrets or personal data.
