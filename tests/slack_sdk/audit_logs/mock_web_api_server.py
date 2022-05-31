import json
import logging
import re
import sys
import threading
import time
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
from multiprocessing.context import Process
from typing import Type
from unittest import TestCase
from urllib.request import Request, urlopen

from tests.helpers import get_mock_server_mode


class MockHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    default_request_version = "HTTP/1.1"
    logger = logging.getLogger(__name__)

    pattern_for_language = re.compile("python/(\\S+)", re.IGNORECASE)
    pattern_for_package_identifier = re.compile("slackclient/(\\S+)")

    def is_valid_user_agent(self):
        user_agent = self.headers["User-Agent"]
        return self.pattern_for_language.search(user_agent) and self.pattern_for_package_identifier.search(user_agent)

    def set_common_headers(self):
        self.send_header("content-type", "application/json;charset=utf-8")
        self.send_header("connection", "close")
        self.end_headers()

    def do_GET(self):
        if self.path == "/received_requests.json":
            self.send_response(200)
            self.set_common_headers()
            self.wfile.write(json.dumps(self.received_requests).encode("utf-8"))
            return

        header = self.headers["Authorization"]
        if header is not None and "xoxp-" in header:
            pattern = str(header).split("xoxp-", 1)[1]
            if "remote_disconnected" in pattern:
                # http.client.RemoteDisconnected
                self.finish()
                return
            if "ratelimited" in pattern:
                self.send_response(429)
                self.send_header("retry-after", 1)
                self.set_common_headers()
                self.wfile.write("""{"ok": false, "error": "ratelimited"}""".encode("utf-8"))
                return

        try:
            if self.path == "/error":
                self.send_response(500)
                self.set_common_headers()
                self.wfile.write("unexpected response body".encode("utf-8"))
                return

            if self.path == "/timeout":
                time.sleep(2)

            # user-agent-this_is-test
            if self.path.startswith("/user-agent-"):
                elements = self.path.split("-")
                prefix, suffix = elements[2], elements[-1]
                ua: str = self.headers["User-Agent"]
                if ua.startswith(prefix) and ua.endswith(suffix):
                    self.send_response(HTTPStatus.OK)
                    self.set_common_headers()
                    self.wfile.write("ok".encode("utf-8"))
                    self.wfile.close()
                    return
                else:
                    self.send_response(HTTPStatus.BAD_REQUEST)
                    self.set_common_headers()
                    self.wfile.write("invalid user agent".encode("utf-8"))
                    self.wfile.close()
                    return

            body = "{}"

            if self.path.startswith("/logs"):
                body = """{"entries":[{"id":"xxx-yyy-zzz-111","date_create":1611221649,"action":"user_login","actor":{"type":"user","user":{"id":"W111","name":"your name","email":"foo@example.com","team":"E111"}},"entity":{"type":"user","user":{"id":"W111","name":"your name","email":"foo@example.com","team":"E111"}},"context":{"location":{"type":"workspace","id":"T111","name":"WS","domain":"foo-bar-baz"},"ua":"UA","ip_address":"1.2.3.4","session_id":1656410836837}},{"id":"32c68de4-cbfa-4fcb-9780-25fdd5aacf32","date_create":1611221649,"action":"user_login","actor":{"type":"user","user":{"id":"W111","name":"your name","email":"foo@example.com","team":"E111"}},"entity":{"type":"user","user":{"id":"W111","name":"your name","email":"foo@example.com","team":"E111"}},"context":{"location":{"type":"workspace","id":"T111","name":"WS","domain":"foo-bar-baz"},"ua":"UA","ip_address":"1.2.3.4","session_id":1656410836837}}],"response_metadata":{"next_cursor":"xxx"}}"""
            if self.path == "/schemas":
                body = """{"schemas":[{"type":"workspace","workspace":{"id":"string","name":"string","domain":"string"}},{"type":"enterprise","enterprise":{"id":"string","name":"string","domain":"string"}},{"type":"user","user":{"id":"string","name":"string","email":"string","team":"string"}},{"type":"file","file":{"id":"string","name":"string","filetype":"string","title":"string"}},{"type":"channel","channel":{"id":"string","name":"string","privacy":"string","is_shared":"bool","is_org_shared":"bool","teams_shared_with":"Optional: varray<string>"}},{"type":"app","app":{"id":"string","name":"string","is_distributed":"bool","is_directory_approved":"bool","is_workflow_app":"bool","scopes":"array"}},{"type":"workflow","workflow":{"id":"string","name":"string"}},{"type":"barrier","barrier":{"id":"string","primary_usergroup":"string","barriered_from_usergroup":"string"}},{"type":"message","message":{"team":"string","channel":"string","timestamp":"string"}}]}"""
            if self.path == "/actions":
                body = """{"actions":{"workspace_or_org":["workspace_created","workspace_deleted","organization_created","organization_deleted","organization_renamed","organization_domain_changed","organization_accepted_migration","organization_declined_migration","emoji_added","emoji_removed","emoji_aliased","emoji_renamed","billing_address_added","migration_scheduled","workspace_accepted_migration","workspace_declined_migration","migration_completed","migration_dms_mpdms_completed","corporate_exports_approved","corporate_exports_enabled","manual_export_started","manual_export_completed","manual_export_downloaded","manual_export_deleted","scheduled_export_started","scheduled_export_completed","scheduled_export_downloaded","scheduled_export_deleted","channels_export_started","channels_export_completed","channels_export_downloaded","channels_export_deleted","manual_user_export_started","manual_user_export_completed","manual_user_export_downloaded","manual_user_export_deleted","ekm_enrolled","ekm_unenrolled","ekm_key_added","ekm_key_removed","ekm_clear_cache_set","ekm_logging_config_set","ekm_slackbot_enroll_notification_sent","ekm_slackbot_unenroll_notification_sent","ekm_slackbot_rekey_notification_sent","ekm_slackbot_logging_notification_sent","approved_orgs_added","approved_orgs_removed","organization_verified","organization_unverified","organization_public_url_updated","pref.admin_retention_override_changed","pref.allow_calls","pref.dlp_access_changed","pref.allow_message_deletion","pref.retention_override_changed","pref.app_dir_only","pref.app_whitelist_enabled","pref.block_file_download_for_unapproved_ip","pref.can_receive_shared_channels_invites","pref.commands_only_regular","pref.custom_tos","pref.disallow_public_file_urls","pref.display_real_names","pref.dm_retention_changed","pref.dnd_enabled","pref.dnd_end_hour","pref.dnd_start_hour","pref.emoji_only_admins","pref.ent_required_browser","pref.enterprise_default_channels","pref.block_download_and_copy_on_untrusted_mobile","pref.enterprise_mobile_device_check","pref.enterprise_team_creation_request","pref.file_retention_changed","pref.private_channel_retention_changed","pref.hide_referers","pref.loading_only_admins","pref.mobile_secondary_auth_timeout_changed","pref.msg_edit_window_mins","pref.notification_redaction_type","pref.required_minimum_mobile_version_changed","pref.public_channel_retention_changed","pref.session_duration_changed","pref.session_duration_type_changed","pref.sign_in_with_slack_disabled","pref.slackbot_responses_disabled","pref.slackbot_responses_only_admins","pref.stats_only_admins","pref.two_factor_auth_changed","pref.username_policy","pref.who_can_archive_channels","pref.who_can_create_public_channels","pref.who_can_create_delete_user_groups","pref.who_can_create_private_channels","pref.who_can_edit_user_groups","pref.who_can_remove_from_public_channels","pref.who_can_remove_from_private_channels","pref.who_can_manage_channel_posting_prefs","pref.who_can_manage_ext_shared_channels","pref.who_can_manage_guests","pref.who_can_manage_shared_channels","pref.sso_setting_changed"],"user":["custom_tos_accepted","guest_created","guest_deactivated","guest_reactivated","owner_transferred","role_change_to_admin","role_change_to_guest","role_change_to_owner","role_change_to_user","user_created","user_deactivated","user_login","user_login_failed","user_logout","user_reactivated","guest_expiration_set","guest_expiration_cleared","guest_expired","user_logout_compromised","user_session_reset_by_admin","user_session_invalidated","user_logout_non_compliant_mobile_app_version","user_force_upgrade_non_compliant_mobile_app_version"],"file":["file_downloaded","file_uploaded","file_public_link_created","file_public_link_revoked","file_shared","file_downloaded_blocked"],"channel":["user_channel_join","user_channel_leave","guest_channel_join","guest_channel_leave","public_channel_created","private_channel_created","public_channel_deleted","private_channel_deleted","public_channel_archive","private_channel_archive","public_channel_unarchive","private_channel_unarchive","mpim_converted_to_private","public_channel_converted_to_private","group_converted_to_channel","channel_workspaces_updated","external_shared_channel_invite_sent","external_shared_channel_invite_accepted","external_shared_channel_invite_approved","external_shared_channel_invite_created","external_shared_channel_invite_declined","external_shared_channel_invite_expired","external_shared_channel_invite_revoked","external_shared_channel_invite_auto_revoked","external_shared_channel_connected","external_shared_channel_disconnected","external_shared_channel_reconnected","channel_moved","channel_posting_pref_changed_from_org_level","channel_renamed","channel_email_address_created","channel_email_address_deleted"],"app":["app_installed","app_uninstalled","app_scopes_expanded","app_approved","app_restricted","app_removed_from_whitelist","app_resources_granted","app_token_preserved","workflow_app_token_preserved","bot_token_upgraded","bot_token_downgraded","org_app_workspace_added","org_app_workspace_removed","org_app_future_workspace_install_enabled","org_app_future_workspace_install_disabled","org_app_upgraded_to_org_install"],"workflow_builder":["workflow_created","workflow_deleted","workflow_published","workflow_unpublished","workflow_responses_csv_download"],"barrier":["barrier_created","barrier_updated","barrier_deleted"],"message":["message_tombstoned","message_restored"]}}"""

            self.send_response(HTTPStatus.OK)
            self.set_common_headers()
            self.wfile.write(body.encode("utf-8"))
            self.wfile.close()

        except Exception as e:
            self.logger.error(str(e), exc_info=True)
            raise


