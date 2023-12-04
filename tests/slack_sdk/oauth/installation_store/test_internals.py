import sys
import unittest
from datetime import datetime, timezone

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


@pytest.mark.parametrize(
    "ts,target_type,expected_result",
    [
        (1701209097, int, 1701209097),
        (datetime(2023, 11, 28, 22, 9, 7, tzinfo=timezone.utc), int, 1701209347),
        ("1701209605", int, 1701209605),
        ("2023-11-28 22:11:19", int, 1701209479),
        (1701209998.3429494, float, 1701209998.3429494),
        (datetime(2023, 11, 28, 22, 20, 25, 262571, tzinfo=timezone.utc), float, 1701210025.262571),
        ("1701210054.4672053", float, 1701210054.4672053),
        ("2023-11-28 22:21:14.745556", float, 1701210074.745556),
    ],
)
def test_timestamp_to_type(ts, target_type, expected_result):
    result = _timestamp_to_type(ts, target_type)
    assert result == expected_result


def test_timestamp_to_type_invalid_str():
    match = "Invalid isoformat string" if sys.version_info[:2] > (3, 6) else "time data .* does not match format"
    with pytest.raises(ValueError, match=match):
        _timestamp_to_type("not-a-timestamp", int)


def test_timestamp_to_type_unsupported_format():
    with pytest.raises(ValueError, match="Unsupported data format"):
        _timestamp_to_type({}, int)
