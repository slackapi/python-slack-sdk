import os
import unittest

import slack
from slack.web.classes.blocks import DividerBlock
from slack.web.classes.views import View
from tests.web.mock_web_api_server import setup_mock_web_api_server, cleanup_mock_web_api_server


class TestWebClientCoverage(unittest.TestCase):
    # 205 endpoints as of July 16, 2020
    # Can be fetched by running `var methodNames = [].slice.call(document.getElementsByClassName('bold')).map(e => e.text);console.log(methodNames.toString());console.log(methodNames.length);` on https://api.slack.com/methods
    all_api_methods = "admin.apps.approve,admin.apps.restrict,admin.apps.approved.list,admin.apps.requests.list,admin.apps.restricted.list,admin.conversations.restrictAccess.addGroup,admin.conversations.restrictAccess.listGroups,admin.conversations.restrictAccess.removeGroup,admin.conversations.setTeams,admin.emoji.add,admin.emoji.addAlias,admin.emoji.list,admin.emoji.remove,admin.emoji.rename,admin.inviteRequests.approve,admin.inviteRequests.deny,admin.inviteRequests.list,admin.inviteRequests.approved.list,admin.inviteRequests.denied.list,admin.teams.admins.list,admin.teams.create,admin.teams.list,admin.teams.owners.list,admin.teams.settings.info,admin.teams.settings.setDefaultChannels,admin.teams.settings.setDescription,admin.teams.settings.setDiscoverability,admin.teams.settings.setIcon,admin.teams.settings.setName,admin.usergroups.addChannels,admin.usergroups.addTeams,admin.usergroups.listChannels,admin.usergroups.removeChannels,admin.users.assign,admin.users.invite,admin.users.list,admin.users.remove,admin.users.setAdmin,admin.users.setExpiration,admin.users.setOwner,admin.users.setRegular,admin.users.session.reset,api.test,apps.permissions.info,apps.permissions.request,apps.permissions.resources.list,apps.permissions.scopes.list,apps.permissions.users.list,apps.permissions.users.request,apps.uninstall,auth.revoke,auth.test,bots.info,calls.add,calls.end,calls.info,calls.update,calls.participants.add,calls.participants.remove,chat.delete,chat.deleteScheduledMessage,chat.getPermalink,chat.meMessage,chat.postEphemeral,chat.postMessage,chat.scheduleMessage,chat.unfurl,chat.update,chat.scheduledMessages.list,conversations.archive,conversations.close,conversations.create,conversations.history,conversations.info,conversations.invite,conversations.join,conversations.kick,conversations.leave,conversations.list,conversations.mark,conversations.members,conversations.open,conversations.rename,conversations.replies,conversations.setPurpose,conversations.setTopic,conversations.unarchive,dialog.open,dnd.endDnd,dnd.endSnooze,dnd.info,dnd.setSnooze,dnd.teamInfo,emoji.list,files.comments.delete,files.delete,files.info,files.list,files.revokePublicURL,files.sharedPublicURL,files.upload,files.remote.add,files.remote.info,files.remote.list,files.remote.remove,files.remote.share,files.remote.update,migration.exchange,oauth.access,oauth.token,oauth.v2.access,pins.add,pins.list,pins.remove,reactions.add,reactions.get,reactions.list,reactions.remove,reminders.add,reminders.complete,reminders.delete,reminders.info,reminders.list,rtm.connect,rtm.start,search.all,search.files,search.messages,stars.add,stars.list,stars.remove,team.accessLogs,team.billableInfo,team.info,team.integrationLogs,team.profile.get,usergroups.create,usergroups.disable,usergroups.enable,usergroups.list,usergroups.update,usergroups.users.list,usergroups.users.update,users.conversations,users.deletePhoto,users.getPresence,users.identity,users.info,users.list,users.lookupByEmail,users.setActive,users.setPhoto,users.setPresence,users.profile.get,users.profile.set,views.open,views.publish,views.push,views.update,admin.conversations.whitelist.add,admin.conversations.whitelist.listGroupsLinkedToChannel,admin.conversations.whitelist.remove,channels.archive,channels.create,channels.history,channels.info,channels.invite,channels.join,channels.kick,channels.leave,channels.list,channels.mark,channels.rename,channels.replies,channels.setPurpose,channels.setTopic,channels.unarchive,groups.archive,groups.create,groups.createChild,groups.history,groups.info,groups.invite,groups.kick,groups.leave,groups.list,groups.mark,groups.open,groups.rename,groups.replies,groups.setPurpose,groups.setTopic,groups.unarchive,im.close,im.history,im.list,im.mark,im.open,im.replies,mpim.close,mpim.history,mpim.list,mpim.mark,mpim.open,mpim.replies".split(
        ","
    )

    api_methods_to_call = []
    os.environ.setdefault("SLACKCLIENT_SKIP_DEPRECATION", "1")

    def setUp(self):
        setup_mock_web_api_server(self)
        self.client = slack.WebClient(token="xoxb-coverage", base_url="http://localhost:8888")
        for api_method in self.all_api_methods:
            if api_method.startswith("apps.") or api_method in [
                "oauth.access",
                "oauth.v2.access",
                "oauth.token",
                "users.setActive",
                "admin.conversations.whitelist.add",  # deprecated
                "admin.conversations.whitelist.listGroupsLinkedToChannel",  # deprecated
                "admin.conversations.whitelist.remove",  # deprecated
                "admin.usergroups.addTeams",  # TODO
                "calls.participants.remove",  # TODO
            ]:
                continue
            self.api_methods_to_call.append(api_method)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_coverage(self):
        for api_method in self.all_api_methods:
            if self.api_methods_to_call.count(api_method) == 0:
                continue
            method_name = api_method.replace(".", "_")
            method = getattr(self.client, method_name, None)

            # Run the api calls with required arguments
            if callable(method):
                if method_name == "admin_apps_approve":
                    self.api_methods_to_call.remove(method(app_id="AID123", request_id="RID123")["method"])
                elif method_name == "admin_inviteRequests_approve":
                    self.api_methods_to_call.remove(method(invite_request_id="ID123")["method"])
                elif method_name == "admin_inviteRequests_deny":
                    self.api_methods_to_call.remove(method(invite_request_id="ID123")["method"])
                elif method_name == "admin_teams_admins_list":
                    self.api_methods_to_call.remove(method(team_id="T123")["method"])
                elif method_name == "admin_teams_create":
                    self.api_methods_to_call.remove(
                        method(team_domain="awesome-team", team_name="Awesome Team")["method"])
                elif method_name == "admin_teams_owners_list":
                    self.api_methods_to_call.remove(method(team_id="T123")["method"])
                elif method_name == "admin_teams_settings_info":
                    self.api_methods_to_call.remove(method(team_id="T123")["method"])
                elif method_name == "admin_teams_settings_setDefaultChannels":
                    self.api_methods_to_call.remove(method(team_id="T123", channel_ids=["C123", "C234"])["method"])
                    method(team_id="T123", channel_ids="C123,C234")
                elif method_name == "admin_teams_settings_setDescription":
                    self.api_methods_to_call.remove(
                        method(team_id="T123", description="Workspace for an awesome team")["method"])
                elif method_name == "admin_teams_settings_setDiscoverability":
                    self.api_methods_to_call.remove(method(team_id="T123", discoverability="invite_only")["method"])
                elif method_name == "admin_teams_settings_setIcon":
                    self.api_methods_to_call.remove(method(
                        team_id="T123",
                        image_url="https://www.example.com/images/dummy.png",
                    )["method"])
                elif method_name == "admin_teams_settings_setName":
                    self.api_methods_to_call.remove(method(team_id="T123", name="Awesome Engineering Team")["method"])
                elif method_name == "admin_usergroups_addChannels":
                    self.api_methods_to_call.remove(method(
                        team_id="T123",
                        usergroup_id="S123",
                        channel_ids=["C1A2B3C4D", "C26Z25Y24"],
                    )["method"])
                    method(
                        team_id="T123",
                        usergroup_id="S123",
                        channel_ids="C1A2B3C4D,C26Z25Y24",
                    )
                elif method_name == "admin_usergroups_listChannels":
                    self.api_methods_to_call.remove(method(usergroup_id="S123")["method"])
                    method(usergroup_id="S123", include_num_members=True, team_id="T123")
                    method(usergroup_id="S123", include_num_members="1", team_id="T123")
                    method(usergroup_id="S123", include_num_members=1, team_id="T123")
                    method(usergroup_id="S123", include_num_members=False, team_id="T123")
                    method(usergroup_id="S123", include_num_members="0", team_id="T123")
                    method(usergroup_id="S123", include_num_members=0, team_id="T123")
                elif method_name == "admin_usergroups_removeChannels":
                    self.api_methods_to_call.remove(method(
                        team_id="T123",
                        usergroup_id="S123",
                        channel_ids=["C1A2B3C4D", "C26Z25Y24"],
                    )["method"])
                    method(
                        team_id="T123",
                        usergroup_id="S123",
                        channel_ids="C1A2B3C4D,C26Z25Y24",
                    )
                elif method_name == "admin_users_assign":
                    self.api_methods_to_call.remove(method(team_id="T123", user_id="W123")["method"])
                elif method_name == "admin_users_invite":
                    self.api_methods_to_call.remove(method(
                        team_id="T123",
                        email="test@example.com",
                        channel_ids=["C1A2B3C4D", "C26Z25Y24"],
                    )["method"])
                    method(
                        team_id="T123",
                        email="test@example.com",
                        channel_ids="C1A2B3C4D,C26Z25Y24",
                    )
                elif method_name == "admin_users_list":
                    self.api_methods_to_call.remove(method(team_id="T123")["method"])
                elif method_name == "admin_users_remove":
                    self.api_methods_to_call.remove(method(team_id="T123", user_id="W123")["method"])
                elif method_name == "admin_users_setAdmin":
                    self.api_methods_to_call.remove(method(team_id="T123", user_id="W123")["method"])
                elif method_name == "admin_users_setExpiration":
                    self.api_methods_to_call.remove(method(team_id="T123", user_id="W123", expiration_ts=123)["method"])
                elif method_name == "admin_users_setOwner":
                    self.api_methods_to_call.remove(method(team_id="T123", user_id="W123")["method"])
                elif method_name == "admin_users_setRegular":
                    self.api_methods_to_call.remove(method(team_id="T123", user_id="W123")["method"])
                elif method_name == "admin_users_session_reset":
                    self.api_methods_to_call.remove(method(user_id="W123")["method"])
                elif method_name == "calls_add":
                    self.api_methods_to_call.remove(method(
                        external_unique_id="unique-id",
                        join_url="https://www.example.com",
                    )["method"])
                elif method_name == "calls_end":
                    self.api_methods_to_call.remove(method(id="R111")["method"])
                elif method_name == "calls_info":
                    self.api_methods_to_call.remove(method(id="R111")["method"])
                elif method_name == "calls_participants_add":
                    self.api_methods_to_call.remove(method(
                        id="R111",
                        users=[
                            {
                                "slack_id": "U1H77"
                            },
                            {
                                "external_id": "54321678",
                                "display_name": "External User",
                                "avatar_url": "https://example.com/users/avatar1234.jpg"
                            }
                        ],
                    )["method"])
                elif method_name == "calls_update":
                    self.api_methods_to_call.remove(method(id="R111")["method"])
                elif method_name == "chat_delete":
                    self.api_methods_to_call.remove(method(channel="C123", ts="123.123")["method"])
                elif method_name == "chat_deleteScheduledMessage":
                    self.api_methods_to_call.remove(method(channel="C123", scheduled_message_id="123")["method"])
                elif method_name == "chat_getPermalink":
                    self.api_methods_to_call.remove(method(channel="C123", message_ts="123.123")["method"])
                elif method_name == "chat_meMessage":
                    self.api_methods_to_call.remove(method(channel="C123", text=":wave: Hi there!")["method"])
                elif method_name == "chat_postEphemeral":
                    self.api_methods_to_call.remove(method(channel="C123", user="U123")["method"])
                elif method_name == "chat_postMessage":
                    self.api_methods_to_call.remove(method(channel="C123")["method"])
                elif method_name == "chat_scheduleMessage":
                    self.api_methods_to_call.remove(method(channel="C123", post_at=123, text="Hi")["method"])
                elif method_name == "chat_unfurl":
                    self.api_methods_to_call.remove(method(
                        channel="C123",
                        ts="123.123",
                        unfurls={
                            "https://example.com/": {"text": "Every day is the test."}
                        },
                    )["method"])
                elif method_name == "chat_update":
                    self.api_methods_to_call.remove(method(channel="C123", ts="123.123")["method"])
                elif method_name == "conversations_archive":
                    self.api_methods_to_call.remove(method(channel="C123")["method"])
                elif method_name == "conversations_close":
                    self.api_methods_to_call.remove(method(channel="C123")["method"])
                elif method_name == "conversations_create":
                    self.api_methods_to_call.remove(method(name="announcements")["method"])
                elif method_name == "conversations_history":
                    self.api_methods_to_call.remove(method(channel="C123")["method"])
                elif method_name == "conversations_info":
                    self.api_methods_to_call.remove(method(channel="C123")["method"])
                elif method_name == "conversations_invite":
                    self.api_methods_to_call.remove(
                        method(channel="C123", users=["U2345678901", "U3456789012"])["method"])
                    method(channel="C123", users="U2345678901,U3456789012")
                elif method_name == "conversations_join":
                    self.api_methods_to_call.remove(method(channel="C123")["method"])
                elif method_name == "conversations_kick":
                    self.api_methods_to_call.remove(method(channel="C123", user="U123")["method"])
                elif method_name == "conversations_leave":
                    self.api_methods_to_call.remove(method(channel="C123")["method"])
                elif method_name == "conversations_mark":
                    self.api_methods_to_call.remove(method(channel="C123", ts="123.123")["method"])
                elif method_name == "conversations_members":
                    self.api_methods_to_call.remove(method(channel="C123")["method"])
                elif method_name == "conversations_rename":
                    self.api_methods_to_call.remove(method(channel="C123", name="new-name")["method"])
                elif method_name == "conversations_replies":
                    self.api_methods_to_call.remove(method(channel="C123", ts="123.123")["method"])
                elif method_name == "conversations_setPurpose":
                    self.api_methods_to_call.remove(method(channel="C123", purpose="The purpose")["method"])
                elif method_name == "conversations_setTopic":
                    self.api_methods_to_call.remove(method(channel="C123", topic="The topic")["method"])
                elif method_name == "conversations_unarchive":
                    self.api_methods_to_call.remove(method(channel="C123")["method"])
                elif method_name == "dialog_open":
                    self.api_methods_to_call.remove(method(dialog={}, trigger_id="123")["method"])
                elif method_name == "dnd_setSnooze":
                    self.api_methods_to_call.remove(method(num_minutes=120)["method"])
                elif method_name == "dnd_teamInfo":
                    self.api_methods_to_call.remove(method(users=["123", "U234"])["method"])
                    method(users="U123,U234")
                elif method_name == "files_comments_delete":
                    self.api_methods_to_call.remove(method(file="F123", id="FC123")["method"])
                elif method_name == "files_delete":
                    self.api_methods_to_call.remove(method(file="F123")["method"])
                elif method_name == "files_info":
                    self.api_methods_to_call.remove(method(file="F123")["method"])
                elif method_name == "files_revokePublicURL":
                    self.api_methods_to_call.remove(method(file="F123")["method"])
                elif method_name == "files_sharedPublicURL":
                    self.api_methods_to_call.remove(method(file="F123")["method"])
                elif method_name == "files_upload":
                    self.api_methods_to_call.remove(method(content="This is the content")["method"])
                elif method_name == "files_remote_add":
                    self.api_methods_to_call.remove(method(
                        external_id="123",
                        external_url="https://www.example.com/remote-files/123",
                        title="File title",
                    )["method"])
                elif method_name == "files_remote_share":
                    self.api_methods_to_call.remove(method(channels="C123,G123")["method"])
                    method(channels=["C123", "G123"])
                    method(channels="C123,G123")
                elif method_name == "migration_exchange":
                    self.api_methods_to_call.remove(method(users="U123,U234")["method"])
                    method(users="U123,U234")
                elif method_name == "mpim_open":
                    self.api_methods_to_call.remove(method(users="U123,U234")["method"])
                    method(users="U123,U234")
                elif method_name == "oauth_access":
                    method = getattr(self.no_token_client, method_name, None)
                    method(client_id="123.123", client_secret="secret", code="123456")
                elif method_name == "oauth_v2_access":
                    method = getattr(self.no_token_client, method_name, None)
                    method(client_id="123.123", client_secret="secret", code="123456")
                elif method_name == "pins_add":
                    self.api_methods_to_call.remove(method(channel="C123")["method"])
                elif method_name == "pins_list":
                    self.api_methods_to_call.remove(method(channel="C123")["method"])
                elif method_name == "pins_remove":
                    self.api_methods_to_call.remove(method(channel="C123")["method"])
                elif method_name == "reactions_add":
                    self.api_methods_to_call.remove(method(name="eyes")["method"])
                elif method_name == "reactions_remove":
                    self.api_methods_to_call.remove(method(name="eyes")["method"])
                elif method_name == "reminders_add":
                    self.api_methods_to_call.remove(method(text="The task", time=123)["method"])
                elif method_name == "reminders_complete":
                    self.api_methods_to_call.remove(method(reminder="R123")["method"])
                elif method_name == "reminders_delete":
                    self.api_methods_to_call.remove(method(reminder="R123")["method"])
                elif method_name == "reminders_info":
                    self.api_methods_to_call.remove(method(reminder="R123")["method"])
                elif method_name == "search_all":
                    self.api_methods_to_call.remove(method(query="Slack")["method"])
                elif method_name == "search_files":
                    self.api_methods_to_call.remove(method(query="Slack")["method"])
                elif method_name == "search_messages":
                    self.api_methods_to_call.remove(method(query="Slack")["method"])
                elif method_name == "usergroups_create":
                    self.api_methods_to_call.remove(method(name="Engineering Team")["method"])
                elif method_name == "usergroups_disable":
                    self.api_methods_to_call.remove(method(usergroup="UG123")["method"])
                elif method_name == "usergroups_enable":
                    self.api_methods_to_call.remove(method(usergroup="UG123")["method"])
                elif method_name == "usergroups_update":
                    self.api_methods_to_call.remove(method(usergroup="UG123")["method"])
                elif method_name == "usergroups_users_list":
                    self.api_methods_to_call.remove(method(usergroup="UG123")["method"])
                elif method_name == "usergroups_users_update":
                    self.api_methods_to_call.remove(method(usergroup="UG123", users=["U123", "U234"])["method"])
                    method(usergroup="UG123", users="U123,U234")
                elif method_name == "users_getPresence":
                    self.api_methods_to_call.remove(method(user="U123")["method"])
                elif method_name == "users_info":
                    self.api_methods_to_call.remove(method(user="U123")["method"])
                elif method_name == "users_lookupByEmail":
                    self.api_methods_to_call.remove(method(email="test@example.com")["method"])
                elif method_name == "users_setPhoto":
                    self.api_methods_to_call.remove(method(image="README.md")["method"])
                elif method_name == "users_setPresence":
                    self.api_methods_to_call.remove(method(presence="away")["method"])
                elif method_name == "views_open":
                    self.api_methods_to_call.remove(method(trigger_id="123123", view={})["method"])
                    method(
                        trigger_id="123123",
                        view=View(type="modal", blocks=[DividerBlock()])
                    )
                elif method_name == "views_publish":
                    self.api_methods_to_call.remove(method(user_id="U123", view={})["method"])
                elif method_name == "views_push":
                    self.api_methods_to_call.remove(method(trigger_id="123123", view={})["method"])
                elif method_name == "views_update":
                    self.api_methods_to_call.remove(method(view_id="V123", view={})["method"])
                elif method_name == "channels_archive":
                    self.api_methods_to_call.remove(method(channel="C123")["method"])
                elif method_name == "channels_create":
                    self.api_methods_to_call.remove(method(name="channel-name")["method"])
                elif method_name == "channels_history":
                    self.api_methods_to_call.remove(method(channel="C123")["method"])
                elif method_name == "channels_info":
                    self.api_methods_to_call.remove(method(channel="C123")["method"])
                elif method_name == "channels_invite":
                    self.api_methods_to_call.remove(method(channel="C123", user="U123")["method"])
                elif method_name == "channels_join":
                    self.api_methods_to_call.remove(method(name="channel-name")["method"])
                elif method_name == "channels_kick":
                    self.api_methods_to_call.remove(method(channel="C123", user="U123")["method"])
                elif method_name == "channels_leave":
                    self.api_methods_to_call.remove(method(channel="C123")["method"])
                elif method_name == "channels_mark":
                    self.api_methods_to_call.remove(method(channel="C123", ts="123.123")["method"])
                elif method_name == "channels_rename":
                    self.api_methods_to_call.remove(method(channel="C123", name="new-name")["method"])
                elif method_name == "channels_replies":
                    self.api_methods_to_call.remove(method(channel="C123", thread_ts="123.123")["method"])
                elif method_name == "channels_setPurpose":
                    self.api_methods_to_call.remove(method(channel="C123", purpose="The purpose")["method"])
                elif method_name == "channels_setTopic":
                    self.api_methods_to_call.remove(method(channel="C123", topic="The topic")["method"])
                elif method_name == "channels_unarchive":
                    self.api_methods_to_call.remove(method(channel="C123")["method"])
                elif method_name == "groups_archive":
                    self.api_methods_to_call.remove(method(channel="G123")["method"])
                elif method_name == "groups_create":
                    self.api_methods_to_call.remove(method(name="private-channel-name")["method"])
                elif method_name == "groups_createChild":
                    self.api_methods_to_call.remove(method(channel="G123")["method"])
                elif method_name == "groups_history":
                    self.api_methods_to_call.remove(method(channel="G123")["method"])
                elif method_name == "groups_info":
                    self.api_methods_to_call.remove(method(channel="G123")["method"])
                elif method_name == "groups_invite":
                    self.api_methods_to_call.remove(method(channel="G123", user="U123")["method"])
                elif method_name == "groups_kick":
                    self.api_methods_to_call.remove(method(channel="G123", user="U123")["method"])
                elif method_name == "groups_leave":
                    self.api_methods_to_call.remove(method(channel="G123")["method"])
                elif method_name == "groups_mark":
                    self.api_methods_to_call.remove(method(channel="C123", ts="123.123")["method"])
                elif method_name == "groups_open":
                    self.api_methods_to_call.remove(method(channel="G123")["method"])
                elif method_name == "groups_rename":
                    self.api_methods_to_call.remove(method(channel="G123", name="new-name")["method"])
                elif method_name == "groups_replies":
                    self.api_methods_to_call.remove(method(channel="G123", thread_ts="123.123")["method"])
                elif method_name == "groups_setPurpose":
                    self.api_methods_to_call.remove(method(channel="G123", purpose="The purpose")["method"])
                elif method_name == "groups_setTopic":
                    self.api_methods_to_call.remove(method(channel="G123", topic="The topic")["method"])
                elif method_name == "groups_unarchive":
                    self.api_methods_to_call.remove(method(channel="G123")["method"])
                elif method_name == "im_close":
                    self.api_methods_to_call.remove(method(channel="D123")["method"])
                elif method_name == "im_history":
                    self.api_methods_to_call.remove(method(channel="D123")["method"])
                elif method_name == "im_mark":
                    self.api_methods_to_call.remove(method(channel="D123", ts="123.123")["method"])
                elif method_name == "im_open":
                    self.api_methods_to_call.remove(method(user="U123")["method"])
                elif method_name == "im_replies":
                    self.api_methods_to_call.remove(method(channel="D123", thread_ts="123.123")["method"])
                elif method_name == "mpim_close":
                    self.api_methods_to_call.remove(method(channel="D123")["method"])
                elif method_name == "mpim_history":
                    self.api_methods_to_call.remove(method(channel="D123")["method"])
                elif method_name == "mpim_mark":
                    self.api_methods_to_call.remove(method(channel="D123", ts="123.123")["method"])
                elif method_name == "mpim_open":
                    self.api_methods_to_call.remove(method(users=["U123", "U234"])["method"])
                    method(users="U123,U234")
                elif method_name == "mpim_replies":
                    self.api_methods_to_call.remove(method(channel="D123", thread_ts="123.123")["method"])
                else:
                    self.api_methods_to_call.remove(method(*{})["method"])
            else:
                # Verify if the expected method is supported
                self.assertTrue(callable(method), f"{method_name} is not supported yet")

        self.assertEqual(
            self.api_methods_to_call, [], "All methods should be supported"
        )
