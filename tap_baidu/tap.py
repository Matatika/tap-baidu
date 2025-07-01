"""Baidu tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

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
        th.Property("start_date",th.DateType, description = "Start date required for the report streams - summary and report in campaign dimension"),
        th.Property("end_date",th.DateType, description = "End date required for the report streams - summary and report in campaign dimension"),
        th.Property("timezone",th.StringType, description = "Time zone of the report streams - summary and report in campaign dimension. The possible values are est,utc0,utc8"),
        th.Property("auth_level",th.StringType, description = "This is the allowed authorized level and used to get list of authourized campaigns from teh campaigns stream. The permitted values are: r and rw"),
        th.Property("pageSize",th.IntegerType),
        th.Property("currentPage",th.IntegerType),
        th.Property("campaign_name", th.StringType),
        th.Property("sort_field", th.StringType),
        th.Property("sort_val", th.StringType),
        th.Property("status",th.IntegerType, 
                    description = "This is an optional parameter used in the report in campaign dimension stream to get active(1)/paused(0) campaigns. Possible values are 0 and 1")
    ).to_dict()

    def discover_streams(self):
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapBaidu.cli()
