"""Stream type classes for tap-rilla."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, Iterable

import requests
from singer_sdk import typing as th

from tap_rilla.client import RillaStream


class ConversationsStream(RillaStream):
    """Stream for conversations data."""
    
    name = "conversations"
    path = "/export/conversations"
    primary_keys = ["conversationId"]
    replication_key = None
    records_jsonpath = "$.conversations[*]"
    
    schema = th.PropertiesList(
        th.Property("conversationId", th.StringType, description="The conversation ID"),
        th.Property("recordingId", th.StringType, description="The recording ID"),
        th.Property("title", th.StringType, description="Conversation title"),
        th.Property("date", th.DateTimeType, description="Recording date"),
        th.Property("duration", th.IntegerType, description="Duration in seconds"),
        th.Property("crmEventID", th.StringType, description="CRM event ID"),
        th.Property("user", th.ObjectType(
            th.Property("id", th.StringType, description="User ID"),
            th.Property("name", th.StringType, description="User name"),
            th.Property("email", th.StringType, description="User email"),
        ), description="User information"),
        th.Property("checklists", th.ArrayType(th.ObjectType()), description="Checklist data"),
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
        th.Property("longestCustomerMonologue", th.IntegerType, description="Longest customer monologue"),
        th.Property("totalComments", th.IntegerType, description="Total comments"),
    ).to_dict()
    
    def prepare_request_payload(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Optional[dict]:
        """Prepare the data payload for the request."""
        payload = {}
        
        # Use ISO 8601 format for dates
        start_date = self.config.get("start_date")
        if start_date:
            payload["fromDate"] = f"{start_date}T00:00:00Z"
            
        end_date = self.config.get("end_date")
        if end_date:
            payload["toDate"] = f"{end_date}T23:59:59Z"
        elif start_date:
            payload["toDate"] = datetime.utcnow().isoformat() + "Z"
        
        # Handle pagination
        if next_page_token:
            payload["page"] = int(next_page_token)
        else:
            payload["page"] = 1
            
        # Set limit to maximum allowed
        payload["limit"] = 25
        
        # Set dateType with default
        payload["dateType"] = self.config.get("date_type", "timeOfRecording")
        
        # Optional fields
        if self.config.get("users"):
            payload["users"] = self.config.get("users")
        
        self.logger.info(f"Request payload: {payload}")
        return payload
    
    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return token for next page or None if no more pages."""
        data = response.json()
        current_page = data.get("currentPage", 1)
        total_pages = data.get("totalPages", 1)
        
        if current_page < total_pages:
            return str(current_page + 1)
        return None
    
    @property
    def rest_method(self) -> str:
        """Return the API HTTP method."""
        return "POST"


