"""Stream type classes for tap-rilla."""

from __future__ import annotations

import functools
import sys
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from singer_sdk import typing as th
from singer_sdk.pagination import BasePageNumberPaginator

from tap_rilla.client import RillaStream

if sys.version_info >= (3, 11):
    from http import HTTPMethod
else:
    from backports.datetime_fromisoformat import MonkeyPatch  # ty: ignore[unresolved-import]
    from backports.httpmethod import HTTPMethod  # ty: ignore[unresolved-import]

    MonkeyPatch.patch_fromisoformat()

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    import requests
    from singer_sdk.helpers.types import Context


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


@functools.cache
def _get_date_range(*, start_date: str, end_date: str | None) -> tuple[str, str]:
    """Get the date range from the config."""
    start_date_val = datetime.fromisoformat(start_date)
    end_date_val = datetime.fromisoformat(end_date) if end_date is not None else datetime.now(timezone.utc)

    # Use ISO 8601 format for dates
    return start_date_val.strftime(DATETIME_FORMAT), end_date_val.strftime(DATETIME_FORMAT)


class RillaPageNumberPaginator(BasePageNumberPaginator):
    """Paginator for the Rilla conversations stream."""

    @override
    def get_next(self, response: requests.Response) -> int | None:
        """Get the next page number."""
        data = response.json()
        current_page: int = data.get("currentPage", 1)
        total_pages: int = data.get("totalPages", 1)
        return current_page + 1 if current_page < total_pages else None


class ConversationsStream(RillaStream):
    """Stream for conversations data."""

    name = "conversations"
    path = "/export/conversations"
    primary_keys = ("conversationId",)
    replication_key = None
    records_jsonpath = "$.conversations[*]"
    http_method = HTTPMethod.POST

    schema = th.PropertiesList(
        th.Property("conversationId", th.StringType, description="The conversation ID"),
        th.Property("recordingId", th.StringType, description="The recording ID"),
        th.Property("title", th.StringType, description="Conversation title"),
        th.Property("date", th.DateTimeType, description="Recording date"),
        th.Property("duration", th.IntegerType, description="Duration in seconds"),
        th.Property("crmEventID", th.StringType, description="CRM event ID"),
        th.Property(
            "user",
            th.ObjectType(
                th.Property("id", th.StringType, description="User ID"),
                th.Property("name", th.StringType, description="User name"),
                th.Property("email", th.StringType, description="User email"),
            ),
            description="User information",
        ),
        th.Property(
            "checklists",
            th.ArrayType(
                th.ObjectType(
                    th.Property("name", th.StringType, description="The name of the conversation"),
                    th.Property("score", th.NumberType, description="The score for the conversation"),
                    th.Property(
                        "denominator", th.NumberType, description="The maximum score the conversation can score"
                    ),
                    th.Property(
                        "trackerData",
                        th.ArrayType(
                            th.ObjectType(
                                th.Property("name", th.StringType, description="Name of the tracker"),
                                th.Property("isHit", th.BooleanType, description="Was the tracker hit"),
                                th.Property("aiScore", th.NumberType, description="The score for the tracker"),
                            ),
                        ),
                        description="The individual trackers associated with current checklist",
                    ),
                )
            ),
            description="The latest checklist(s) generated for the conversation",
        ),
        th.Property("rillaUrl", th.StringType, description="Rilla conversation URL"),
        th.Property("audioUrl", th.StringType, description="Audio file URL"),
        th.Property("transcriptUrl", th.StringType, description="Transcript URL"),
        th.Property("processedDate", th.DateTimeType, description="Processing date"),
        th.Property("jobNumber", th.StringType, description="Job number"),
        th.Property("stLink", th.StringType, description="Service Titan link"),
        th.Property("totalSold", th.NumberType, description="Total sold amount"),
        th.Property("outcome", th.StringType, description="Conversation outcome"),
        th.Property("jobSummary", th.StringType, description="Job summary"),
        th.Property("repSpeedWPM", th.NumberType, description="Rep words per minute"),
        th.Property("repTalkRatio", th.NumberType, description="Rep talk ratio"),
        th.Property("longestRepMonologue", th.IntegerType, description="Longest rep monologue"),
        th.Property(
            "longestCustomerMonologue",
            th.IntegerType,
            description="Longest customer monologue",
        ),
        th.Property("totalComments", th.IntegerType, description="Total comments"),
    ).to_dict()

    @override
    def prepare_request_payload(
        self,
        context: Context | None,
        next_page_token: int | None,
    ) -> dict | None:
        """Prepare the data payload for the request."""
        payload: dict[str, Any] = {}

        start_date, end_date = _get_date_range(
            start_date=self.config["start_date"],
            end_date=self.config.get("end_date"),
        )
        payload["toDate"] = end_date
        payload["fromDate"] = start_date

        # Handle pagination
        payload["page"] = next_page_token or 1

        # Set limit to maximum allowed
        payload["limit"] = 25

        # Set dateType with default
        payload["dateType"] = self.config.get("date_type", "timeOfRecording")

        # Optional fields
        if self.config.get("users"):
            payload["users"] = self.config.get("users")

        self.logger.info("Request payload: %s", payload)
        return payload

    @override
    def get_new_paginator(self) -> RillaPageNumberPaginator:
        """Return a new paginator for the next page."""
        return RillaPageNumberPaginator(start_value=1)


