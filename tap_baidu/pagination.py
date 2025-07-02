from singer_sdk.pagination import BasePageNumberPaginator
from typing_extensions import override

class BaiduReportPaginator(BasePageNumberPaginator):

    @override
    def has_more(self,response):       
        return bool(response.json()['results'])