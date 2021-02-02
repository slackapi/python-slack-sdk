import json
from typing import Dict, Any

from slack_sdk.audit_logs.v1.logs import LogsResponse


class AuditLogsResponse:
    url: str
    status_code: int
    headers: Dict[str, Any]
    raw_body: str
    body: Dict[str, Any]
    typed_body: LogsResponse

    @property
    def typed_body(self) -> LogsResponse:
        return LogsResponse(**self.body)

    def __init__(
        self,
        *,
        url: str,
        status_code: int,
        raw_body: str,
        headers: dict,
    ):
        self.url = url
        self.status_code = status_code
        self.headers = headers
        self.raw_body = raw_body
        self.body = (
            json.loads(raw_body)
            if raw_body is not None and raw_body.startswith("{")
            else None
        )
