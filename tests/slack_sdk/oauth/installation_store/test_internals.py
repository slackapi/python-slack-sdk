import os
import sys
import time
import unittest
from datetime import datetime, timezone
from unittest import mock

import pytest

from slack_sdk.oauth.installation_store import Installation, FileInstallationStore
from slack_sdk.oauth.installation_store.internals import _from_iso_format_to_datetime, _timestamp_to_type


class TestFile(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_iso_format(self):
        dt = _from_iso_format_to_datetime("2021-07-14 08:00:17")
        self.assertEqual(dt.timestamp(), 1626249617.0)

    def test_iso_format_with_utc_offset(self):
        dt = _from_iso_format_to_datetime("2021-07-14 17:00:17+09:00")
        self.assertEqual(dt.timestamp(), 1626249617.0)
        dt = _from_iso_format_to_datetime("2021-07-14 03:00:17-05:00")
        self.assertEqual(dt.timestamp(), 1626249617.0)

    def test_iso_format_with_utc_designator(self):
        for iso_datetime_str in ["2021-07-14T08:00:17Z", "2021-07-14T08:00:17z", "2021-07-14T08:00:17.000Z"]:
            dt = _from_iso_format_to_datetime(iso_datetime_str)
            self.assertEqual(dt.timestamp(), 1626249617.0)


@pytest.mark.parametrize(
    "ts,target_type,expected_result",
    [
        (1701209097, int, 1701209097),
        (datetime(2023, 11, 28, 22, 9, 7, tzinfo=timezone.utc), int, 1701209347),
        ("1701209605", int, 1701209605),
        ("2023-11-28 22:11:19", int, 1701209479),
        ("2023-11-28 17:11:19-05:00", int, 1701209479),
        ("2023-11-28T22:11:19Z", int, 1701209479),
        (1701209998.3429494, float, 1701209998.3429494),
        (datetime(2023, 11, 28, 22, 20, 25, 262571, tzinfo=timezone.utc), float, 1701210025.262571),
        ("1701210054.4672053", float, 1701210054.4672053),
        ("2023-11-28 22:21:14.745556", float, 1701210074.745556),
    ],
)
def test_timestamp_to_type(ts, target_type, expected_result):
    result = _timestamp_to_type(ts, target_type)
    assert result == expected_result


@pytest.mark.skipif(not hasattr(time, "tzset"), reason="time.tzset is not available on this platform")
def test_timestamp_to_type_naive_datetime_is_utc():
    try:
        with mock.patch.dict(os.environ, {"TZ": "America/New_York"}):
            time.tzset()
            assert _timestamp_to_type(datetime(2023, 11, 28, 22, 9, 7), int) == 1701209347
    finally:
        time.tzset()


def test_timestamp_to_type_invalid_str():
    match = "Invalid isoformat string"
    with pytest.raises(ValueError, match=match):
        _timestamp_to_type("not-a-timestamp", int)


def test_timestamp_to_type_unsupported_format():
    with pytest.raises(ValueError, match="Unsupported data format"):
        _timestamp_to_type({}, int)