class TeamsStream(RillaStream):
    """Stream for teams data."""

    name = "teams"
    path = "/export/teams"
    primary_keys = ("teamId",)
    replication_key = None
    records_jsonpath = "$.teams[*]"
    http_method = HTTPMethod.POST

    schema = th.PropertiesList(
        th.Property("teamId", th.StringType, description="Unique ID for the team"),
        th.Property("name", th.StringType, description="The name of the team"),
        th.Property(
            "parentTeamId",
            th.StringType,
            description="The unique ID of the parent team (if applies)",
        ),
        th.Property(
            "parentTeamName",
            th.StringType,
            description="The name of the parent team (if applies)",
        ),
        # Analytics calculated for the provided date range
        th.Property(
            "appointmentsRecorded",
            th.NumberType,
            description="The number of CRM appointments recorded",
        ),
        th.Property(
            "analyticsViewed",
            th.NumberType,
            description="The number of analytics viewed",
        ),
        th.Property(
            "averageConversationDuration",
            th.NumberType,
            description="The average duration of the conversations that were recorded",
        ),
        th.Property(
            "averageConversationLength",
            th.NumberType,
            description="Average conversation length",
        ),
        th.Property("clipViewDuration", th.NumberType, description="Clip view duration"),
        th.Property("commentsGiven", th.NumberType, description="The number of comments written"),
        th.Property("commentsRead", th.NumberType, description="The number of comments read"),
        th.Property(
            "commentsReceived",
            th.NumberType,
            description="The number of comments received",
        ),
        th.Property(
            "commentsReceivedRead",
            th.NumberType,
            description="The number of comments that were left on the user’s conversations that the user read",
        ),
        th.Property(
            "conversationsViewed",
            th.NumberType,
            description="The number of conversations viewed",
        ),
        th.Property(
            "conversationsRecorded",
            th.NumberType,
            description=(
                "The total number of conversations recorded by users on the team during the requested time range"
            ),
        ),
        th.Property(
            "viewedRecordedRatio",
            th.NumberType,
            description="The ratio of conversations viewed to conversations recorded",
        ),
        th.Property(
            "conversationViewDuration",
            th.NumberType,
            description="The total duration of how long conversations were viewed for",
        ),
        th.Property(
            "patienceAverage",
            th.NumberType,
            description="The average patience for the team",
        ),
        th.Property(
            "recordingCompliance",
            th.NumberType,
            description=(
                "The recording compliance for the team (number of appointments recorded / total number of appointments)"
            ),
        ),
        th.Property(
            "scorecardsGiven",
            th.NumberType,
            description="The number of scorecards graded",
        ),
        th.Property(
            "scorecardsReceived",
            th.NumberType,
            description="The number of scorecards received",
        ),
        th.Property("talkRatioAverage", th.NumberType, description="Average talk ratio"),
        th.Property(
            "totalAppointments",
            th.NumberType,
            description="The total number of appointments for users on the team",
        ),
    ).to_dict()

    @override
    def prepare_request_payload(
        self,
        context: Context | None,
        next_page_token: Any | None,
    ) -> dict | None:
        """Prepare the data payload for the request."""
        payload: dict[str, Any] = {}

        start_date, end_date = _get_date_range(
            start_date=self.config["start_date"],
            end_date=self.config.get("end_date"),
        )
        payload["fromDate"] = start_date
        payload["toDate"] = end_date

        # Set dateType with default
        payload["dateType"] = self.config.get("date_type", "timeOfRecording")

        return payload


