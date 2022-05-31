import json
from typing import Optional, Dict, Any, Sequence
from urllib.parse import parse_qsl


def parse_body(body: str, content_type: Optional[str]) -> Dict[str, Any]:
    if not body:
        return {}
    if (content_type is not None and content_type == "application/json") or body.startswith("{"):
        return json.loads(body)
    else:
        if "payload" in body:  # This is not JSON format yet
            params = dict(parse_qsl(body))
            if params.get("payload") is not None:
                return json.loads(params.get("payload"))
            else:
                return {}
        else:
            return dict(parse_qsl(body))


def extract_is_enterprise_install(payload: Dict[str, Any]) -> Optional[bool]:
    if "is_enterprise_install" in payload:
        is_enterprise_install = payload.get("is_enterprise_install")
        return is_enterprise_install is not None and (is_enterprise_install is True or is_enterprise_install == "true")
    return False


def extract_enterprise_id(payload: Dict[str, Any]) -> Optional[str]:
    if payload.get("enterprise") is not None:
        org = payload.get("enterprise")
        if isinstance(org, str):
            return org
        elif "id" in org:
            return org.get("id")  # type: ignore
    if payload.get("authorizations") is not None and len(payload["authorizations"]) > 0:
        # To make Events API handling functioning also for shared channels,
        # we should use .authorizations[0].enterprise_id over .enterprise_id
        return extract_enterprise_id(payload["authorizations"][0])
    if "enterprise_id" in payload:
        return payload.get("enterprise_id")
    if payload.get("team") is not None and "enterprise_id" in payload["team"]:
        # In the case where the type is view_submission
        return payload["team"].get("enterprise_id")
    if payload.get("event") is not None:
        return extract_enterprise_id(payload["event"])
    return None


def extract_team_id(payload: Dict[str, Any]) -> Optional[str]:
    if payload.get("team") is not None:
        team = payload.get("team")
        if isinstance(team, str):
            return team
        elif team and "id" in team:
            return team.get("id")
    if payload.get("authorizations") is not None and len(payload["authorizations"]) > 0:
        # To make Events API handling functioning also for shared channels,
        # we should use .authorizations[0].team_id over .team_id
        return extract_team_id(payload["authorizations"][0])
    if "team_id" in payload:
        return payload.get("team_id")
    if payload.get("event") is not None:
        return extract_team_id(payload["event"])
    if payload.get("user") is not None:
        return payload.get("user")["team_id"]
    return None


def extract_user_id(payload: Dict[str, Any]) -> Optional[str]:
    if payload.get("user") is not None:
        user = payload.get("user")
        if isinstance(user, str):
            return user
        elif "id" in user:
            return user.get("id")  # type: ignore
    if "user_id" in payload:
        return payload.get("user_id")
    if payload.get("event") is not None:
        return extract_user_id(payload["event"])
    return None


def extract_content_type(headers: Dict[str, Sequence[str]]) -> Optional[str]:
    content_type: Optional[str] = headers.get("content-type", [None])[0]
    if content_type:
        return content_type.split(";")[0]
    return None
