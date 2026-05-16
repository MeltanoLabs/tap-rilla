"""Rilla tap class."""

from __future__ import annotations

import sys

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_rilla import streams

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class TapRilla(Tap):
    """Rilla tap class."""

    name = "tap-rilla"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="The API key to authenticate with the Rilla API",
            secret=True,
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            required=True,
            description="The earliest date from which to pull data (ISO 8601 format)",
        ),
        th.Property(
            "end_date",
            th.DateTimeType,
            description=(
                "The latest date from which to pull data (ISO 8601 format). If not "
                "specified, defaults to the current date and time."
            ),
        ),
        th.Property(
            "users",
            th.ArrayType(th.StringType),
            description=(
                "Optional array of user email addresses to filter conversations. Only "
                "applies to the conversations stream. If provided and not empty, only "
                "conversation data for those users will be returned. If not provided or "
                "empty, all conversation data is returned. Example: "
                "['user1@company.com', 'user2@company.com']"
            ),
        ),
        th.Property(
            "date_type",
            th.StringType,
            description=(
                "Date type to filter by: 'timeOfRecording' or 'processedDate'. Defaults "
                "to 'timeOfRecording' if not specified. Applies to the teams and users "
                "streams only; conversations always filters by 'processedDate'."
            ),
            allowed_values=[
                "timeOfRecording",
                "processedDate",
            ],
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams."""
        return [
            streams.ConversationsStream(tap=self),
            streams.TranscriptsStream(tap=self),
            streams.TeamsStream(tap=self),
            streams.UsersStream(tap=self),
        ]
