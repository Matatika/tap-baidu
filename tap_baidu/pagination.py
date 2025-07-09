"""Pagination classes for tap-baidu."""

from singer_sdk.pagination import BasePageNumberPaginator
from typing_extensions import override


class BaiduReportPaginator(BasePageNumberPaginator):
    """Baidu report paginator."""

    def __init__(self, start_value, stream, key="results") -> None:
        """Initialize the paginator with the given stream.

        Args:
            start_value: The initial value for pagination.
            stream: The stream instance to paginate.
            key: The key in the response JSON to paginate over (default is "results").
        """
        super().__init__(start_value=start_value)
        self._stream = stream
        self.key = key

    @override
    def has_more(self, response):
        return bool(response.json()[self.key])
