"""Automatic integration tests for tap-rilla."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_rilla.tap import TapRilla

ONE_WEEK_AGO = datetime.now(tz=timezone.utc) - timedelta(days=7)


TestTapRilla = get_tap_test_class(
    TapRilla,
    config={
        "start_date": ONE_WEEK_AGO.isoformat(),
    },
    suite_config=SuiteConfig(
        max_records_limit=10,
    ),
)
