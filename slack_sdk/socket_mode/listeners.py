from typing import Optional

from slack_sdk.socket_mode.request import SocketModeRequest


class WebSocketMessageListener:
    def __call__(
        self,
        receiver: "SocketModeClient",  # noqa: F821
        message: dict,
        raw_message: Optional[str] = None,
    ):
        raise NotImplementedError()


class SocketModeRequestListener:
    def __call__(
        self, receiver: "SocketModeClient", request: SocketModeRequest  # noqa: F821
    ):
        raise NotImplementedError()