class MockServerProcessTarget:
    def __init__(self, handler: Type[SimpleHTTPRequestHandler] = MockHandler):
        self.handler = handler

    def run(self):
        self.handler.received_requests = {}
        self.server = HTTPServer(("localhost", 8888), self.handler)
        try:
            self.server.serve_forever(0.05)
        finally:
            self.server.server_close()

    def stop(self):
        self.handler.received_requests = {}
        self.server.shutdown()
        self.join()


class MonitorThread(threading.Thread):
    def __init__(self, test: TestCase, handler: Type[SimpleHTTPRequestHandler] = MockHandler):
        threading.Thread.__init__(self, daemon=True)
        self.handler = handler
        self.test = test
        self.test.mock_received_requests = None
        self.is_running = True

    def run(self) -> None:
        while self.is_running:
            try:
                req = Request(f"{self.test.server_url}/received_requests.json")
                resp = urlopen(req, timeout=1)
                self.test.mock_received_requests = json.loads(resp.read().decode("utf-8"))
            except Exception as e:
                # skip logging for the initial request
                if self.test.mock_received_requests is not None:
                    logging.getLogger(__name__).exception(e)
            time.sleep(0.01)

    def stop(self):
        self.is_running = False
        self.join()


class MockServerThread(threading.Thread):
    def __init__(self, test: TestCase, handler: Type[SimpleHTTPRequestHandler] = MockHandler):
        threading.Thread.__init__(self)
        self.handler = handler
        self.test = test

    def run(self):
        self.server = HTTPServer(("localhost", 8888), self.handler)
        self.test.server_url = "http://localhost:8888"
        self.test.host, self.test.port = self.server.socket.getsockname()
        self.test.server_started.set()  # threading.Event()

        self.test = None
        try:
            self.server.serve_forever()
        finally:
            self.server.server_close()

    def stop(self):
        self.server.shutdown()
        self.join()


