"""REST client handling, including RillaStream base class."""

from __future__ import annotations

import http
import sys
from typing import TYPE_CHECKING

from singer_sdk.authenticators import SimpleAuthenticator
from singer_sdk.exceptions import FatalAPIError
from singer_sdk.streams import RESTStream

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    import requests


class RillaStream(RESTStream):
    """Rilla stream class."""

    url_base = "https://customer.rillavoice.com"

    @property
    @override
    def authenticator(self) -> SimpleAuthenticator:
        """An authenticator object for the stream."""
        return SimpleAuthenticator(
            stream=self,
            auth_headers={"Authorization": self.config["api_key"]},
        )

    @property
    @override
    def http_headers(self) -> dict:
        """HTTP headers used for each request."""
        return {
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
        }

    @override
    def validate_response(self, response: requests.Response) -> None:
        """Validate HTTP response."""
        if response.status_code == http.HTTPStatus.NOT_FOUND:
            self.logger.error("Request URL: %s", response.request.url)
            self.logger.error("Request method: %s", response.request.method)
            self.logger.error("Request headers: %s", response.request.headers.keys())
            self.logger.error("Request body: %s", response.request.body)
            self.logger.error("Response status: %s", response.status_code)
            self.logger.error("Response text: %s", response.text[:500])

        elif response.status_code in {
            http.HTTPStatus.UNAUTHORIZED,
            http.HTTPStatus.FORBIDDEN,
        }:
            msg = (
                f"{response.status_code} Client Error: Authorization failed. "
                "Please check your API key."
            )
            raise FatalAPIError(msg)

        super().validate_response(response)
