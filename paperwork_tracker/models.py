"""Data model for tracked documents."""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass
from datetime import date
from typing import Any, Dict, Iterable, Optional

DOCUMENT_TYPES: tuple = ("license", "registration", "insurance", "passport")

DEFAULT_ALERT_DAYS = 30


@dataclass
class Document:
    """A single renewable document record."""

    id: str
    type: str
    name: str
    issue_date: date
    expiry_date: date
    alert_days: int = DEFAULT_ALERT_DAYS
    notes: str = ""

    def validate(self) -> None:
        """Raise ``ValueError`` if the document holds invalid data."""
        if self.type not in DOCUMENT_TYPES:
            raise ValueError(
                f"Invalid document type: {self.type!r}. "
                f"Must be one of: {', '.join(DOCUMENT_TYPES)}"
            )
        if self.alert_days < 0:
            raise ValueError("alert_days must be a non-negative integer")
        if self.expiry_date < self.issue_date:
            raise ValueError(
                "expiry_date must not precede issue_date "
                f"({self.expiry_date} < {self.issue_date})"
            )
        if not self.name.strip():
            raise ValueError("name must not be empty")

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["issue_date"] = self.issue_date.isoformat()
        data["expiry_date"] = self.expiry_date.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        return cls(
            id=str(data["id"]),
            type=str(data["type"]),
            name=str(data["name"]),
            issue_date=date.fromisoformat(str(data["issue_date"])),
            expiry_date=date.fromisoformat(str(data["expiry_date"])),
            alert_days=int(data.get("alert_days", DEFAULT_ALERT_DAYS)),
            notes=str(data.get("notes", "")),
        )

    @classmethod
    def create(
        cls,
        type: str,
        name: str,
        issue_date: date,
        expiry_date: date,
        alert_days: int = DEFAULT_ALERT_DAYS,
        notes: str = "",
        doc_id: Optional[str] = None,
    ) -> "Document":
        doc = cls(
            id=doc_id or uuid.uuid4().hex,
            type=type,
            name=name,
            issue_date=issue_date,
            expiry_date=expiry_date,
            alert_days=alert_days,
            notes=notes,
        )
        doc.validate()
        return doc


def document_summary(doc: Document) -> Iterable[str]:
    """Yield human-readable summary lines for a document (not for storage)."""
    yield from (
        f"ID:    {doc.id}",
        f"Type:  {doc.type}",
        f"Name:  {doc.name}",
        f"Issue: {doc.issue_date.isoformat()}",
        f"Expiry:{doc.expiry_date.isoformat()}",
        f"Alert:{doc.alert_days} days before expiry",
        f"Notes: {doc.notes or '-'}",
    )
