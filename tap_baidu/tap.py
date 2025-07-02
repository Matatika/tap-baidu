"""Baidu tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers
from datetime import date, timedelta

from tap_baidu import streams

STREAM_TYPES = [
            streams.SummaryStream,
            streams.CampaignsList,
            streams.CampaignDetails,
            streams.ReportInCampaignDimension
            ]

class TapBaidu(Tap):
    """Baidu tap class."""

    name = "tap-baidu"

    config_jsonschema = th.PropertiesList(
        th.Property("api_token",th.StringType,required=True, description = "API token used for authentication"),
        th.Property("start_date",th.DateType, value = (date.today() - timedelta(days=365)).isoformat(), description = "Start date required for the report streams - summary and report in campaign dimension."),
        th.Property("end_date",th.DateType, value = date.today().isoformat(), description = "End date required for the report streams - summary and report in campaign dimension."),
        th.Property("timezone",th.StringType,allowed_values= ['utc0','utc8', 'est'] ,value = 'utc0', description = "Time zone of the report streams - summary and report in campaign dimension.")
    ).to_dict()

    def discover_streams(self):
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapBaidu.cli()
