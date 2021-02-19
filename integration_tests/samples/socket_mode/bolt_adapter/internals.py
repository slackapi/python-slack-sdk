import json
import logging
from time import time

from slack_sdk.socket_mode.client import BaseSocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse

from slack_bolt.app import App
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse


def run_bolt_app(app: App, req: SocketModeRequest):  # type: ignore
    bolt_req: BoltRequest = BoltRequest(mode="socket_mode", body=req.payload)
    bolt_resp: BoltResponse = app.dispatch(bolt_req)
    return bolt_resp


def send_response(
    client: BaseSocketModeClient,
    req: SocketModeRequest,
    bolt_resp: BoltResponse,
    start_time: float,
):
    if bolt_resp.status == 200:
        content_type = bolt_resp.headers.get("content-type", [""])[0]
        if bolt_resp.body is None or len(bolt_resp.body) == 0:
            client.send_socket_mode_response(
                SocketModeResponse(envelope_id=req.envelope_id)
            )
        elif content_type.startswith("application/json"):
            dict_body = json.loads(bolt_resp.body)
            client.send_socket_mode_response(
                SocketModeResponse(envelope_id=req.envelope_id, payload=dict_body)
            )
        else:
            client.send_socket_mode_response(
                SocketModeResponse(
                    envelope_id=req.envelope_id, payload={"text": bolt_resp.body}
                )
            )

        if client.logger.level <= logging.DEBUG:
            spent_time = int((time() - start_time) * 1000)
            client.logger.debug(f"Response time: {spent_time} milliseconds")
    else:
        client.logger.info(
            f"Unsuccessful Bolt execution result (status: {bolt_resp.status}, body: {bolt_resp.body})"
        )
