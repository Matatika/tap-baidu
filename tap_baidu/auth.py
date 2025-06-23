"""Baidu Authentication."""

from __future__ import annotations
from singer_sdk.authenticators import SimpleAuthenticator


# The SingletonMeta metaclass makes your streams reuse the same authenticator instance.
# If this behaviour interferes with your use-case, you can remove the metaclass.
class BaiduAuthenticator(SimpleAuthenticator):
    """Authenticator class for Baidu."""

    def __init__(self,stream):
        super().__init__(stream=stream)
        self.stream = stream
        self.config.get("auth_token")
        self._access_token = None
    
    def update_access_token(self):
        import requests

        api_token = self.config.get("api_token")
        response = requests.post(
            "https://api.mediago.io/data/v1/authentication", 
            headers={"Authorization": f"Basic {api_token}"}
        )
        response.raise_for_status()
        self._access_token = response.json()["access_token"]
        return super().update_access_token()
    
    def auth_headers(self) -> dict:
        if not self._access_token:
            self.update_access_token()
        headers = {"Authorization": f"Bearer {self._access_token}"}
        self.logger.info(f"Auth headers: {headers}")
        return headers
    