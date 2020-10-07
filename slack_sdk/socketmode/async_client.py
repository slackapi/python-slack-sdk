import json
import asyncio
import websockets
from typing import Optional
from slack_sdk import WebClient


class SocketModeClient(object):

    connected: bool = False
    authenticated: bool = False

    websocket = None
    secondary_websocket = None

    web_client = None

    event_listeners = {}
    interactive_listeners = {}
    all_listener = None

    connections = set()

    def __init__(
        self,
        token: str,
        auto_reconnect: Optional[bool] = True,
        client_ping_timeout: Optional[int] = 30000,
        client_options: Optional[dict] = {},
    ):
        self.token = token.strip()
        self.auto_reconnect = auto_reconnect

        # self._logger = logging.getLogger(__name__)
        self.client_options = client_options

        print('token', self.token)
        print('client_options', client_options)
        self.web_client = WebClient(
            token=self.token,
            **self.client_options,
        )

    async def start(self):
        await self.ws_handler()

    async def ws_handler(self):
        # State: Disconnected
        # Initial State

        # This while loop handles reconnections
        while True:
            try:
                # State: Connecting
                #   State: Authenticating
                #   api call to apps.connections.open
                ws_url = self.get_ws_url()

                #   State: Authenticated
                #   connect to websocket
                await self.setup_websocket(ws_url)
            # except socket.gaierror:
            #     print('socket gaierror')
            #     continue
            except ConnectionRefusedError:
                print('connection refused error')
                continue

    # State: Disconnecting
    # State: Reconnecting

    async def setup_websocket(self, ws_url):
        # TODO: pass proxy and agent to websocket connection
        # TODO: This should be a separate function so I can open more than one websocket
        # Have manager class with manager object instead of async with 
        async with websockets.connect(ws_url) as socket:
            self.websocket = socket
            # if self.websocket is None:
            #     print('self.websocket is None')
            #     self.websocket = socket
            # else:
            #     print('creating secondary socket')
            #     # Creating secondary Websocket
            #     self.secondary_websocket = socket

            while True:
                try:
                    # State: Connected
                    event = json.loads(await socket.recv())
                    print(f"<(down) {event}")

                    event_type = event['type']

                    reason = event['reason'] if 'reason' in event else None

                    print('reason', reason)

                    print('eventType', event_type)

                    if event_type == 'hello':
                        # State: Ready
                        print('hello')
                        continue

                    if event_type == 'disconnect' and reason == 'warning':
                        print('disconnect warning')
                        # create new websocket connection
                        # TODO: creating a new connection here essentially destroys the first connection
                        # await self.reconnect()
                        continue

                    if event_type == 'disconnect' and reason == 'refresh_requested':
                        print('refresh requested')
                        # websocket will auto close
                        # set secondary websocket as primary
                        continue

                    envelope_id = event['envelope_id']
                    event_payload = event['payload']

                    def ack(*response: dict):
                        print('calling ack', event_type)
                        self.send(envelope_id, response)
                    
                    response = {'body': event_payload, 'ack': ack}

                    if event_type == 'events_api':
                        # print(listeners)
                        print('events_api')
                        response['event'] = event_payload['event']
                        # cycle through registered event listeners to see if a matching one exists
                        for e_type in self.event_listeners:
                            if e_type in event_payload.get('event', {}).get('type'):
                                print('event_type =', e_type)
                                # task = asyncio.create_task(self.event_listeners[e_type])
                                # await task
                                asyncio.get_running_loop().run_in_executor(None, self.event_listeners[e_type], response)
                                # Ensure task, detect complication of task, can't use await
                                # Wrap executor in future, don't do this
                                # manage background execution, once completed, send result to websocket
                    elif event_type == 'interactive':
                        print('interactive message')
                        print('event_type', event_type)
                        # response.action = event_payload('')
                        asyncio.get_running_loop().run_in_executor(None, self.interactive_listener, response)
                    else:
                        # TODO: create listeners for other payload types
                        print('need to create listeners for other types')

                    # All listener
                    if self.all_listener is not None:
                        print('all listener is defined')
                        asyncio.get_running_loop().run_in_executor(None, self.all_listener, response)
                    else:
                        print('all listener is Not defined')
                except Exception:
                    print('outside try')
                    print(Exception)
                    # socket disconnected, break out of this while loop
                    break
                    # switch secondary socket to primary
                    # await self.reconnect()

    def all(self):
        def inner(fcn):
            self.all_listener = fcn
        return inner

    def event(self, event_type=None):
        def inner(fcn):
            print('eventType')
            if event_type is None:
                print('You must provide an event type when creating an event listener')
            else:
                self.event_listeners[event_type] = fcn
        return inner

    def interactive(self):
        def inner(fcn):
            print('interactive')
            self.interactive_listener = fcn
        return inner

    def send(self, envelope_id, response={}):
        print('in send')
        # TODO: add response to response_msg
        response_msg = {'envelope_id': envelope_id}
        print(response_msg)
        self.websocket.send(json.dumps(response_msg))

    def get_ws_url(self) -> str:
        print('in get_ws_url')
        # If I use async webclient, i could await
        r = self.web_client.api_call(api_method='apps.connections.open')
        return r['url']

    def disconnect(self):
        # TODO: Implement this
        print('need to disconnect websocket')

    # async def reconnect(self):
    #     ws_url = self.get_ws_url()

    #     #   State: Authenticated
    #     #   connect to websocket
    #     await self.setup_websocket(ws_url)
