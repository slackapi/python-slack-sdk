import logging

logging.basicConfig(level=logging.DEBUG)

import os
from threading import Event
from slack_sdk.web import WebClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.websocket_client import SocketModeClient

client = SocketModeClient(
    app_token=os.environ.get("SLACK_SDK_TEST_SOCKET_MODE_APP_TOKEN"),
    web_client=WebClient(
        token=os.environ.get("SLACK_SDK_TEST_SOCKET_MODE_BOT_TOKEN"),
        # pip3 install proxy.py
        # proxy --port 9000 --log-level d
        proxy="http://localhost:9000",
    ),
    trace_enabled=True,
    # pip3 install proxy.py
    # proxy --port 9000 --log-level d
    http_proxy_host="localhost",
    http_proxy_port=9000,
    http_proxy_auth=("user", "pass"),
)

if __name__ == "__main__":

    def process(client: SocketModeClient, req: SocketModeRequest):
        if req.type == "events_api":
            response = SocketModeResponse(envelope_id=req.envelope_id)
            client.send_socket_mode_response(response)
            client.web_client.reactions_add(
                name="eyes",
                channel=req.payload["event"]["channel"],
                timestamp=req.payload["event"]["ts"],
            )

    client.socket_mode_request_listeners.append(process)
    client.connect()
    Event().wait()
