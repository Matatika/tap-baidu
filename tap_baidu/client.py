"""REST client handling, including BaiduStream base class."""

from __future__ import annotations

from functools import cached_property

from singer_sdk.streams import RESTStream
from typing_extensions import override

from tap_baidu.auth import BaiduAuthenticator


class BaiduStream(RESTStream):
    """Baidu stream class."""

    @override
    @cached_property
    def authenticator(self):
        return BaiduAuthenticator(stream=self, api_token=self.config["api_token"])

    @property
    def url_base(self) -> str:
        """Return the base URL for the API."""
        return "https://api.mediago.io"

    def backoff_max_tries(self):
        """Return the maximum number of backoff attempts for API requests."""
        return 8


class BaiduReportStream(BaiduStream):
    """Baidu report stream class."""

    @property
    def url_base(self) -> str:
        """Return the appropriate base URL depending on the stream name."""
        return "https://api.mediago.io/data/v1/report"

    def get_url_params(self, context, next_page_token) -> dict:
        """Return URL query parameters for the request."""
        params = super().get_url_params(context, next_page_token)
        start_value = self.get_starting_replication_key_value(context)
        # add your start_date, end_date, timezone here
        params.update(
            {
                "start_date": start_value or self.config.get("start_date"),
                "end_date": self.config["end_date"],
                "timezone": self.config["timezone"],
            }
        )
        return params
