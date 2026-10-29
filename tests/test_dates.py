"""Tests for the date/alert logic in paperwork_tracker.dates.

These tests are deterministic: they pass an explicit ``as_of`` date so the
results do not depend on the real wall clock.
"""

from datetime import date

import pytest

from paperwork_tracker.dates import (
    alert_window_start,
    classify,
    days_until,
    is_due_soon,
    is_due_today,
    is_expired,
    needs_attention,
)

TODAY = date(2026, 6, 15)


class TestDaysUntil:
    def test_future(self):
        assert days_until(date(2026, 6, 20), TODAY) == 5

    def test_past(self):
        assert days_until(date(2026, 6, 10), TODAY) == -5

    def test_same_day(self):
        assert days_until(TODAY, TODAY) == 0

    def test_next_year_boundary(self):
        assert days_until(date(2027, 1, 1), date(2026, 12, 31)) == 1

    def test_leap_year(self):
        # 2024 is a leap year
        assert days_until(date(2024, 3, 1), date(2024, 2, 1)) == 29


class TestIsExpired:
    def test_past_is_expired(self):
        assert is_expired(date(2026, 1, 1), TODAY) is True

    def test_today_is_not_expired(self):
        assert is_expired(TODAY, TODAY) is False

    def test_future_is_not_expired(self):
        assert is_expired(date(2026, 7, 1), TODAY) is False

    def test_default_as_of_uses_today(self):
        # Should not crash and returns a bool.
        assert isinstance(is_expired(date(2020, 1, 1)), bool)


class TestIsDueToday:
    def test_true_on_same_day(self):
        assert is_due_today(TODAY, TODAY) is True

    def test_false_other_days(self):
        assert is_due_today(date(2026, 6, 14), TODAY) is False
        assert is_due_today(date(2026, 6, 16), TODAY) is False


class TestIsDueSoon:
    def test_within_window(self):
        # 30-day window; due in 10 days -> soon
        assert is_due_soon(date(2026, 6, 25), 30, TODAY) is True

    def test_exactly_at_window_edge_is_soon(self):
        assert is_due_soon(date(2026, 7, 15), 30, TODAY) is True

    def test_one_day_past_window_not_soon(self):
        assert is_due_soon(date(2026, 7, 16), 30, TODAY) is False

    def test_expired_not_soon(self):
        assert is_due_soon(date(2026, 6, 10), 30, TODAY) is False

    def test_due_today_not_soon(self):
        assert is_due_soon(TODAY, 30, TODAY) is False

    def test_zero_alert_days_no_soon(self):
        assert is_due_soon(date(2026, 6, 16), 0, TODAY) is False

    def test_negative_alert_days_raises(self):
        with pytest.raises(ValueError):
            is_due_soon(date(2026, 7, 1), -1, TODAY)

    def test_bool_alert_days_raises(self):
        with pytest.raises(TypeError):
            is_due_soon(date(2026, 7, 1), True, TODAY)

    def test_non_int_alert_days_raises(self):
        with pytest.raises(TypeError):
            is_due_soon(date(2026, 7, 1), "30", TODAY)


class TestNeedsAttention:
    def test_expired_needs_attention(self):
        assert needs_attention(date(2026, 1, 1), 30, TODAY) is True

    def test_due_today_needs_attention(self):
        assert needs_attention(TODAY, 30, TODAY) is True

    def test_within_window_needs_attention(self):
        assert needs_attention(date(2026, 6, 20), 30, TODAY) is True

    def test_outside_window_no_attention(self):
        assert needs_attention(date(2026, 8, 1), 30, TODAY) is False

    def test_negative_alert_days_raises(self):
        with pytest.raises(ValueError):
            needs_attention(date(2026, 7, 1), -5, TODAY)


class TestClassify:
    def test_expired(self):
        assert classify(date(2026, 1, 1), 30, TODAY) == "expired"

    def test_expires_today(self):
        assert classify(TODAY, 30, TODAY) == "expires_today"

    def test_due_soon(self):
        assert classify(date(2026, 6, 20), 30, TODAY) == "due_soon"

    def test_due_soon_at_window_edge(self):
        assert classify(date(2026, 7, 15), 30, TODAY) == "due_soon"

    def test_ok(self):
        assert classify(date(2026, 8, 1), 30, TODAY) == "ok"

    def test_ok_at_window_plus_one(self):
        assert classify(date(2026, 7, 16), 30, TODAY) == "ok"

    def test_negative_alert_days_raises(self):
        with pytest.raises(ValueError):
            classify(date(2026, 7, 1), -5, TODAY)


class TestAlertWindowStart:
    def test_computes_start_date(self):
        assert alert_window_start(date(2026, 7, 15), 30) == date(2026, 6, 15)

    def test_zero_alert_days_starts_on_expiry(self):
        assert alert_window_start(date(2026, 7, 15), 0) == date(2026, 7, 15)

    def test_negative_alert_days_raises(self):
        with pytest.raises(ValueError):
            alert_window_start(date(2026, 7, 15), -1)