class TeamsStream(RillaStream):
    """Stream for teams data."""
    
    name = "teams"
    path = "/export/teams"
    primary_keys = ["teamId"]
    replication_key = None
    records_jsonpath = "$.teams[*]"
    
    schema = th.PropertiesList(
        th.Property("teamId", th.StringType, description="Unique ID for the team"),
        th.Property("name", th.StringType, description="The name of the team"),
        th.Property("parentTeamId", th.StringType, description="The unique ID of the parent team (if applies)"),
        th.Property("parentTeamName", th.StringType, description="The name of the parent team (if applies)"),
        # Analytics calculated for the provided date range
        th.Property("appointmentsRecorded", th.NumberType, description="The number of CRM appointments recorded"),
        th.Property("analyticsViewed", th.NumberType, description="The number of analytics viewed"),
        th.Property("averageConversationDuration", th.NumberType, description="The average duration of the conversations that were recorded"),
        th.Property("averageConversationLength", th.NumberType, description="Average conversation length"),
        th.Property("clipViewDuration", th.NumberType, description="Clip view duration"),
        th.Property("commentsGiven", th.NumberType, description="The number of comments written"),
        th.Property("commentsRead", th.NumberType, description="The number of comments read"),
        th.Property("commentsReceived", th.NumberType, description="The number of comments received"),
        th.Property("conversationsViewed", th.NumberType, description="The number of conversations viewed"),
        th.Property("conversationsRecorded", th.NumberType, description="The total number of conversations recorded by users on the team during the requested time range"),
        th.Property("viewedRecordedRatio", th.NumberType, description="The ratio of conversations viewed to conversations recorded"),
        th.Property("conversationViewDuration", th.NumberType, description="The total duration of how long conversations were viewed for"),
        th.Property("patienceAverage", th.NumberType, description="The average patience for the team"),
        th.Property("recordingCompliance", th.NumberType, description="The recording compliance for the team (number of appointments recorded / total number of appointments)"),
        th.Property("scorecardsGiven", th.NumberType, description="The number of scorecards graded"),
        th.Property("scorecardsReceived", th.NumberType, description="The number of scorecards received"),
        th.Property("talkRatioAverage", th.NumberType, description="Average talk ratio"),
        th.Property("totalAppointments", th.NumberType, description="The total number of appointments for users on the team"),
    ).to_dict()
    
    def prepare_request_payload(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Optional[dict]:
        """Prepare the data payload for the request."""
        payload = {}
        
        # Use ISO 8601 format for dates
        start_date = self.config.get("start_date")
        if start_date:
            payload["fromDate"] = f"{start_date}T00:00:00Z"
            
        end_date = self.config.get("end_date")
        if end_date:
            payload["toDate"] = f"{end_date}T23:59:59Z"
        elif start_date:
            payload["toDate"] = datetime.utcnow().isoformat() + "Z"
        
        # Set dateType with default
        payload["dateType"] = self.config.get("date_type", "timeOfRecording")
            
        return payload
    
    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return token for next page or None if no more pages."""
        # Teams endpoint might not have pagination
        return None
    
    @property
    def rest_method(self) -> str:
        """Return the API HTTP method."""
        return "POST"


class UsersStream(RillaStream):
    """Stream for users data."""
    
    name = "users"
    path = "/export/users"
    primary_keys = ["userId"]
    replication_key = None
    records_jsonpath = "$.users[*]"
    
    schema = th.PropertiesList(
        th.Property("userId", th.StringType, description="The unique ID of the user"),
        th.Property("name", th.StringType, description="The name of the user"),
        th.Property("email", th.StringType, description="The email of the user"),
        th.Property("isRemoved", th.BooleanType, description="Flag indicating whether the user has been deleted (true) or is still active (false)"),
        th.Property("role", th.StringType, description="The user's role within Rilla"),
        th.Property("teams", th.ArrayType(th.ObjectType(
            th.Property("teamId", th.StringType, description="The unique ID of the team"),
            th.Property("name", th.StringType, description="The name of the team"),
        )), description="An array of the objects which are the team the user belongs to"),
        # Analytics calculated for the provided date range
        th.Property("analyticsViewed", th.NumberType, description="The number of times the user has viewed analytics"),
        th.Property("appointmentsRecorded", th.NumberType, description="The number of appointments recorded"),
        th.Property("averageConversationDuration", th.NumberType, description="The average duration of the audio of the conversations recorded"),
        th.Property("averageConversationLength", th.NumberType, description="The average duration of the talking that occurs during the conversations recorded"),
        th.Property("clipViewDuration", th.NumberType, description="The total amount of time spent viewing clips"),
        th.Property("commentsReceived", th.NumberType, description="The number of comments the user received on their conversations"),
        th.Property("commentsReceivedRead", th.NumberType, description="The number of comments that were left on the user's conversations that the user read"),
        th.Property("commentsGiven", th.NumberType, description="The number of comments given"),
        th.Property("conversationsRecorded", th.NumberType, description="The number of conversations recorded"),
        th.Property("conversationsViewed", th.NumberType, description="The number of conversations viewed"),
        th.Property("conversationViewDuration", th.NumberType, description="The total amount of time viewing conversations"),
        th.Property("patienceAverage", th.NumberType, description="The average patience score for the user's conversations"),
        th.Property("recordingCompliance", th.NumberType, description="The number of appointments recorded / total number of user's appointments"),
        th.Property("scorecardsGiven", th.NumberType, description="The number of scorecards graded"),
        th.Property("scorecardsReceived", th.NumberType, description="The number of scorecards received"),
        th.Property("talkRatioAverage", th.NumberType, description="The average talk ratio for the user's conversations"),
        th.Property("totalAppointments", th.NumberType, description="The total number of appointments the user had"),
    ).to_dict()
    
    def prepare_request_payload(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Optional[dict]:
        """Prepare the data payload for the request."""
        payload = {}
        
        # Use ISO 8601 format for dates
        start_date = self.config.get("start_date")
        if start_date:
            payload["fromDate"] = f"{start_date}T00:00:00Z"
            
        end_date = self.config.get("end_date")
        if end_date:
            payload["toDate"] = f"{end_date}T23:59:59Z"
        elif start_date:
            payload["toDate"] = datetime.utcnow().isoformat() + "Z"
        
        # Set dateType with default
        payload["dateType"] = self.config.get("date_type", "timeOfRecording")
            
        return payload
    
    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return token for next page or None if no more pages."""
        # Users endpoint might not have pagination
        return None
    
    @property
    def rest_method(self) -> str:
        """Return the API HTTP method."""
        return "POST"