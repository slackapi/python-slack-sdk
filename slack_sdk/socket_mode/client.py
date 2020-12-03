import json
import logging
from queue import Queue
from concurrent.futures.thread import ThreadPoolExecutor
from logging import Logger
from threading import Lock
from typing import Dict, Union, Any, Optional, List, Callable

from slack_sdk.errors import SlackApiError
from slack_sdk.socket_mode.listeners import (
    WebSocketMessageListener,
    SocketModeRequestListener,
)
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.web import WebClient


class BaseSocketModeClient:
    logger: Logger
    web_client: WebClient
    app_token: str
    wss_uri: str
    message_queue: Queue
    message_listeners: List[
        Union[
            WebSocketMessageListener,
            Callable[["BaseSocketModeClient", dict, Optional[str]], None],
        ]
    ]
    socket_mode_request_listeners: List[
        Union[
            SocketModeRequestListener,
            Callable[["BaseSocketModeClient", SocketModeRequest], None],
        ]
    ]

    message_processor: ThreadPoolExecutor
    message_workers: ThreadPoolExecutor

    connect_operation_lock: Lock

    def issue_new_wss_url(self) -> str:
        try:
            response = self.web_client.apps_connections_open(app_token=self.app_token)
            return response["url"]
        except SlackApiError as e:
            self.logger.error(f"Failed to retrieve Socket Mode URL: {e}")
            raise e

    def is_connected(self) -> bool:
        return False

    def connect(self) -> None:
        raise NotImplementedError()

    def disconnect(self) -> None:
        raise NotImplementedError()

    def connect_to_new_endpoint(self):
        try:
            self.connect_operation_lock.acquire(blocking=True, timeout=5)
            if not self.is_connected():
                self.wss_uri = self.issue_new_wss_url()
                self.connect()
        finally:
            self.connect_operation_lock.release()

    def close(self) -> None:
        self.disconnect()

    def send_message(self, message: str) -> None:
        raise NotImplementedError()

    def send_socket_mode_response(
        self, response: Union[Dict[str, Any], SocketModeResponse]
    ) -> None:
        if isinstance(response, SocketModeResponse):
            self.send_message(json.dumps(response.to_dict()))
        else:
            self.send_message(json.dumps(response))

    def enqueue_message(self, message: str):
        self.message_queue.put(message)
        if self.logger.level <= logging.DEBUG:
            self.logger.debug(
                f"A new message enqueued (current queue size: {self.message_queue.qsize()})"
            )

    def process_message(self):
        raw_message = self.message_queue.get()

        def _run_message_listeners():
            if raw_message is not None and raw_message.startswith("{"):
                message: dict = json.loads(raw_message)
                self.run_message_listeners(message, raw_message)

        self.message_workers.submit(_run_message_listeners)

    def run_message_listeners(self, message: dict, raw_message: str) -> None:
        type, envelope_id = message.get("type"), message.get("envelope_id")
        if self.logger.level <= logging.DEBUG:
            self.logger.debug(
                f"Message processing started (type: {type}, envelope_id: {envelope_id})"
            )
        try:
            if message.get("type") == "disconnect":
                self.connect_to_new_endpoint()
                return

            for listener in self.message_listeners:
                try:
                    listener(self, message, raw_message)
                except Exception as e:
                    self.logger.exception(f"Failed to run a message listener: {e}")

            if len(self.socket_mode_request_listeners) > 0:
                request = SocketModeRequest.from_dict(message)
                if request is not None:
                    for listener in self.socket_mode_request_listeners:
                        try:
                            listener(self, request)
                        except Exception as e:
                            self.logger.exception(
                                f"Failed to run a request listener: {e}"
                            )
        except Exception as e:
            self.logger.exception(f"Failed to run message listeners: {e}")
        finally:
            if self.logger.level <= logging.DEBUG:
                self.logger.debug(
                    f"Message processing completed (type: {type}, envelope_id: {envelope_id})"
                )

    def process_messages(self) -> None:
        while True:
            try:
                self.process_message()
            except Exception as e:
                self.logger.exception(f"Failed to process a message: {e}")
