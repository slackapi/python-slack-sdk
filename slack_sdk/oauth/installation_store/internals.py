import platform
import datetime

(major, minor, patch) = platform.python_version_tuple()
is_python_3_6: bool = int(major) == 3 and int(minor) >= 6

utc_timezone = datetime.timezone.utc


def _from_iso_format_to_datetime(iso_datetime_str: str) -> datetime.datetime:
    if is_python_3_6:
        elements = iso_datetime_str.split(" ")
        ymd = elements[0].split("-")
        hms = elements[1].split(":")
        return datetime.datetime(
            int(ymd[0]),
            int(ymd[1]),
            int(ymd[2]),
            int(hms[0]),
            int(hms[1]),
            int(hms[2]),
            0,
            utc_timezone,
        )
    else:
        if "+" not in iso_datetime_str:
            iso_datetime_str += "+00:00"
        return datetime.datetime.fromisoformat(iso_datetime_str)


def _from_iso_format_to_unix_timestamp(iso_datetime_str: str) -> float:
    return _from_iso_format_to_datetime(iso_datetime_str).timestamp()
