# Standard Imports
import unittest

# ThirdParty Imports
import asyncio
from aiohttp import web

# Internal Imports
import slack


class TestWebClientCoverage(unittest.TestCase):
    # as of March 16, 2020
    # Can be fetched by running `var methodNames = [].slice.call(document.getElementsByClassName('bold')).map(e => e.text);console.log(methodNames.toString());console.log(methodNames.length);` on https://api.slack.com/methods
    all_api_methods = "admin.apps.approve,admin.apps.restrict,admin.apps.approved.list,admin.apps.requests.list,admin.apps.restricted.list,admin.conversations.setTeams,admin.emoji.add,admin.emoji.addAlias,admin.emoji.list,admin.emoji.remove,admin.emoji.rename,admin.inviteRequests.approve,admin.inviteRequests.deny,admin.inviteRequests.list,admin.inviteRequests.approved.list,admin.inviteRequests.denied.list,admin.teams.admins.list,admin.teams.create,admin.teams.list,admin.teams.owners.list,admin.teams.settings.info,admin.teams.settings.setDefaultChannels,admin.teams.settings.setDescription,admin.teams.settings.setDiscoverability,admin.teams.settings.setIcon,admin.teams.settings.setName,admin.users.assign,admin.users.invite,admin.users.list,admin.users.remove,admin.users.setAdmin,admin.users.setExpiration,admin.users.setOwner,admin.users.setRegular,admin.users.session.reset,api.test,apps.permissions.info,apps.permissions.request,apps.permissions.resources.list,apps.permissions.scopes.list,apps.permissions.users.list,apps.permissions.users.request,apps.uninstall,auth.revoke,auth.test,bots.info,chat.delete,chat.deleteScheduledMessage,chat.getPermalink,chat.meMessage,chat.postEphemeral,chat.postMessage,chat.scheduleMessage,chat.unfurl,chat.update,chat.scheduledMessages.list,conversations.archive,conversations.close,conversations.create,conversations.history,conversations.info,conversations.invite,conversations.join,conversations.kick,conversations.leave,conversations.list,conversations.members,conversations.open,conversations.rename,conversations.replies,conversations.setPurpose,conversations.setTopic,conversations.unarchive,dialog.open,dnd.endDnd,dnd.endSnooze,dnd.info,dnd.setSnooze,dnd.teamInfo,emoji.list,files.comments.delete,files.delete,files.info,files.list,files.revokePublicURL,files.sharedPublicURL,files.upload,files.remote.add,files.remote.info,files.remote.list,files.remote.remove,files.remote.share,files.remote.update,migration.exchange,oauth.access,oauth.token,oauth.v2.access,pins.add,pins.list,pins.remove,reactions.add,reactions.get,reactions.list,reactions.remove,reminders.add,reminders.complete,reminders.delete,reminders.info,reminders.list,rtm.connect,rtm.start,search.all,search.files,search.messages,stars.add,stars.list,stars.remove,team.accessLogs,team.billableInfo,team.info,team.integrationLogs,team.profile.get,usergroups.create,usergroups.disable,usergroups.enable,usergroups.list,usergroups.update,usergroups.users.list,usergroups.users.update,users.conversations,users.deletePhoto,users.getPresence,users.identity,users.info,users.list,users.lookupByEmail,users.setActive,users.setPhoto,users.setPresence,users.profile.get,users.profile.set,views.open,views.publish,views.push,views.update,channels.archive,channels.create,channels.history,channels.info,channels.invite,channels.join,channels.kick,channels.leave,channels.list,channels.mark,channels.rename,channels.replies,channels.setPurpose,channels.setTopic,channels.unarchive,groups.archive,groups.create,groups.createChild,groups.history,groups.info,groups.invite,groups.kick,groups.leave,groups.list,groups.mark,groups.open,groups.rename,groups.replies,groups.setPurpose,groups.setTopic,groups.unarchive,im.close,im.history,im.list,im.mark,im.open,im.replies,mpim.close,mpim.history,mpim.list,mpim.mark,mpim.open,mpim.replies".split(
        ","
    )

    api_methods_to_call = []

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        task = asyncio.ensure_future(self.mock_server(), loop=self.loop)
        self.loop.run_until_complete(asyncio.wait_for(task, 0.3))
        self.client = slack.WebClient(
            token="xoxb-abc-123", base_url="http://localhost:8765", loop=self.loop
        )
        self.no_token_client = slack.WebClient(
            base_url="http://localhost:8765", loop=self.loop
        )
        for api_method in self.all_api_methods:
            if api_method.startswith("apps.") or api_method in [
                "oauth.token",
                "users.setActive",
            ]:
                continue
            self.api_methods_to_call.append(api_method)

    def tearDown(self):
        self.loop.run_until_complete(self.site.stop())
        if not self.loop.is_closed():
            self.loop.close()

    async def mock_server(self):
        app = web.Application()
        for method_name in self.all_api_methods:
            app.router.add_get(f"/{method_name}", self.handler)
            app.router.add_post(f"/{method_name}", self.handler)
        runner = web.AppRunner(app)
        await runner.setup()
        self.site = web.TCPSite(runner, "localhost", 8765)
        await self.site.start()

    async def handler(self, request):
        content_type = request.content_type
        assert content_type in [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
        ]
        # This `api_method` is done
        self.api_methods_to_call.remove(request.path.replace("/", ""))
        return web.json_response({"ok": True})

    def test_coverage(self):
        for api_method in self.all_api_methods:
            if self.api_methods_to_call.count(api_method) == 0:
                continue
            method_name = api_method.replace(".", "_")
            method = getattr(self.client, method_name, None)

            # Run the api calls with required arguments
            if callable(method):
                if method_name == "admin_apps_approve":
                    method(app_id="AID123", request_id="RID123")
                elif method_name == "admin_inviteRequests_approve":
                    method(invite_request_id="ID123")
                elif method_name == "admin_inviteRequests_deny":
                    method(invite_request_id="ID123")
                elif method_name == "admin_teams_admins_list":
                    method(team_id="T123")
                elif method_name == "admin_teams_create":
                    method(team_domain="awesome-team", team_name="Awesome Team")
                elif method_name == "admin_teams_owners_list":
                    method(team_id="T123")
                elif method_name == "admin_teams_settings_info":
                    method(team_id="T123")
                elif method_name == "admin_teams_settings_setDefaultChannels":
                    method(team_id="T123", channel_ids=["C123", "C234"])
                elif method_name == "admin_teams_settings_setDescription":
                    method(team_id="T123", description="Workspace for an awesome team")
                elif method_name == "admin_teams_settings_setDiscoverability":
                    method(team_id="T123", discoverability="invite_only")
                elif method_name == "admin_teams_settings_setIcon":
                    method(
                        team_id="T123",
                        image_url="https://www.example.com/images/dummy.png",
                    )
                elif method_name == "admin_teams_settings_setName":
                    method(team_id="T123", name="Awesome Engineering Team")
                elif method_name == "admin_users_assign":
                    method(team_id="T123", user_id="W123")
                elif method_name == "admin_users_invite":
                    method(
                        team_id="T123",
                        email="test@example.com",
                        channel_ids=["C1A2B3C4D", "C26Z25Y24"],
                    )
                elif method_name == "admin_users_list":
                    method(team_id="T123")
                elif method_name == "admin_users_remove":
                    method(team_id="T123", user_id="W123")
                elif method_name == "admin_users_setAdmin":
                    method(team_id="T123", user_id="W123")
                elif method_name == "admin_users_setExpiration":
                    method(team_id="T123", user_id="W123", expiration_ts=123)
                elif method_name == "admin_users_setOwner":
                    method(team_id="T123", user_id="W123")
                elif method_name == "admin_users_setRegular":
                    method(team_id="T123", user_id="W123")
                elif method_name == "admin_users_session_reset":
                    method(user_id="W123")
                elif method_name == "chat_delete":
                    method(channel="C123", ts="123.123")
                elif method_name == "chat_deleteScheduledMessage":
                    method(channel="C123", scheduled_message_id="123")
                elif method_name == "chat_getPermalink":
                    method(channel="C123", message_ts="123.123")
                elif method_name == "chat_meMessage":
                    method(channel="C123", text=":wave: Hi there!")
                elif method_name == "chat_postEphemeral":
                    method(channel="C123", user="U123")
                elif method_name == "chat_postMessage":
                    method(channel="C123")
                elif method_name == "chat_scheduleMessage":
                    method(channel="C123", post_at=123, text="Hi")
                elif method_name == "chat_unfurl":
                    method(
                        channel="C123",
                        ts="123.123",
                        unfurls={
                            "https://example.com/": {"text": "Every day is the test."}
                        },
                    )
                elif method_name == "chat_update":
                    method(channel="C123", ts="123.123")
                elif method_name == "conversations_archive":
                    method(channel="C123")
                elif method_name == "conversations_close":
                    method(channel="C123")
                elif method_name == "conversations_create":
                    method(name="announcements")
                elif method_name == "conversations_history":
                    method(channel="C123")
                elif method_name == "conversations_info":
                    method(channel="C123")
                elif method_name == "conversations_invite":
                    method(channel="C123", users=["U2345678901", "U3456789012"])
                elif method_name == "conversations_join":
                    method(channel="C123")
                elif method_name == "conversations_kick":
                    method(channel="C123", user="U123")
                elif method_name == "conversations_leave":
                    method(channel="C123")
                elif method_name == "conversations_members":
                    method(channel="C123")
                elif method_name == "conversations_rename":
                    method(channel="C123", name="new-name")
                elif method_name == "conversations_replies":
                    method(channel="C123", ts="123.123")
                elif method_name == "conversations_setPurpose":
                    method(channel="C123", purpose="The purpose")
                elif method_name == "conversations_setTopic":
                    method(channel="C123", topic="The topic")
                elif method_name == "conversations_unarchive":
                    method(channel="C123")
                elif method_name == "dialog_open":
                    method(dialog={}, trigger_id="123")
                elif method_name == "dnd_setSnooze":
                    method(num_minutes=120)
                elif method_name == "files_comments_delete":
                    method(file="F123", id="FC123")
                elif method_name == "files_delete":
                    method(file="F123")
                elif method_name == "files_info":
                    method(file="F123")
                elif method_name == "files_revokePublicURL":
                    method(file="F123")
                elif method_name == "files_sharedPublicURL":
                    method(file="F123")
                elif method_name == "files_upload":
                    method(content="This is the content")
                elif method_name == "files_remote_add":
                    method(
                        external_id="123",
                        external_url="https://www.example.com/remote-files/123",
                        title="File title",
                    )
                elif method_name == "files_remote_share":
                    method(channels="C123,G123")
                elif method_name == "migration_exchange":
                    method(users="U123,U234")
                elif method_name == "oauth_access":
                    method = getattr(self.no_token_client, method_name, None)
                    method(client_id="123.123", client_secret="secret", code="123456")
                elif method_name == "oauth_v2_access":
                    method = getattr(self.no_token_client, method_name, None)
                    method(client_id="123.123", client_secret="secret", code="123456")
                elif method_name == "pins_add":
                    method(channel="C123")
                elif method_name == "pins_list":
                    method(channel="C123")
                elif method_name == "pins_remove":
                    method(channel="C123")
                elif method_name == "reactions_add":
                    method(name="eyes")
                elif method_name == "reactions_remove":
                    method(name="eyes")
                elif method_name == "reminders_add":
                    method(text="The task", time=123)
                elif method_name == "reminders_complete":
                    method(reminder="R123")
                elif method_name == "reminders_delete":
                    method(reminder="R123")
                elif method_name == "reminders_info":
                    method(reminder="R123")
                elif method_name == "search_all":
                    method(query="Slack")
                elif method_name == "search_files":
                    method(query="Slack")
                elif method_name == "search_messages":
                    method(query="Slack")
                elif method_name == "usergroups_create":
                    method(name="Engineering Team")
                elif method_name == "usergroups_disable":
                    method(usergroup="UG123")
                elif method_name == "usergroups_enable":
                    method(usergroup="UG123")
                elif method_name == "usergroups_update":
                    method(usergroup="UG123")
                elif method_name == "usergroups_users_list":
                    method(usergroup="UG123")
                elif method_name == "usergroups_users_update":
                    method(usergroup="UG123", users=["U123", "U234"])
                elif method_name == "users_getPresence":
                    method(user="U123")
                elif method_name == "users_info":
                    method(user="U123")
                elif method_name == "users_lookupByEmail":
                    method(email="test@example.com")
                elif method_name == "users_setPhoto":
                    method(image="README.md")
                elif method_name == "users_setPresence":
                    method(presence="away")
                elif method_name == "views_open":
                    method(trigger_id="123123", view={})
                elif method_name == "views_publish":
                    method(user_id="U123", view={})
                elif method_name == "views_push":
                    method(trigger_id="123123", view={})
                elif method_name == "views_update":
                    method(view_id="V123", view={})
                elif method_name == "channels_archive":
                    method(channel="C123")
                elif method_name == "channels_create":
                    method(name="channel-name")
                elif method_name == "channels_history":
                    method(channel="C123")
                elif method_name == "channels_info":
                    method(channel="C123")
                elif method_name == "channels_invite":
                    method(channel="C123", user="U123")
                elif method_name == "channels_join":
                    method(name="channel-name")
                elif method_name == "channels_kick":
                    method(channel="C123", user="U123")
                elif method_name == "channels_leave":
                    method(channel="C123")
                elif method_name == "channels_mark":
                    method(channel="C123", ts="123.123")
                elif method_name == "channels_rename":
                    method(channel="C123", name="new-name")
                elif method_name == "channels_replies":
                    method(channel="C123", thread_ts="123.123")
                elif method_name == "channels_setPurpose":
                    method(channel="C123", purpose="The purpose")
                elif method_name == "channels_setTopic":
                    method(channel="C123", topic="The topic")
                elif method_name == "channels_unarchive":
                    method(channel="C123")
                elif method_name == "groups_archive":
                    method(channel="G123")
                elif method_name == "groups_create":
                    method(name="private-channel-name")
                elif method_name == "groups_createChild":
                    method(channel="G123")
                elif method_name == "groups_history":
                    method(channel="G123")
                elif method_name == "groups_info":
                    method(channel="G123")
                elif method_name == "groups_invite":
                    method(channel="G123", user="U123")
                elif method_name == "groups_kick":
                    method(channel="G123", user="U123")
                elif method_name == "groups_leave":
                    method(channel="G123")
                elif method_name == "groups_mark":
                    method(channel="C123", ts="123.123")
                elif method_name == "groups_open":
                    method(channel="G123")
                elif method_name == "groups_rename":
                    method(channel="G123", name="new-name")
                elif method_name == "groups_replies":
                    method(channel="G123", thread_ts="123.123")
                elif method_name == "groups_setPurpose":
                    method(channel="G123", purpose="The purpose")
                elif method_name == "groups_setTopic":
                    method(channel="G123", topic="The topic")
                elif method_name == "groups_unarchive":
                    method(channel="G123")
                elif method_name == "im_close":
                    method(channel="D123")
                elif method_name == "im_history":
                    method(channel="D123")
                elif method_name == "im_mark":
                    method(channel="D123", ts="123.123")
                elif method_name == "im_open":
                    method(user="U123")
                elif method_name == "im_replies":
                    method(channel="D123", thread_ts="123.123")
                elif method_name == "mpim_close":
                    method(channel="D123")
                elif method_name == "mpim_history":
                    method(channel="D123")
                elif method_name == "mpim_mark":
                    method(channel="D123", ts="123.123")
                elif method_name == "mpim_open":
                    method(users=["U123", "U234"])
                elif method_name == "mpim_replies":
                    method(channel="D123", thread_ts="123.123")
                else:
                    method(*{})
            else:
                # Verify if the expected method is supported
                self.assertTrue(callable(method), f"{method_name} is not supported yet")

        self.assertEqual(
            self.api_methods_to_call, [], "All methods should be supported"
        )
