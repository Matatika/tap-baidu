"""Stream type classes for tap-baidu."""

from __future__ import annotations

from importlib import resources

from typing_extensions import override

from tap_baidu import BufferDeque
from tap_baidu.client import BaiduStream
from tap_baidu.pagination import BaiduReportPaginator

SCHEMAS_DIR = resources.files(__package__) / "schemas"


class SummaryStream(BaiduStream):
    """Class to get summary of reports."""

    name = "summary"
    path = "/summary"
    primary_keys = ("date",)
    replication_key = "date"
    schema_filepath = SCHEMAS_DIR / "summary.json"
    records_jsonpath = "$.results[*]"
    is_sorted = True


class CampaignStream(BaiduStream):
    """Class to get list of authorized campaigns."""

    name = "campaigns"
    path = "/manage/v1/campaign"
    primary_keys = ("campaign_id",)
    schema_filepath = SCHEMAS_DIR / "campaign_list.json"

    @override
    def get_url_params(self, context, next_page_token):
        return {"auth_level": "r"}

    @override
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.campaign_ids_buffer = BufferDeque(maxlen=150)

    @override
    def parse_response(self, response):
        for record in super().parse_response(response):
            yield record

        # make sure we process the remaining buffer entries
        self.campaign_ids_buffer.finalize()
        yield record  # yield last record again to force child context generation

    @override
    def generate_child_contexts(self, record, context):
        self.campaign_ids_buffer.append(record["campaign_id"])

        with self.campaign_ids_buffer as buf:
            if buf.flush:
                yield {"campaign_ids": buf}


class AccountsStream(BaiduStream):
    """Class to get list of authorized accounts."""

    name = "authorized_accounts"
    path = "/manage/v1/account"
    primary_keys = ("account_id",)
    schema_filepath = SCHEMAS_DIR / "authorized_account_list.json"

    @override
    def get_url_params(self, context, next_page_token):
        return {"auth_level": "r"}


class CampaignDetails(BaiduStream):
    """Class to get details about campaigns."""

    parent_stream_type = CampaignStream
    name = "campaign_details"
    path = "/manage/v1/campaign/detail"
    primary_keys = ("campaign_id",)
    schema_filepath = SCHEMAS_DIR / "campaign_details.json"

    # we don't want to store any state bookmarks for the child stream
    state_partitioning_keys = ()

    @override
    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["campaign_ids"] = ",".join(context["campaign_ids"])
        return params


class ReportInCampaignDimension(BaiduStream):
    """Class to get report in campaign dimension."""

    name = "daily_report_in_campaign_dimension"
    path = "/day/list"
    primary_keys = ("id", "date")
    replication_key = "date"
    schema_filepath = SCHEMAS_DIR / "report_campaign_dimension.json"
    records_jsonpath = "$.results[*]"
    is_sorted = True

    @override
    def get_new_paginator(self):
        return BaiduReportPaginator(1, stream=self)

    @override
    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["page_size"] = 500
        params["current_page"] = next_page_token
        params["sort_field"] = "date"
        params["sort_val"] = "asc"
        return params


class ReportInSiteDimension(BaiduStream):
    """Class to get report in site dimension."""

    name = "daily_report_in_site_dimension"
    path = "/site/day/list"
    primary_keys = ("site_id", "date")
    replication_key = "date"
    schema_filepath = SCHEMAS_DIR / "report_in_site_dimension.json"
    records_jsonpath = "$.result[*]"

    @override
    def get_new_paginator(self):
        return BaiduReportPaginator(1, stream=self)

    @override
    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params["campaign_id"] = self.config["campaign_id"]
        params["page_size"] = 500
        params["current_page"] = next_page_token
        return params
