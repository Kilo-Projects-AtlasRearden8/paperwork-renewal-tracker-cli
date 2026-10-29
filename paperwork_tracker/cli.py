"""Command-line interface for the Paperwork Renewal Tracker.

A local-first, no-keys CLI for tracking document renewals
(licenses, registration, insurance, passports) with due-date alerts
and CSV export.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from typing import List, Optional, Sequence

from .dates import (
    alert_window_start,
    classify,
    days_until,
    needs_attention,
)
from .export import export_to_file, to_csv
from .models import DEFAULT_ALERT_DAYS, DOCUMENT_TYPES, Document
from .storage import Storage, default_storage_path


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date. Use YYYY-MM-DD (e.g. 2025-01-15)."
        ) from exc


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paperwork-tracker",
        description=(
            "Track document renewals locally: licenses, registration, "
            "insurance, and passports. Stores records in a local JSON file "
            "and can export to CSV. No account, no keys, no cloud."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version="paperwork-tracker 1.0.0",
    )
    parser.add_argument(
        "--data",
        default=None,
        help=(
            "Path to the local JSON storage file (default: "
            + default_storage_path()
            + ")."
        ),
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add", help="Add a new document to track.")
    p_add.add_argument("--type", required=True, choices=list(DOCUMENT_TYPES),
                       help="Document type.")
    p_add.add_argument("--name", required=True, help="Document name / label.")
    p_add.add_argument("--issue", required=True, type=_parse_date,
                       help="Issue date (YYYY-MM-DD).")
    p_add.add_argument("--expiry", required=True, type=_parse_date,
                       help="Expiry / renewal due date (YYYY-MM-DD).")
    p_add.add_argument("--alert-days", type=int, default=DEFAULT_ALERT_DAYS,
                       help="Days before expiry to start alerting (default 30).")
    p_add.add_argument("--notes", default="", help="Optional notes.")
    p_add.set_defaults(func=_cmd_add)

    # list
    p_list = sub.add_parser("list", help="List all tracked documents.")
    p_list.add_argument("--type", choices=list(DOCUMENT_TYPES),
                        help="Filter by document type.")
    p_list.add_argument("--sort", choices=["expiry", "name", "type"],
                        default="expiry", help="Sort order (default expiry).")
    p_list.set_defaults(func=_cmd_list)

    # show
    p_show = sub.add_parser("show", help="Show details for one document.")
    p_show.add_argument("id", help="Document ID.")
    p_show.set_defaults(func=_cmd_show)

    # alert
    p_alert = sub.add_parser("alert", help="Show documents needing attention.")
    p_alert.add_argument("--days", type=int, default=DEFAULT_ALERT_DAYS,
                         help="Alert window in days (default 30).")
    p_alert.set_defaults(func=_cmd_alert)

    # delete
    p_delete = sub.add_parser("delete", help="Delete a tracked document.")
    p_delete.add_argument("id", help="Document ID.")
    p_delete.set_defaults(func=_cmd_delete)

    # export
    p_export = sub.add_parser("export", help="Export all records to CSV.")
    p_export.add_argument("--output", default=None,
                          help="Output CSV file path (default: stdout).")
    p_export.set_defaults(func=_cmd_export)

    return parser


def _storage(args: argparse.Namespace) -> Storage:
    return Storage(args.data)


def _cmd_add(args: argparse.Namespace) -> int:
    store = _storage(args)
    try:
        doc = Document.create(
            type=args.type,
            name=args.name,
            issue_date=args.issue,
            expiry_date=args.expiry,
            alert_days=args.alert_days,
            notes=args.notes,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    store.add(doc)
    alert_start = alert_window_start(doc.expiry_date, doc.alert_days)
    print(f"Added document {doc.id}: {doc.name} ({doc.type})")
    print(f"  Expires {doc.expiry_date.isoformat()} "
          f"(alerts start {alert_start.isoformat()})")
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    store = _storage(args)
    documents = store.load()
    if args.type:
        documents = [d for d in documents if d.type == args.type]

    if args.sort == "name":
        documents.sort(key=lambda d: d.name.lower())
    elif args.sort == "type":
        documents.sort(key=lambda d: (d.type, d.name.lower()))
    else:
        documents.sort(key=lambda d: d.expiry_date)

    if not documents:
        print("No tracked documents.")
        return 0

    today = date.today()
    print(f"{'ID':<10} {'Type':<14} {'Name':<24} {'Expiry':<12} {'Status'}")
    print("-" * 74)
    for d in documents:
        status = classify(d.expiry_date, d.alert_days, today)
        print(f"{d.id:<10} {d.type:<14} {d.name:<24} {d.expiry_date.isoformat():<12} {status}")
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    store = _storage(args)
    doc = store.get(args.id)
    if doc is None:
        print(f"Error: no document with id {args.id}", file=sys.stderr)
        return 1
    today = date.today()
    status = classify(doc.expiry_date, doc.alert_days, today)
    print(f"ID:      {doc.id}")
    print(f"Type:    {doc.type}")
    print(f"Name:    {doc.name}")
    print(f"Issue:   {doc.issue_date.isoformat()}")
    print(f"Expiry:  {doc.expiry_date.isoformat()}")
    print(f"Alerts:  {doc.alert_days} days before expiry")
    print(f"Status:  {status} (as of {today.isoformat()})")
    print(f"Notes:   {doc.notes or '-'}")
    return 0


def _cmd_alert(args: argparse.Namespace) -> int:
    store = _storage(args)
    documents = store.load()
    today = date.today()
    alert_days = args.days
    needing = [
        d for d in documents
        if needs_attention(d.expiry_date, alert_days, today)
    ]
    needing.sort(key=lambda d: d.expiry_date)
    if not needing:
        print("All clear. No documents need attention.")
        return 0
    print(f"Documents needing attention (alert window: {alert_days} days):")
    print(f"{'ID':<10} {'Type':<14} {'Name':<24} {'Expiry':<12} {'Status'}")
    print("-" * 74)
    for d in needing:
        status = classify(d.expiry_date, d.alert_days, today)
        days_left = days_until(d.expiry_date, today)
        label = f"{days_left} day(s)" if days_left >= 0 else "overdue"
        print(f"{d.id:<10} {d.type:<14} {d.name:<24} {d.expiry_date.isoformat():<12} {status} ({label})")
    return 0


def _cmd_delete(args: argparse.Namespace) -> int:
    store = _storage(args)
    if store.delete(args.id):
        print(f"Deleted document {args.id}.")
        return 0
    print(f"Error: no document with id {args.id}", file=sys.stderr)
    return 1


def _cmd_export(args: argparse.Namespace) -> int:
    store = _storage(args)
    documents = store.load()
    text = to_csv(documents, as_of=date.today())
    if args.output:
        n = export_to_file(documents, args.output, as_of=date.today())
        print(f"Exported {n} document(s) to {args.output}.")
    else:
        sys.stdout.write(text)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
