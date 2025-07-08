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
    def is_report_stream(self) -> bool:
        """Return True if the stream is a report stream, otherwise False."""
        return self.name in (
            "summary",
            "daily_report_in_campaign_dimension",
            "daily_report_in_site_dimension",
        )

    @property
    def url_base(self) -> str:
        """Return the appropriate base URL depending on the stream name."""
        if self.is_report_stream:
            return "https://api.mediago.io/data/v1/report"
        return "https://api.mediago.io"

    def get_url_params(self, context, next_page_token) -> dict:
        """Return URL query parameters for the request."""
        params = super().get_url_params(context, next_page_token)
        if self.is_report_stream:
            # add your start_date, end_date, timezone here
            params.update(
                {
                    "start_date": self.get_starting_replication_key_value(context),
                    "end_date": self.config["end_date"],
                    "timezone": self.config["timezone"],
                }
            )
        return params
