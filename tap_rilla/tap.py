"""Rilla tap class."""

from __future__ import annotations

from singer_sdk import Tap, Stream
from singer_sdk import typing as th

from tap_rilla.streams import (
    ConversationsStream,
    TeamsStream,
    UsersStream,
)

STREAM_TYPES = [
    ConversationsStream,
    TeamsStream,
    UsersStream,
]


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
            th.DateType,
            description="The earliest date from which to pull data (YYYY-MM-DD format)",
        ),
        th.Property(
            "end_date",
            th.DateType,
            description="The latest date from which to pull data (YYYY-MM-DD format). If not specified, defaults to today.",
        ),
        th.Property(
            "users",
            th.ArrayType(th.StringType),
            description="Optional array of user email addresses to filter conversations. Only applies to the conversations stream. If provided and not empty, only conversation data for those users will be returned. If not provided or empty, all conversation data is returned. Example: ['user1@company.com', 'user2@company.com']",
        ),
        th.Property(
            "date_type",
            th.StringType,
            description="Date type to filter by: 'timeOfRecording' or 'processedDate'. Defaults to 'timeOfRecording' if not specified.",
            allowed_values=["timeOfRecording", "processedDate"],
        ),
    ).to_dict()
    
    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]