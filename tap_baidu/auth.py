"""Baidu Authentication."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING

from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta

if TYPE_CHECKING:
    from singer_sdk.streams import Stream


# The SingletonMeta metaclass makes your streams reuse the same authenticator instance.
# If this behaviour interferes with your use-case, you can remove the metaclass.
class BaiduAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for Baidu."""

    def __init__(self, stream: Stream, api_token: str)-> None:
        token_bytes = api_token.encode("utf-8")
        base64_token = base64.b64encode(token_bytes).decode("utf-8")
        headers = {"Authorization": f"Basic {base64_token}"}

        super().__init__(
            stream=stream,
            auth_endpoint="https://api.mediago.io/data/v1/authentication",
            oauth_headers=headers,
        )

    @property
    def oauth_request_body(self):
        return {}