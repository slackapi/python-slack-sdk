import logging
import unittest
from typing import Optional, List, Tuple

from slack_sdk.socket_mode.builtin.frame_header import FrameHeader
from slack_sdk.socket_mode.builtin.internals import _fetch_messages


class TestBuiltin(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def test_parse_test_server_response_1(self):
        def receive():
            return b"\n\x8a7230b6da2-4280-46b3-9ab0-986d4093c5a1:1610196543.3950982\x8a6230b6da2-4280-46b3-9ab0-986d4093c5a1:1610196543.395274"

        messages: List[Tuple[Optional[FrameHeader], bytes]] = _fetch_messages(
            messages=[],
            receive=receive,
            logger=self.logger,
        )
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0], (None, b"\n"))
        self.assertEqual(messages[1][0].opcode, FrameHeader.OPCODE_PONG)
        self.assertEqual(messages[1][1], b"230b6da2-4280-46b3-9ab0-986d4093c5a1:1610196543.3950982")
        self.assertEqual(messages[2][0].opcode, FrameHeader.OPCODE_PONG)
        self.assertEqual(messages[2][1], b"230b6da2-4280-46b3-9ab0-986d4093c5a1:1610196543.395274")

    def test_parse_test_server_response_2(self):
        socket_data = [
            b'\x81\x03foo\x81~\x03@{"envelope_id":"08cfc559-d933-402e-a5c1-79e135afaae4","payload":{"token":"xxx","team_id":"T111","api_app_id":"A111","event":{"client_msg_id":"c9b466b5-845c-49c6-a371-57ae44359bf1","type":"message","text":"<@W111>","user":"U111","ts":"1610197986.000300","team":"T111","blocks":[{"type":"rich_text","block_id":"1HBPc","elements":[{"type":"rich_text_section","elements":[{"type":"user","user_id":"U111"}]}]}],"channel":"C111","event_ts":"1610197986.000300","channel_type":"channel"},"type":"event_callback","event_id":"Ev111","event_time":1610197986,"authorizations":[{"enterprise_id":null,"team_id":"T111","user_id":"U111","is_bot":true,"is_enterprise_install":false}],"is_ext_shared_channel":false,"event_context":"1-message-T111-C111"},"type":"events_api","accepts_response_payload":false,"retry_attempt":1,"retry_reason":"timeout"}\x81\x03bar\x81~\x01\x83{"envelope_id":"57d6a792-4d35-4d0b-b6aa-3361493e1caf","payload":{"type":"shortcut","token":"xxx","action_ts":"1610198080.300836","team":{"id":"T111","domain":"seratch"},"user',
            b'":{"id":"U111","username":"seratch","team_id":"T111"},"is_enterprise_install":false,"enterprise":null,"callback_id":"do-something","trigger_id":"111.222.xxx"},"type":"interactive","accepts_response_payload":false}\x81\x03baz',
        ]

        def receive():
            if len(socket_data) > 0:
                return socket_data.pop(0)
            else:
                return bytes()

        messages: List[Tuple[Optional[FrameHeader], bytes]] = _fetch_messages(
            messages=[],
            receive=receive,
            logger=self.logger,
        )
        self.assertEqual(len(messages), 5)
        self.assertEqual(messages[0][1], b"foo")
        self.assertEqual(messages[2][1], b"bar")
        self.assertEqual(messages[4][1], b"baz")
