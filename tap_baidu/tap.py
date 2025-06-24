"""Baidu tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers
from tap_baidu import streams

STREAM_TYPES = [
            streams.SummaryStream,
            streams.CampaignsList
            ]

class TapBaidu(Tap):
    """Baidu tap class."""

    name = "tap-baidu"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property("api_token",th.StringType,required=True),
        th.Property("start_date",th.DateType),
        th.Property("end_date",th.DateType),
        th.Property("timezone",th.StringType),
        th.Property("auth_level",th.StringType)
    ).to_dict()

    def discover_streams(self):
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapBaidu.cli()
