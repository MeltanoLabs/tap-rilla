"""REST client handling, including RillaStream base class."""

from __future__ import annotations

from typing import Any, Dict, Optional, Iterable
from urllib.parse import parse_qsl

import requests
from singer_sdk.authenticators import SimpleAuthenticator
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseAPIPaginator
from singer_sdk.streams import RESTStream


class RillaStream(RESTStream):
    """Rilla stream class."""
    
    url_base = "https://customer.rillavoice.com"
    
    @property
    def authenticator(self) -> SimpleAuthenticator:
        """Return a new authenticator object."""
        return SimpleAuthenticator(
            stream=self,
            auth_headers={
                "Authorization": self.config.get("api_key")
            }
        )
    
    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "tap-rilla/0.1.0",
        }
        return headers
    
    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params.update(parse_qsl(next_page_token))
        return params
    
    def validate_response(self, response: requests.Response) -> None:
        """Validate HTTP response."""
        if response.status_code == 404:
            self.logger.error(f"Request URL: {response.request.url}")
            self.logger.error(f"Request method: {response.request.method}")
            self.logger.error(f"Request headers: {dict(response.request.headers)}")
            self.logger.error(f"Request body: {response.request.body}")
            self.logger.error(f"Response status: {response.status_code}")
            self.logger.error(f"Response text: {response.text[:500]}")
        if response.status_code in [401, 403]:
            msg = f"{response.status_code} Client Error: Authorization failed. Please check your API key."
            raise Exception(msg)
        elif response.status_code == 404:
            msg = (
                f"{response.status_code} Client Error: Not Found for path: {self.path}\n"
                f"Please verify the API endpoint with Rilla support (support@rilla.com).\n"
                f"Request URL: {response.request.url}"
            )
            raise Exception(msg)
        super().validate_response(response)
    
    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records."""
        try:
            yield from extract_jsonpath(self.records_jsonpath, input=response.json())
        except Exception as e:
            self.logger.error(f"Failed to parse response: {e}")
            self.logger.error(f"Response text: {response.text[:500]}")
            raise