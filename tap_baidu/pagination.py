"""Pagination classes for tap-baidu."""

from singer_sdk.pagination import BasePageNumberPaginator
from typing_extensions import override


class BaiduReportPaginator(BasePageNumberPaginator):
    """Baidu report paginator."""

    def __init__(self, start_value, stream) -> None:
        """Initialize the paginator with the given stream.

        Args:
            start_value: The initial value for pagination.
            stream: The stream instance to paginate.
        """
        super().__init__(start_value=start_value)
        self._stream = stream

    @override
    def has_more(self, response):
        stream_name = self._stream.name
        if stream_name in ("daily_report_in_site_dimension"):
            return bool(response.json()["result"])
        return bool(response.json()["results"])
