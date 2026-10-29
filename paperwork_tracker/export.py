"""CSV export of document records."""

from __future__ import annotations

import csv
import io
from typing import Iterable, List, Optional

from datetime import date

from .dates import alert_window_start, classify
from .models import Document

COLUMNS: tuple = (
    "id",
    "type",
    "name",
    "issue_date",
    "expiry_date",
    "alert_days",
    "alert_start",
    "notes",
    "status",
)


def to_csv(
    documents: Iterable[Document],
    as_of: Optional[date] = None,
) -> str:
    """Render documents as CSV text, including a derived status column."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(COLUMNS)
    for doc in documents:
        writer.writerow(
            [
                doc.id,
                doc.type,
                doc.name,
                doc.issue_date.isoformat(),
                doc.expiry_date.isoformat(),
                doc.alert_days,
                alert_window_start(doc.expiry_date, doc.alert_days).isoformat(),
                doc.notes,
                classify(doc.expiry_date, doc.alert_days, as_of),
            ]
        )
    return buffer.getvalue()


def export_to_file(
    documents: List[Document],
    file_path: str,
    as_of: Optional[date] = None,
) -> int:
    """Write documents to ``file_path`` as CSV and return row count written."""
    text = to_csv(documents, as_of=as_of)
    with open(file_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    return text.count("\n") - 1 if documents else 0
