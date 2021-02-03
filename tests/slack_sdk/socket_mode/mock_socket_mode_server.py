import logging

socket_mode_envelopes = [
    """{"envelope_id":"1d3c79ab-0ffb-41f3-a080-d19e85f53649","payload":{"token":"verification-token","team_id":"T111","team_domain":"xxx","channel_id":"C111","channel_name":"random","user_id":"U111","user_name":"seratch","command":"/hello-socket-mode","text":"","api_app_id":"A111","response_url":"https://hooks.slack.com/commands/T111/111/xxx","trigger_id":"111.222.xxx"},"type":"slash_commands","accepts_response_payload":true}""",
    """{"envelope_id":"cda4159a-72a5-4744-aba3-4d66eb52682b","payload":{"token":"verification-token","team_id":"T111","api_app_id":"A111","event":{"client_msg_id":"f0582a78-72db-4feb-b2f3-1e47d66365c8","type":"app_mention","text":"<@U111>","user":"U222","ts":"1610241741.000200","team":"T111","blocks":[{"type":"rich_text","block_id":"Sesm","elements":[{"type":"rich_text_section","elements":[{"type":"user","user_id":"U111"}]}]}],"channel":"C111","event_ts":"1610241741.000200"},"type":"event_callback","event_id":"Ev111","event_time":1610241741,"authorizations":[{"enterprise_id":null,"team_id":"T111","user_id":"U222","is_bot":true,"is_enterprise_install":false}],"is_ext_shared_channel":false,"event_context":"1-app_mention-T111-C111"},"type":"events_api","accepts_response_payload":false,"retry_attempt":0,"retry_reason":""}""",
    """{"envelope_id":"57d6a792-4d35-4d0b-b6aa-3361493e1caf","payload":{"type":"shortcut","token":"verification-token","action_ts":"1610198080.300836","team":{"id":"T111","domain":"seratch"},"user":{"id":"U111","username":"seratch","team_id":"T111"},"is_enterprise_install":false,"enterprise":null,"callback_id":"do-something","trigger_id":"111.222.xxx"},"type":"interactive","accepts_response_payload":false}""",
    """{"envelope_id":"ac2cfd40-6f8c-4d5e-a1ad-646e532baa19","payload":{"token":"verification-token","team_id":"T111","api_app_id":"A111","event":{"client_msg_id":"f0582a78-72db-4feb-b2f3-1e47d66365c8","type":"message","text":"<@U111> Hi here!","user":"U222","ts":"1610241741.000200","team":"T111","channel":"C111","event_ts":"1610241741.000200","channel_type":"channel"},"type":"event_callback","event_id":"Ev111","event_time":1610241741,"authorizations":[{"enterprise_id":null,"team_id":"T111","user_id":"U333","is_bot":true,"is_enterprise_install":false}],"is_ext_shared_channel":false,"event_context":"1-message-T111-C111"},"type":"events_api","accepts_response_payload":false,"retry_attempt":0,"retry_reason":""}""",
]

socket_mode_hello_message = """{"type":"hello","num_connections":2,"debug_info":{"host":"applink-111-xxx","build_number":10,"approximate_connection_time":18060},"connection_info":{"app_id":"A111"}}"""

from flask import Flask
from flask_sockets import Sockets


def start_socket_mode_server(self, port: int):
    def _start_socket_mode_server():
        logger = logging.getLogger(__name__)
        app: Flask = Flask(__name__)
        sockets: Sockets = Sockets(app)

        state = {
            "hello_sent": False,
            "envelopes_to_consume": list(socket_mode_envelopes),
        }

        @sockets.route("/link")
        def link(ws):
            while not ws.closed:
                message = ws.read_message()
                if message is not None:
                    if not state["hello_sent"]:
                        ws.send(socket_mode_hello_message)
                        state["hello_sent"] = True

                    if len(state.get("envelopes_to_consume")) > 0:
                        e = state.get("envelopes_to_consume").pop(0)
                        logger.debug(f"Send an envelope: {e}")
                        ws.send(e)

                    logger.debug(f"Server received a message: {message}")
                    ws.send(message)

        from gevent import pywsgi
        from geventwebsocket.handler import WebSocketHandler

        server = pywsgi.WSGIServer(("", port), app, handler_class=WebSocketHandler)
        self.server = server

        def reset_sever_state():
            state["hello_sent"] = False
            state["envelopes_to_consume"] = list(socket_mode_envelopes)

        self.reset_sever_state = reset_sever_state

        server.serve_forever(stop_timeout=1)

    return _start_socket_mode_server
