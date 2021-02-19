import logging
from threading import Event

from slack_sdk.socket_mode.client import BaseSocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest

from slack_bolt import App


class BaseSocketModeHandler:
    app: App  # type: ignore
    client: BaseSocketModeClient

    def handle(self, client: BaseSocketModeClient, req: SocketModeRequest) -> None:
        raise NotImplementedError()

    def connect(self):
        self.client.connect()

    def disconnect(self):
        self.client.disconnect()

    def close(self):
        self.client.close()

    def start(self):
        self.connect()
        if self.app.logger.level > logging.INFO:
            print("⚡️ Bolt app is running!")
        else:
            self.app.logger.info("⚡️ Bolt app is running!")
        Event().wait()
