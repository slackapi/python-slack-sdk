import os
from time import time
from typing import Optional

from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.websocket_client import SocketModeClient

from slack_bolt import App
from .base_handler import BaseSocketModeHandler
from .internals import run_bolt_app, send_response
from slack_bolt.response import BoltResponse


class SocketModeHandler(BaseSocketModeHandler):
    app: App  # type: ignore
    app_token: str
    client: SocketModeClient

    def __init__(  # type: ignore
        self,
        app: App,  # type: ignore
        app_token: Optional[str] = None,
    ):
        self.app = app
        self.app_token = app_token or os.environ["SLACK_APP_TOKEN"]
        self.client = SocketModeClient(app_token=self.app_token)
        self.client.socket_mode_request_listeners.append(self.handle)

    def handle(self, client: SocketModeClient, req: SocketModeRequest) -> None:
        start = time()
        bolt_resp: BoltResponse = run_bolt_app(self.app, req)
        send_response(client, req, bolt_resp, start)
