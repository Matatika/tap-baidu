"""Stream type classes for tap-baidu."""

from __future__ import annotations

from importlib import resources
from typing import Any

from typing_extensions import override

from tap_baidu import BufferDeque
from tap_baidu.client import BaiduStream
from singer_sdk.exceptions import ConfigValidationError


SCHEMAS_DIR = resources.files(__package__) / "schemas"

class SummaryStream(BaiduStream):
    """Class to get summary of reports."""
    name = "summary"
    path = "/data/v1/report/summary"
    primary_keys = ["date"]  # noqa: RUF012
    replication_key = "date"
    schema_filepath = SCHEMAS_DIR /"summary.json"
    records_jsonpath = "$.results[*]"

    def __init__(self, tap, stream_config=None):
        super().__init__(tap, stream_config)
        # validate required config
        if not self.config.get("start_date"):
            raise ConfigValidationError("Missing required config parameter: 'start_date'")
        
    def get_url_params(self, context: dict | None,next_page_token: Any | None) -> dict:  # noqa: ANN401, ARG002
        return {
        "start_date": self.get_starting_replication_key_value(context),
        "end_date": self.config["end_date"],
        "timezone": self.config["timezone"]
        }

class CampaignsList(BaiduStream):
    """Class to get list of authorized campaigns."""
    name = "campaigns"
    path = "/manage/v1/campaign"
    primary_keys = ["campaign_id"]  # noqa: RUF012
    schema_filepath = SCHEMAS_DIR /"campaign_list.json"
    records_jsonpath = "$[*]"

    def get_url_params(self, context: dict | None,next_page_token: Any | None): # noqa: ANN401, ARG002
        return {
            "auth_level": 'r'
        }
    @override
    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        super().__init__(*args, **kwargs)
        self.campaign_ids_buffer = BufferDeque(maxlen=150)

    @override
    def parse_response(self, response):  # noqa: ANN001
        for record in super().parse_response(response):
            yield record

        # make sure we process the remaining buffer entries
        self.campaign_ids_buffer.finalize()
        yield record  # yield last record again to force child context generation

    @override
    def generate_child_contexts(self, record, context):  # noqa: ANN001
        self.campaign_ids_buffer.append(record["campaign_id"])

        with self.campaign_ids_buffer as buf:
            if buf.flush:
                yield {"campaign_ids": buf}

class CampaignDetails(BaiduStream):
    """Class to get details about campaigns."""
    parent_stream_type = CampaignsList
    name = "campaign_details"
    path = "/manage/v1/campaign/detail"
    primary_keys = ["campaign_id"]  # noqa: RUF012
    schema_filepath = SCHEMAS_DIR /"campaign_details.json"
    records_jsonpath = "$[*]"
    state_partitioning_keys = () # we don't want to store any state bookmarks for the child stream
    def get_url_params(self, context, next_page_token):  # noqa: ANN001
        params = super().get_url_params(context, next_page_token)
        params["campaign_ids"] = ",".join(context["campaign_ids"])
        return params

class ReportInCampaignDimension(BaiduStream):
    """Class to get report in campaign dimension."""
    name = "daily_report_in_campaign_dimension"
    path = "/data/v1/report/day/list"
    primary_keys = ["id","date"]
    replication_key = "date"
    schema_filepath = SCHEMAS_DIR /"report_campaign_dimension.json"
    records_jsonpath = "$.results[*]"

    def get_url_params(self, context, next_page_token):  # noqa: ANN001
        
        params = super().get_url_params(context, next_page_token)

        params["start_date"] =  self.get_starting_replication_key_value(context)
        params["end_date"] = self.config["end_date"]
        params["timezone"] = self.config["timezone"]
        params["page_size"] = 500
        params["current_page"] = next_page_token or 1
        params["sort_val"] = "asc"
        return params