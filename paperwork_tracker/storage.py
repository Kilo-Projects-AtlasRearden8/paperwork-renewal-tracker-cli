"""Local JSON storage for documents.

Storage is intentionally plain JSON so the data is human-readable and
portable. Writes are atomic: data is staged to a temporary file in the same
directory and renamed into place.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from typing import List, Optional

from .models import Document


def default_data_dir() -> str:
    """Resolve a platform-appropriate, dependency-free data directory."""
    env = os.environ.get("PAPERWORK_TRACKER_DATA")
    if env:
        return env
    if os.name == "nt":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        return os.path.join(base, "PaperworkTracker")
    if sys.platform == "darwin":
        base = os.environ.get("HOME") or os.path.expanduser("~")
        return os.path.join(base, "Library", "Application Support", "PaperworkTracker")
    base = (
        os.environ.get("XDG_DATA_HOME")
        or os.path.join(os.path.expanduser("~"), ".local", "share")
    )
    return os.path.join(base, "paperwork_tracker")


def default_storage_path() -> str:
    return os.path.join(default_data_dir(), "documents.json")


class Storage:
    """Read/write a JSON document store at a given path."""

    def __init__(self, path: Optional[str] = None) -> None:
        self.path = os.path.abspath(path or default_storage_path())

    def _ensure_parent(self) -> None:
        parent = os.path.dirname(self.path)
        if parent:
            os.makedirs(parent, exist_ok=True)

    def exists(self) -> bool:
        return os.path.exists(self.path)

    def load(self) -> List[Document]:
        if not self.exists():
            return []
        with open(self.path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return [Document.from_dict(item) for item in data.get("documents", [])]

    def save(self, documents: List[Document]) -> None:
        self._ensure_parent()
        payload = {"documents": [doc.to_dict() for doc in documents]}
        fd, tmp_path = tempfile.mkstemp(
            prefix=".tmp_", suffix=".json", dir=os.path.dirname(self.path) or None
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            os.replace(tmp_path, self.path)
        except BaseException:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    def add(self, document: Document) -> None:
        documents = self.load()
        documents.append(document)
        self.save(documents)

    def get(self, doc_id: str) -> Optional[Document]:
        for doc in self.load():
            if doc.id == doc_id:
                return doc
        return None

    def delete(self, doc_id: str) -> bool:
        documents = self.load()
        filtered = [doc for doc in documents if doc.id != doc_id]
        if len(filtered) == len(documents):
            return False
        self.save(filtered)
        return True
