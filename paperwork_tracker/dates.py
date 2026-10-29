"""Pure date logic for renewal alerts.

All functions accept an ``as_of`` date so the logic is deterministic and
easy to test without depending on the real wall clock.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

__all__ = [
    "days_until",
    "is_expired",
    "is_due_today",
    "is_due_soon",
    "needs_attention",
    "alert_window_start",
    "alert_window_end",
    "classify",
]


def _resolve_as_of(as_of: Optional[date]) -> date:
    return date.today() if as_of is None else as_of


def _check_alert_days(alert_days: int) -> int:
    if not isinstance(alert_days, int):
        raise TypeError("alert_days must be an integer")
    if isinstance(alert_days, bool):  # bool is an int subclass; reject it
        raise TypeError("alert_days must be an integer, not bool")
    if alert_days < 0:
        raise ValueError("alert_days must be a non-negative integer")
    return alert_days


def days_until(target: date, as_of: Optional[date] = None) -> int:
    """Whole days remaining until ``target``. Negative if already past."""
    as_of = _resolve_as_of(as_of)
    return (target - as_of).days


def is_expired(target: date, as_of: Optional[date] = None) -> bool:
    """True when ``target`` is strictly in the past (before ``as_of``)."""
    return days_until(target, as_of) < 0


def is_due_today(target: date, as_of: Optional[date] = None) -> bool:
    """True when ``target`` falls exactly on ``as_of``."""
    return days_until(target, as_of) == 0


def is_due_soon(
    target: date, alert_days: int, as_of: Optional[date] = None
) -> bool:
    """True when ``target`` is within the alert window, not yet expired."""
    alert_days = _check_alert_days(alert_days)
    delta = days_until(target, as_of)
    return 0 < delta <= alert_days


def needs_attention(
    expiry_date: date, alert_days: int, as_of: Optional[date] = None
) -> bool:
    """True if the document is expired, due today, or due soon.

    This is the union of the "red" and "yellow" alert states.
    """
    alert_days = _check_alert_days(alert_days)
    return days_until(expiry_date, as_of) <= alert_days


def alert_window_start(expiry_date: date, alert_days: int) -> date:
    """The date on which an upcoming-expiry alert first fires."""
    alert_days = _check_alert_days(alert_days)
    return expiry_date - timedelta(days=alert_days)


def alert_window_end(expiry_date: date) -> date:
    """The date on which the document is due (inclusive)."""
    return expiry_date


def classify(
    expiry_date: date, alert_days: int, as_of: Optional[date] = None
) -> str:
    """Return a stable status label for a document's renewal state.

    One of: ``"ok"``, ``"due_soon"``, ``"expires_today"``, ``"expired"``.
    """
    alert_days = _check_alert_days(alert_days)
    delta = days_until(expiry_date, as_of)
    if delta < 0:
        return "expired"
    if delta == 0:
        return "expires_today"
    if delta <= alert_days:
        return "due_soon"
    return "ok"
