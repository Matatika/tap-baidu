from math import ceil
from singer_sdk.pagination import BasePageNumberPaginator
from typing_extensions import override

class BaiduPaginator(BasePageNumberPaginator):

    @override
    def __init__(self, start_value = 1, page_size = 500) -> None:
        super().__init__(start_value)
        self.page_size = page_size

    @override
    def has_more(self,response):
        
        data = response.json()
        if isinstance(data, list):
            # the paginator occasionally looks at the parsed response from the child stream which is a list. This check avoids those responses.
            return False
        total_records = data.get("total",0)
        total_pages = ceil(total_records/self.page_size)
        current_page = self._value

        return current_page < total_pages