class UsersStream(RillaStream):
    """Stream for users data."""

    name = "users"
    path = "/export/users"
    primary_keys = ("userId",)
    replication_key = None
    records_jsonpath = "$.users[*]"
    http_method = HTTPMethod.POST

    schema = th.PropertiesList(
        th.Property("userId", th.StringType, description="The unique ID of the user"),
        th.Property("name", th.StringType, description="The name of the user"),
        th.Property("email", th.StringType, description="The email of the user"),
        th.Property(
            "isRemoved",
            th.BooleanType,
            description="Flag indicating whether the user has been deleted (true) or is still active (false)",
        ),
        th.Property("role", th.StringType, description="The user's role within Rilla"),
        th.Property(
            "teams",
            th.ArrayType(
                th.ObjectType(
                    th.Property("teamId", th.StringType, description="The unique ID of the team"),
                    th.Property("name", th.StringType, description="The name of the team"),
                ),
            ),
            description="An array of the objects which are the team the user belongs to",
        ),
        # Analytics calculated for the provided date range
        th.Property(
            "analyticsViewed",
            th.NumberType,
            description="The number of times the user has viewed analytics",
        ),
        th.Property(
            "appointmentsRecorded",
            th.NumberType,
            description="The number of appointments recorded",
        ),
        th.Property(
            "averageConversationDuration",
            th.NumberType,
            description="The average duration of the audio of the conversations recorded",
        ),
        th.Property(
            "averageConversationLength",
            th.NumberType,
            description="The average duration of the talking that occurs during the conversations recorded",
        ),
        th.Property(
            "clipViewDuration",
            th.NumberType,
            description="The total amount of time spent viewing clips",
        ),
        th.Property(
            "commentsReceived",
            th.NumberType,
            description="The number of comments the user received on their conversations",
        ),
        th.Property(
            "commentsReceivedRead",
            th.NumberType,
            description="The number of comments that were left on the user's conversations that the user read",
        ),
        th.Property("commentsGiven", th.NumberType, description="The number of comments given"),
        th.Property(
            "conversationsRecorded",
            th.NumberType,
            description="The number of conversations recorded",
        ),
        th.Property(
            "viewedRecordedRatio",
            th.NumberType,
            description="The ratio of conversations viewed to conversations recorded",
        ),
        th.Property(
            "conversationsViewed",
            th.NumberType,
            description="The number of conversations viewed",
        ),
        th.Property(
            "conversationViewDuration",
            th.NumberType,
            description="The total amount of time viewing conversations",
        ),
        th.Property(
            "patienceAverage",
            th.NumberType,
            description="The average patience score for the user's conversations",
        ),
        th.Property(
            "recordingCompliance",
            th.NumberType,
            description="The number of appointments recorded / total number of user's appointments",
        ),
        th.Property(
            "scorecardsGiven",
            th.NumberType,
            description="The number of scorecards graded",
        ),
        th.Property(
            "scorecardsReceived",
            th.NumberType,
            description="The number of scorecards received",
        ),
        th.Property(
            "talkRatioAverage",
            th.NumberType,
            description="The average talk ratio for the user's conversations",
        ),
        th.Property(
            "totalAppointments",
            th.NumberType,
            description="The total number of appointments the user had",
        ),
    ).to_dict()

    @override
    def prepare_request_payload(
        self,
        context: Context | None,
        next_page_token: Any | None,
    ) -> dict | None:
        """Prepare the data payload for the request."""
        payload: dict[str, Any] = {}

        start_date, end_date = _get_date_range(
            start_date=self.config["start_date"],
            end_date=self.config.get("end_date"),
        )
        payload["fromDate"] = start_date
        payload["toDate"] = end_date

        # Set dateType with default
        payload["dateType"] = self.config.get("date_type", "timeOfRecording")

        return payload