def setup_mock_web_api_server(test: TestCase):
    if get_mock_server_mode() == "threading":
        test.server_started = threading.Event()
        test.thread = MockServerThread(test)
        test.thread.start()
        test.server_started.wait()
    else:
        # start a mock server as another process
        target = MockServerProcessTarget()
        test.server_url = "http://localhost:8888"
        test.host, test.port = "localhost", 8888
        test.process = Process(target=target.run, daemon=True)
        test.process.start()

        time.sleep(0.1)

        # start a thread in the current process
        # this thread fetches mock_received_requests from the remote process
        test.monitor_thread = MonitorThread(test)
        test.monitor_thread.start()
        count = 0
        # wait until the first successful data retrieval
        while test.mock_received_requests is None:
            time.sleep(0.01)
            count += 1
            if count >= 100:
                raise Exception("The mock server is not yet running!")


def cleanup_mock_web_api_server(test: TestCase):
    if get_mock_server_mode() == "threading":
        test.thread.stop()
        test.thread = None
    else:
        # stop the thread to fetch mock_received_requests from the remote process
        test.monitor_thread.stop()

        retry_count = 0
        # terminate the process
        while test.process.is_alive():
            test.process.terminate()
            time.sleep(0.01)
            retry_count += 1
            if retry_count >= 100:
                raise Exception("Failed to stop the mock server!")

        # Python 3.6 does not have this method
        if sys.version_info.major == 3 and sys.version_info.minor > 6:
            # cleanup the process's resources
            test.process.close()

        test.process = None
