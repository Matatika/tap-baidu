"""REST client handling, including BaiduStream base class."""

from __future__ import annotations

from functools import cached_property

from singer_sdk.streams import RESTStream
from typing_extensions import override

from tap_baidu.auth import BaiduAuthenticator


class BaiduStream(RESTStream):
    """Baidu stream class."""

    url_base = "https://api.mediago.io"

    @override
    @cached_property
    def authenticator(self):
        return BaiduAuthenticator(stream=self, api_token=self.config["api_token"])
