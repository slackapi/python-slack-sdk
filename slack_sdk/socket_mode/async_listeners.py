from typing import Optional, Callable

from slack_sdk.socket_mode.request import SocketModeRequest


class AsyncWebSocketMessageListener(Callable):
    async def __call__(
        client: "AsyncBaseSocketModeClient",
        message: dict,
        raw_message: Optional[str] = None,
    ):
        raise NotImplementedError()


class AsyncSocketModeRequestListener(Callable):
    async def __call__(
        client: "AsyncBaseSocketModeClient", request: SocketModeRequest,
    ):
        raise NotImplementedError()
