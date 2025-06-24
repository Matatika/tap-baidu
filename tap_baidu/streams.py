"""Stream type classes for tap-baidu."""

from __future__ import annotations

import typing as t
from importlib import resources
from typing import Optional, Any
from typing_extensions import override
from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_baidu.client import BaiduStream
from singer_sdk.streams import RESTStream
from tap_baidu.auth import BaiduAuthenticator
from tap_baidu import BufferDeque


# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = resources.files(__package__) / "schemas"
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class SummaryStream(BaiduStream):
    name = "summary"
    path = "/data/v1/report/summary"
    primary_keys = ["date"]
    replication_key = "date"
    schema_filepath = SCHEMAS_DIR /"summary.json"
    records_jsonpath = "$.results[*]"

    def __init__(self, tap, schema=None):
        super().__init__(tap, schema=schema)
        self.authenticator = BaiduAuthenticator(self)

    def get_url_params(self, context: Optional[dict],next_page_token: Optional[Any]) -> dict:
        params = {
        "start_date": self.config["start_date"],
        "end_date": self.config["end_date"],
        "timezone": self.config.get("timezone"),
        # add other required params
        }
        return params

class CampaignsList(BaiduStream):
    name = "campaignslist"
    path = "/manage/v1/campaign"
    primary_keys = ["campaign_id"]
    schema_filepath = SCHEMAS_DIR /"campaign_list.json"
    records_jsonpath = "$[*]"

    def get_url_params(self, context, next_page_token):
        params = {
            "auth_level": self.config["auth_level"]
        }
        return params
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

class CampaignDetails(BaiduStream):
    parent_stream_type = CampaignsList
    name = "campaigndetails"
    path = "/manage/v1/campaign/detail"
    primary_key = ["campaign_id"]
    schema_filepath = SCHEMAS_DIR /"campaign_details.json"
    records_jsonpath = "$[*]"
    def get_url_params(self, context, next_page_token):
        params = super().get_url_params(context, next_page_token)
        params['campaign_ids'] = ','.join(context['campaign_ids'])
        return params
