import os
import unittest

import slack_sdk.errors as e
from slack_sdk.models.blocks import DividerBlock
from slack_sdk.models.views import View
from slack_sdk.web import WebClient
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.web.legacy_client import LegacyWebClient
from tests.mock_web_api_server import cleanup_mock_web_api_server_async, setup_mock_web_api_server_async
from tests.slack_sdk.web.mock_web_api_handler import MockHandler
from tests.slack_sdk_async.helpers import async_test


class TestWebClientCoverage(unittest.TestCase):
    # 295 endpoints as of September 17, 2025
    # Can be fetched by running `var methodNames = [].slice.call(document.getElementsByClassName('apiReferenceFilterableList__listItemLink')).map(e => e.href.replace("https://api.slack.com/methods/", ""));console.log(methodNames.toString());console.log(methodNames.length);` on https://api.slack.com/methods
    all_api_methods = "admin.analytics.getFile,admin.apps.activities.list,admin.apps.approve,admin.apps.clearResolution,admin.apps.restrict,admin.apps.uninstall,admin.apps.approved.list,admin.apps.config.lookup,admin.apps.config.set,admin.apps.requests.cancel,admin.apps.requests.list,admin.apps.restricted.list,admin.audit.anomaly.allow.getItem,admin.audit.anomaly.allow.updateItem,admin.auth.policy.assignEntities,admin.auth.policy.getEntities,admin.auth.policy.removeEntities,admin.barriers.create,admin.barriers.delete,admin.barriers.list,admin.barriers.update,admin.conversations.archive,admin.conversations.bulkArchive,admin.conversations.bulkDelete,admin.conversations.bulkMove,admin.conversations.convertToPrivate,admin.conversations.convertToPublic,admin.conversations.create,admin.conversations.createForObjects,admin.conversations.delete,admin.conversations.disconnectShared,admin.conversations.getConversationPrefs,admin.conversations.getCustomRetention,admin.conversations.getTeams,admin.conversations.invite,admin.conversations.linkObjects,admin.conversations.lookup,admin.conversations.removeCustomRetention,admin.conversations.rename,admin.conversations.search,admin.conversations.setConversationPrefs,admin.conversations.setCustomRetention,admin.conversations.setTeams,admin.conversations.unarchive,admin.conversations.unlinkObjects,admin.conversations.ekm.listOriginalConnectedChannelInfo,admin.conversations.restrictAccess.addGroup,admin.conversations.restrictAccess.listGroups,admin.conversations.restrictAccess.removeGroup,admin.emoji.add,admin.emoji.addAlias,admin.emoji.list,admin.emoji.remove,admin.emoji.rename,admin.functions.list,admin.functions.permissions.lookup,admin.functions.permissions.set,admin.inviteRequests.approve,admin.inviteRequests.deny,admin.inviteRequests.list,admin.inviteRequests.approved.list,admin.inviteRequests.denied.list,admin.roles.addAssignments,admin.roles.listAssignments,admin.roles.removeAssignments,admin.teams.admins.list,admin.teams.create,admin.teams.list,admin.teams.owners.list,admin.teams.settings.info,admin.teams.settings.setDefaultChannels,admin.teams.settings.setDescription,admin.teams.settings.setDiscoverability,admin.teams.settings.setIcon,admin.teams.settings.setName,admin.usergroups.addChannels,admin.usergroups.addTeams,admin.usergroups.listChannels,admin.usergroups.removeChannels,admin.users.assign,admin.users.invite,admin.users.list,admin.users.remove,admin.users.setAdmin,admin.users.setExpiration,admin.users.setOwner,admin.users.setRegular,admin.users.session.clearSettings,admin.users.session.getSettings,admin.users.session.invalidate,admin.users.session.list,admin.users.session.reset,admin.users.session.resetBulk,admin.users.session.setSettings,admin.users.unsupportedVersions.export,admin.workflows.collaborators.add,admin.workflows.collaborators.remove,admin.workflows.permissions.lookup,admin.workflows.search,admin.workflows.unpublish,admin.workflows.triggers.types.permissions.lookup,admin.workflows.triggers.types.permissions.set,api.test,apps.activities.list,apps.auth.external.delete,apps.auth.external.get,apps.connections.open,apps.uninstall,apps.datastore.bulkDelete,apps.datastore.bulkGet,apps.datastore.bulkPut,apps.datastore.count,apps.datastore.delete,apps.datastore.get,apps.datastore.put,apps.datastore.query,apps.datastore.update,apps.event.authorizations.list,apps.manifest.create,apps.manifest.delete,apps.manifest.export,apps.manifest.update,apps.manifest.validate,assistant.search.context,assistant.threads.setStatus,assistant.threads.setSuggestedPrompts,assistant.threads.setTitle,auth.revoke,auth.test,auth.teams.list,bookmarks.add,bookmarks.edit,bookmarks.list,bookmarks.remove,bots.info,calls.add,calls.end,calls.info,calls.update,calls.participants.add,calls.participants.remove,canvases.access.delete,canvases.access.set,canvases.create,canvases.delete,canvases.edit,canvases.sections.lookup,channels.mark,chat.appendStream,chat.delete,chat.deleteScheduledMessage,chat.getPermalink,chat.meMessage,chat.postEphemeral,chat.postMessage,chat.scheduleMessage,chat.scheduledMessages.list,chat.startStream,chat.stopStream,chat.unfurl,chat.update,conversations.acceptSharedInvite,conversations.approveSharedInvite,conversations.archive,conversations.close,conversations.create,conversations.declineSharedInvite,conversations.history,conversations.info,conversations.invite,conversations.inviteShared,conversations.join,conversations.kick,conversations.leave,conversations.list,conversations.listConnectInvites,conversations.mark,conversations.members,conversations.open,conversations.rename,conversations.replies,conversations.setPurpose,conversations.setTopic,conversations.unarchive,conversations.canvases.create,conversations.externalInvitePermissions.set,conversations.requestSharedInvite.approve,conversations.requestSharedInvite.deny,conversations.requestSharedInvite.list,dialog.open,dnd.endDnd,dnd.endSnooze,dnd.info,dnd.setSnooze,dnd.teamInfo,emoji.list,files.completeUploadExternal,files.delete,files.getUploadURLExternal,files.info,files.list,files.revokePublicURL,files.sharedPublicURL,files.upload,files.comments.delete,files.remote.add,files.remote.info,files.remote.list,files.remote.remove,files.remote.share,files.remote.update,functions.completeError,functions.completeSuccess,functions.distributions.permissions.add,functions.distributions.permissions.list,functions.distributions.permissions.remove,functions.distributions.permissions.set,functions.workflows.steps.list,functions.workflows.steps.responses.export,groups.mark,migration.exchange,oauth.access,oauth.v2.access,oauth.v2.exchange,openid.connect.token,openid.connect.userInfo,pins.add,pins.list,pins.remove,reactions.add,reactions.get,reactions.list,reactions.remove,reminders.add,reminders.complete,reminders.delete,reminders.info,reminders.list,rtm.connect,rtm.start,search.all,search.files,search.messages,stars.add,stars.list,stars.remove,team.accessLogs,team.billableInfo,team.info,team.integrationLogs,team.billing.info,team.externalTeams.disconnect,team.externalTeams.list,team.preferences.list,team.profile.get,tooling.tokens.rotate,usergroups.create,usergroups.disable,usergroups.enable,usergroups.list,usergroups.update,usergroups.users.list,usergroups.users.update,users.conversations,users.deletePhoto,users.getPresence,users.identity,users.info,users.list,users.lookupByEmail,users.setActive,users.setPhoto,users.setPresence,users.discoverableContacts.lookup,users.profile.get,users.profile.set,views.open,views.publish,views.push,views.update,workflows.featured.add,workflows.featured.list,workflows.featured.remove,workflows.featured.set,workflows.stepCompleted,workflows.stepFailed,workflows.updateStep,workflows.triggers.permissions.add,workflows.triggers.permissions.list,workflows.triggers.permissions.remove,workflows.triggers.permissions.set,im.list,im.mark,mpim.list,mpim.mark".split(
        ","
    )

    api_methods_to_call = []
    os.environ.setdefault("SLACKCLIENT_SKIP_DEPRECATION", "1")

    def setUp(self):
        setup_mock_web_api_server_async(self, MockHandler)
        self.client = WebClient(token="xoxb-coverage", base_url="http://localhost:8888")
        self.legacy_client = LegacyWebClient(token="xoxb-coverage", base_url="http://localhost:8888")
        self.async_client = AsyncWebClient(token="xoxb-coverage", base_url="http://localhost:8888")

        self.api_methods_to_call = []
        for api_method in self.all_api_methods:
            if api_method.startswith("apps.permissions.") or api_method in [
                "apps.connections.open",  # app-level token
                "oauth.access",
                "oauth.v2.access",
                "oauth.v2.exchange",
                "oauth.token",
                "openid.connect.token",
                "openid.connect.userInfo",
                "users.setActive",
                # automation platform token required ones
                "apps.activities.list",
                "apps.auth.external.delete",
                "apps.auth.external.get",
                "apps.datastore.delete",
                "apps.datastore.get",
                "apps.datastore.put",
                "apps.datastore.query",
                "apps.datastore.update",
                "apps.datastore.bulkDelete",
                "apps.datastore.bulkGet",
                "apps.datastore.bulkPut",
                "apps.datastore.count",
                "functions.workflows.steps.list",
                "functions.workflows.steps.responses.export",
                "functions.distributions.permissions.add",
                "functions.distributions.permissions.list",
                "functions.distributions.permissions.remove",
                "functions.distributions.permissions.set",
                "workflows.triggers.permissions.add",
                "workflows.triggers.permissions.list",
                "workflows.triggers.permissions.remove",
                "workflows.triggers.permissions.set",
                "admin.workflows.triggers.types.permissions.lookup",
                "admin.workflows.triggers.types.permissions.set",
                # TODO: admin.audit.anomaly.allow.* / The endpoints requires a "session" token
                "admin.audit.anomaly.allow.getItem",
                "admin.audit.anomaly.allow.updateItem",
                "assistant.search.context",  # TODO: add this method in follow up PR
                "conversations.requestSharedInvite.list",  # TODO: add this method in follow up PR
            ]:
                continue
            self.api_methods_to_call.append(api_method)

    def tearDown(self):
        cleanup_mock_web_api_server_async(self)

    async def run_method(self, method_name, method, async_method):
        # Run the api calls with required arguments
        if callable(method):
            if method_name == "admin_analytics_getFile":
                self.api_methods_to_call.remove(method(date="2020-09-01", type="member")["method"])
                await async_method(date="2020-09-01", type="member")
            elif method_name == "admin_apps_approve":
                self.api_methods_to_call.remove(method(app_id="AID123", request_id="RID123")["method"])
                await async_method(app_id="AID123", request_id="RID123")
            elif method_name == "admin_apps_restrict":
                self.api_methods_to_call.remove(method(app_id="AID123", request_id="RID123")["method"])
                await async_method(app_id="AID123", request_id="RID123")
            elif method_name == "admin_apps_uninstall":
                self.api_methods_to_call.remove(
                    method(app_id="AID123", enterprise_id="E111", team_ids=["T1", "T2"])["method"]
                )
                await async_method(app_id="AID123", enterprise_id="E111", team_ids=["T1", "T2"])
            elif method_name == "apps_manifest_create":
                self.api_methods_to_call.remove(method(manifest="{}")["method"])
                await async_method(manifest="{}")
            elif method_name == "apps_manifest_delete":
                self.api_methods_to_call.remove(method(app_id="AID123")["method"])
                await async_method(app_id="AID123")
            elif method_name == "apps_manifest_export":
                self.api_methods_to_call.remove(method(app_id="AID123")["method"])
                await async_method(app_id="AID123")
            elif method_name == "apps_manifest_update":
                self.api_methods_to_call.remove(method(app_id="AID123", manifest="{}")["method"])
                await async_method(app_id="AID123", manifest="{}")
            elif method_name == "apps_manifest_validate":
                self.api_methods_to_call.remove(method(manifest="{}")["method"])
                await async_method(manifest="{}")
            elif method_name == "admin_apps_requests_cancel":
                self.api_methods_to_call.remove(method(request_id="XXX", enterprise_id="E111", team_id="T123")["method"])
                await async_method(request_id="XXX", enterprise_id="E111", team_id="T123")
            elif method_name == "admin_apps_clearResolution":
                self.api_methods_to_call.remove(method(app_id="AID123")["method"])
                await async_method(app_id="AID123")
            elif method_name == "admin_apps_activities_list":
                self.api_methods_to_call.remove(method()["method"])
                await async_method()
            elif method_name == "admin_apps_config_lookup":
                self.api_methods_to_call.remove(method(app_ids=["A111"])["method"])
                await async_method(app_ids=["A111"])
            elif method_name == "admin_apps_config_set":
                self.api_methods_to_call.remove(method(app_id="A111")["method"])
                await async_method(app_id="A111")
            elif method_name == "admin_auth_policy_getEntities":
                self.api_methods_to_call.remove(method(policy_name="policyname")["method"])
                await async_method(policy_name="policyname")
            elif method_name == "admin_auth_policy_assignEntities":
                self.api_methods_to_call.remove(
                    method(
                        entity_ids=["1", "2"],
                        entity_type="type",
                        policy_name="policyname",
                    )["method"]
                )
                await async_method(entity_ids=["1", "2"], entity_type="type", policy_name="policyname")
            elif method_name == "admin_auth_policy_removeEntities":
                self.api_methods_to_call.remove(
                    method(
                        entity_ids=["1", "2"],
                        entity_type="type",
                        policy_name="policyname",
                    )["method"]
                )
                await async_method(entity_ids=["1", "2"], entity_type="type", policy_name="policyname")
            elif method_name == "admin_conversations_createForObjects":
                self.api_methods_to_call.remove(
                    method(
                        object_id="0019000000DmehKAAR",
                        salesforce_org_id="00DGC00000024hsuWY",
                    )["method"]
                )
                await async_method(object_id="0019000000DmehKAAR", salesforce_org_id="00DGC00000024hsuWY")
            elif method_name == "admin_conversations_linkObjects":
                self.api_methods_to_call.remove(
                    method(
                        channel="C1234567890",
                        record_id="0019000000DmehKAAR",
                        salesforce_org_id="00DGC00000024hsuWY",
                    )["method"]
                )
                await async_method(
                    channel="C1234567890", record_id="0019000000DmehKAAR", salesforce_org_id="00DGC00000024hsuWY"
                )
            elif method_name == "admin_conversations_unlinkObjects":
                self.api_methods_to_call.remove(
                    method(
                        channel="C1234567890",
                        new_name="new-channel-name",
                    )["method"]
                )
                await async_method(channel="C1234567890", new_name="new-channel-name")
            elif method_name == "admin_barriers_create":
                self.api_methods_to_call.remove(
                    method(
                        barriered_from_usergroup_ids=["AAA"],
                        primary_usergroup_id="AAA",
                        restricted_subjects=["AAA"],
                    )["method"]
                )
                await async_method(
                    barriered_from_usergroup_ids=["AAA"],
                    primary_usergroup_id="AAA",
                    restricted_subjects=["AAA"],
                )
            elif method_name == "admin_barriers_update":
                self.api_methods_to_call.remove(
                    method(
                        barrier_id="AAA",
                        barriered_from_usergroup_ids=["AAA"],
                        primary_usergroup_id="AAA",
                        restricted_subjects=["AAA"],
                    )["method"]
                )
                await async_method(
                    barrier_id="AAA",
                    barriered_from_usergroup_ids=["AAA"],
                    primary_usergroup_id="AAA",
                    restricted_subjects=["AAA"],
                )
            elif method_name == "admin_barriers_delete":
                self.api_methods_to_call.remove(method(barrier_id="AAA")["method"])
                await async_method(barrier_id="AAA")
            elif method_name == "admin_emoji_add":
                self.api_methods_to_call.remove(method(name="eyes", url="https://www.example.com/")["method"])
                await async_method(name="eyes", url="https://www.example.com/")
            elif method_name == "admin_emoji_addAlias":
                self.api_methods_to_call.remove(method(name="watching", alias_for="eyes")["method"])
                await async_method(name="watching", alias_for="eyes")
            elif method_name == "admin_emoji_remove":
                self.api_methods_to_call.remove(method(name="eyes")["method"])
                await async_method(name="eyes")
            elif method_name == "admin_emoji_rename":
                self.api_methods_to_call.remove(method(name="eyes", new_name="eyez")["method"])
                await async_method(name="eyes", new_name="eyez")
            elif method_name == "admin_functions_list":
                self.api_methods_to_call.remove(method(app_ids=["A111"])["method"])
                await async_method(app_ids=["A111"])
            elif method_name == "admin_functions_permissions_lookup":
                self.api_methods_to_call.remove(method(function_ids=["A111"])["method"])
                await async_method(function_ids=["A111"])
            elif method_name == "admin_functions_permissions_set":
                self.api_methods_to_call.remove(method(function_id="F", visibility="everyone")["method"])
                await async_method(function_id="F", visibility="everyone")
            elif method_name == "admin_inviteRequests_approve":
                self.api_methods_to_call.remove(method(invite_request_id="ID123")["method"])
                await async_method(invite_request_id="ID123")
            elif method_name == "admin_inviteRequests_deny":
                self.api_methods_to_call.remove(method(invite_request_id="ID123")["method"])
                await async_method(invite_request_id="ID123")
            elif method_name == "admin_roles_addAssignments":
                self.api_methods_to_call.remove(method(entity_ids=["X"], user_ids=["U"], role_id="R")["method"])
                await async_method(entity_ids=["X"], user_ids=["U"], role_id="R")
            elif method_name == "admin_roles_listAssignments":
                self.api_methods_to_call.remove(method()["method"])
                await async_method()
            elif method_name == "admin_roles_removeAssignments":
                self.api_methods_to_call.remove(method(entity_ids=["X"], user_ids=["U"], role_id="R")["method"])
                await async_method(entity_ids=["X"], user_ids=["U"], role_id="R")
            elif method_name == "admin_teams_admins_list":
                self.api_methods_to_call.remove(method(team_id="T123")["method"])
                await async_method(team_id="T123")
            elif method_name == "admin_teams_create":
                self.api_methods_to_call.remove(method(team_domain="awesome-team", team_name="Awesome Team")["method"])
                await async_method(team_domain="awesome-team", team_name="Awesome Team")
            elif method_name == "admin_teams_owners_list":
                self.api_methods_to_call.remove(method(team_id="T123")["method"])
                await async_method(team_id="T123")
            elif method_name == "admin_teams_settings_info":
                self.api_methods_to_call.remove(method(team_id="T123")["method"])
                await async_method(team_id="T123")
            elif method_name == "admin_teams_settings_setDefaultChannels":
                self.api_methods_to_call.remove(method(team_id="T123", channel_ids=["C123", "C234"])["method"])
                # checking tuple compatibility as sample
                method(team_id="T123", channel_ids=("C123", "C234"))
                method(team_id="T123", channel_ids="C123,C234")
                await async_method(team_id="T123", channel_ids="C123,C234")
            elif method_name == "admin_teams_settings_setDescription":
                self.api_methods_to_call.remove(
                    method(team_id="T123", description="Workspace for an awesome team")["method"]
                )
                await async_method(team_id="T123", description="Workspace for an awesome team")
            elif method_name == "admin_teams_settings_setDiscoverability":
                self.api_methods_to_call.remove(method(team_id="T123", discoverability="invite_only")["method"])
                await async_method(team_id="T123", discoverability="invite_only")
            elif method_name == "admin_teams_settings_setIcon":
                self.api_methods_to_call.remove(
                    method(
                        team_id="T123",
                        image_url="https://www.example.com/images/dummy.png",
                    )["method"]
                )
                await async_method(
                    team_id="T123",
                    image_url="https://www.example.com/images/dummy.png",
                )
            elif method_name == "admin_teams_settings_setName":
                self.api_methods_to_call.remove(method(team_id="T123", name="Awesome Engineering Team")["method"])
                await async_method(team_id="T123", name="Awesome Engineering Team")
            elif method_name == "admin_usergroups_addChannels":
                self.api_methods_to_call.remove(
                    method(
                        team_id="T123",
                        usergroup_id="S123",
                        channel_ids=["C1A2B3C4D", "C26Z25Y24"],
                    )["method"]
                )
                method(
                    team_id="T123",
                    usergroup_id="S123",
                    channel_ids="C1A2B3C4D,C26Z25Y24",
                )
                await async_method(
                    team_id="T123",
                    usergroup_id="S123",
                    channel_ids=["C1A2B3C4D", "C26Z25Y24"],
                )
            elif method_name == "admin_usergroups_addTeams":
                self.api_methods_to_call.remove(
                    method(
                        team_id="T123",
                        usergroup_id="S123",
                        team_ids=["T111", "T222"],
                    )["method"]
                )
                method(
                    team_id="T123",
                    usergroup_id="S123",
                    team_ids="T111,T222",
                )
                await async_method(
                    team_id="T123",
                    usergroup_id="S123",
                    team_ids="T111,T222",
                )
            elif method_name == "admin_usergroups_listChannels":
                self.api_methods_to_call.remove(method(usergroup_id="S123")["method"])
                method(usergroup_id="S123", include_num_members=True, team_id="T123")
                method(usergroup_id="S123", include_num_members="1", team_id="T123")
                method(usergroup_id="S123", include_num_members=1, team_id="T123")
                method(usergroup_id="S123", include_num_members=False, team_id="T123")
                method(usergroup_id="S123", include_num_members="0", team_id="T123")
                method(usergroup_id="S123", include_num_members=0, team_id="T123")
                await async_method(usergroup_id="S123", include_num_members=0, team_id="T123")
            elif method_name == "admin_usergroups_removeChannels":
                self.api_methods_to_call.remove(
                    method(
                        team_id="T123",
                        usergroup_id="S123",
                        channel_ids=["C1A2B3C4D", "C26Z25Y24"],
                    )["method"]
                )
                method(
                    team_id="T123",
                    usergroup_id="S123",
                    channel_ids="C1A2B3C4D,C26Z25Y24",
                )
                await async_method(
                    team_id="T123",
                    usergroup_id="S123",
                    channel_ids="C1A2B3C4D,C26Z25Y24",
                )
            elif method_name == "admin_users_assign":
                self.api_methods_to_call.remove(method(team_id="T123", user_id="W123")["method"])
                await async_method(team_id="T123", user_id="W123")
            elif method_name == "admin_users_invite":
                self.api_methods_to_call.remove(
                    method(
                        team_id="T123",
                        email="test@example.com",
                        channel_ids=["C1A2B3C4D", "C26Z25Y24"],
                    )["method"]
                )
                method(
                    team_id="T123",
                    email="test@example.com",
                    channel_ids="C1A2B3C4D,C26Z25Y24",
                )
                await async_method(
                    team_id="T123",
                    email="test@example.com",
                    channel_ids="C1A2B3C4D,C26Z25Y24",
                )
            elif method_name == "admin_users_list":
                self.api_methods_to_call.remove(method(team_id="T123")["method"])
                await async_method(team_id="T123")
            elif method_name == "admin_users_remove":
                self.api_methods_to_call.remove(method(team_id="T123", user_id="W123")["method"])
                await async_method(team_id="T123", user_id="W123")
            elif method_name == "admin_users_setAdmin":
                self.api_methods_to_call.remove(method(team_id="T123", user_id="W123")["method"])
                await async_method(team_id="T123", user_id="W123")
            elif method_name == "admin_users_setExpiration":
                self.api_methods_to_call.remove(method(team_id="T123", user_id="W123", expiration_ts=123)["method"])
                await async_method(team_id="T123", user_id="W123", expiration_ts=123)
            elif method_name == "admin_users_setOwner":
                self.api_methods_to_call.remove(method(team_id="T123", user_id="W123")["method"])
                await async_method(team_id="T123", user_id="W123")
            elif method_name == "admin_users_setRegular":
                self.api_methods_to_call.remove(method(team_id="T123", user_id="W123")["method"])
                await async_method(team_id="T123", user_id="W123")
            elif method_name == "admin_users_session_invalidate":
                self.api_methods_to_call.remove(method(session_id="XXX", team_id="T111")["method"])
                await async_method(session_id="XXX", team_id="T111")
            elif method_name == "admin_users_session_reset":
                self.api_methods_to_call.remove(method(user_id="W123")["method"])
                await async_method(user_id="W123")
            elif method_name == "admin_users_session_resetBulk":
                self.api_methods_to_call.remove(method(user_ids=["W123"])["method"])
                method(user_ids="W123,W234")
                await async_method(user_ids=["W123"])
                await async_method(user_ids="W123,W234")
            elif method_name == "admin_users_session_getSettings":
                self.api_methods_to_call.remove(method(user_ids=["W111"])["method"])
                await async_method(user_ids=["W111"])
            elif method_name == "admin_users_session_setSettings":
                self.api_methods_to_call.remove(method(user_ids=["W111"])["method"])
                await async_method(user_ids=["W111"])
            elif method_name == "admin_users_session_clearSettings":
                self.api_methods_to_call.remove(method(user_ids=["W111"])["method"])
                await async_method(user_ids=["W111"])
            elif method_name == "admin_workflows_search":
                self.api_methods_to_call.remove(method()["method"])
                await async_method()
            elif method_name == "admin_workflows_permissions_lookup":
                self.api_methods_to_call.remove(method(workflow_ids=["W"])["method"])
                await async_method(workflow_ids=["W"])
            elif method_name == "admin_workflows_collaborators_add":
                self.api_methods_to_call.remove(method(workflow_ids=["W"], collaborator_ids=["W111"])["method"])
                await async_method(workflow_ids=["W"], collaborator_ids=["W111"])
            elif method_name == "admin_workflows_collaborators_remove":
                self.api_methods_to_call.remove(method(workflow_ids=["W"], collaborator_ids=["W111"])["method"])
                await async_method(workflow_ids=["W"], collaborator_ids=["W111"])
            elif method_name == "admin_workflows_unpublish":
                self.api_methods_to_call.remove(method(workflow_ids=["W"])["method"])
                await async_method(workflow_ids=["W"])
            elif method_name == "apps_event_authorizations_list":
                self.api_methods_to_call.remove(method(event_context="xxx")["method"])
                await async_method(event_context="xxx")
            elif method_name == "apps_uninstall":
                self.api_methods_to_call.remove(method(client_id="111.222", client_secret="xxx")["method"])
                await async_method(client_id="111.222", client_secret="xxx")
            elif method_name == "assistant_threads_setStatus":
                self.api_methods_to_call.remove(
                    method(channel_id="D111", thread_ts="111.222", status="is typing...")["method"]
                )
                method(
                    channel_id="D111",
                    thread_ts="111.222",
                    status="is typing...",
                    loading_states=["Thinking...", "Writing..."],
                )
                await async_method(channel_id="D111", thread_ts="111.222", status="is typing...")
                await async_method(
                    channel_id="D111",
                    thread_ts="111.222",
                    status="is typing...",
                    loading_states=["Thinking...", "Writing..."],
                )
            elif method_name == "assistant_threads_setTitle":
                self.api_methods_to_call.remove(method(channel_id="D111", thread_ts="111.222", title="New chat")["method"])
                await async_method(channel_id="D111", thread_ts="111.222", title="New chat")
            elif method_name == "assistant_threads_setSuggestedPrompts":
                self.api_methods_to_call.remove(
                    method(channel_id="D111", thread_ts="111.222", prompts=[{"title": "X", "message": "Y"}])["method"]
                )
                await async_method(channel_id="D111", thread_ts="111.222", prompts=[{"title": "X", "message": "Y"}])
            elif method_name == "bookmarks_add":
                self.api_methods_to_call.remove(method(channel_id="C1234", title="bedtime story", type="article")["method"])
                await async_method(channel_id="C1234", title="bedtime story", type="article")
            elif method_name == "bookmarks_edit":
                self.api_methods_to_call.remove(method(bookmark_id="B1234", channel_id="C1234")["method"])
                await async_method(bookmark_id="B1234", channel_id="C1234")
            elif method_name == "bookmarks_list":
                self.api_methods_to_call.remove(method(channel_id="C1234")["method"])
                await async_method(channel_id="C1234")
            elif method_name == "bookmarks_remove":
                self.api_methods_to_call.remove(method(bookmark_id="B1234", channel_id="C1234")["method"])
                await async_method(bookmark_id="B1234", channel_id="C1234")
            elif method_name == "calls_add":
                self.api_methods_to_call.remove(
                    method(
                        external_unique_id="unique-id",
                        join_url="https://www.example.com",
                    )["method"]
                )
                await async_method(
                    external_unique_id="unique-id",
                    join_url="https://www.example.com",
                )
            elif method_name == "calls_end":
                self.api_methods_to_call.remove(method(id="R111")["method"])
                await async_method(id="R111")
            elif method_name == "calls_info":
                self.api_methods_to_call.remove(method(id="R111")["method"])
                await async_method(id="R111")
            elif method_name == "calls_participants_add":
                self.api_methods_to_call.remove(
                    method(
                        id="R111",
                        users=[
                            {"slack_id": "U1H77"},
                            {
                                "external_id": "54321678",
                                "display_name": "External User",
                                "avatar_url": "https://example.com/users/avatar1234.jpg",
                            },
                        ],
                    )["method"]
                )
                await async_method(
                    id="R111",
                    users=[
                        {"slack_id": "U1H77"},
                        {
                            "external_id": "54321678",
                            "display_name": "External User",
                            "avatar_url": "https://example.com/users/avatar1234.jpg",
                        },
                    ],
                )
            elif method_name == "calls_participants_remove":
                self.api_methods_to_call.remove(
                    method(
                        id="R111",
                        users=[
                            {"slack_id": "U1H77"},
                            {
                                "external_id": "54321678",
                                "display_name": "External User",
                                "avatar_url": "https://example.com/users/avatar1234.jpg",
                            },
                        ],
                    )["method"]
                )
                await async_method(
                    id="R111",
                    users=[
                        {"slack_id": "U1H77"},
                        {
                            "external_id": "54321678",
                            "display_name": "External User",
                            "avatar_url": "https://example.com/users/avatar1234.jpg",
                        },
                    ],
                )
            elif method_name == "calls_update":
                self.api_methods_to_call.remove(method(id="R111")["method"])
                await async_method(id="R111")
            elif method_name == "canvases_create":
                self.api_methods_to_call.remove(method(document_content={})["method"])
                await async_method(document_content={})
            elif method_name == "conversations_canvases_create":
                self.api_methods_to_call.remove(method(channel_id="C123", document_content={})["method"])
                await async_method(channel_id="C123", document_content={})
            elif method_name == "conversations_externalInvitePermissions_set":
                self.api_methods_to_call.remove(method(action="upgrade", channel="C123", target_team="T123")["method"])
                await async_method(action="upgrade", channel="C123", target_team="T123")
            elif method_name == "canvases_access_set":
                self.api_methods_to_call.remove(method(canvas_id="F111", access_level="write")["method"])
                await async_method(canvas_id="F111", access_level="write")
            elif method_name == "canvases_access_delete":
                self.api_methods_to_call.remove(method(canvas_id="F111")["method"])
                await async_method(canvas_id="F111")
            elif method_name == "canvases_delete":
                self.api_methods_to_call.remove(method(canvas_id="F111")["method"])
                await async_method(canvas_id="F111")
            elif method_name == "canvases_edit":
                self.api_methods_to_call.remove(method(canvas_id="F111", changes=[])["method"])
                await async_method(canvas_id="F111", changes=[])
            elif method_name == "canvases_sections_lookup":
                self.api_methods_to_call.remove(method(canvas_id="F123", criteria={})["method"])
                await async_method(canvas_id="F123", criteria={})
            elif method_name == "chat_appendStream":
                self.api_methods_to_call.remove(method(channel="C123", ts="123.123", markdown_text="**bold**")["method"])
                await async_method(channel="C123", ts="123.123", markdown_text="**bold**")
            elif method_name == "chat_delete":
                self.api_methods_to_call.remove(method(channel="C123", ts="123.123")["method"])
                await async_method(channel="C123", ts="123.123")
            elif method_name == "chat_deleteScheduledMessage":
                self.api_methods_to_call.remove(method(channel="C123", scheduled_message_id="123")["method"])
                await async_method(channel="C123", scheduled_message_id="123")
            elif method_name == "chat_getPermalink":
                self.api_methods_to_call.remove(method(channel="C123", message_ts="123.123")["method"])
                await async_method(channel="C123", message_ts="123.123")
            elif method_name == "chat_meMessage":
                self.api_methods_to_call.remove(method(channel="C123", text=":wave: Hi there!")["method"])
                await async_method(channel="C123", text=":wave: Hi there!")
            elif method_name == "chat_postEphemeral":
                self.api_methods_to_call.remove(method(channel="C123", user="U123")["method"])
                await async_method(channel="C123", user="U123")
            elif method_name == "chat_postMessage":
                self.api_methods_to_call.remove(method(channel="C123")["method"])
                await async_method(channel="C123")
            elif method_name == "chat_scheduleMessage":
                self.api_methods_to_call.remove(method(channel="C123", post_at=123, text="Hi")["method"])
                await async_method(channel="C123", post_at=123, text="Hi")
            elif method_name == "chat_scheduledMessages_list":
                self.api_methods_to_call.remove(method()["method"])
                await async_method()
            elif method_name == "chat_startStream":
                self.api_methods_to_call.remove(method(channel="C123", thread_ts="123.123")["method"])
                await async_method(channel="C123", thread_ts="123.123")
                method(channel="C123", thread_ts="123.123", recipient_team_id="T123", recipient_user_id="U123")
                await async_method(channel="C123", thread_ts="123.123", recipient_team_id="T123", recipient_user_id="U123")
            elif method_name == "chat_stopStream":
                self.api_methods_to_call.remove(
                    method(channel="C123", ts="123.123", blocks=[{"type": "markdown", "text": "**twelve**"}])["method"]
                )
                await async_method(channel="C123", ts="123.123", blocks=[{"type": "markdown", "text": "**twelve**"}])
            elif method_name == "chat_unfurl":
                self.api_methods_to_call.remove(
                    method(
                        channel="C123",
                        ts="123.123",
                        unfurls={"https://example.com/": {"text": "Every day is the test."}},
                    )["method"]
                )
                await async_method(
                    channel="C123",
                    ts="123.123",
                    unfurls={"https://example.com/": {"text": "Every day is the test."}},
                )
                method(
                    source="composer",
                    unfurl_id="Uxxxxxxx-909b5454-75f8-4ac4-b325-1b40e230bbd8",
                    unfurls={"https://example.com/": {"text": "Every day is the test."}},
                )
                await async_method(
                    source="composer",
                    unfurl_id="Uxxxxxxx-909b5454-75f8-4ac4-b325-1b40e230bbd8",
                    unfurls={"https://example.com/": {"text": "Every day is the test."}},
                )
            elif method_name == "chat_update":
                self.api_methods_to_call.remove(method(channel="C123", ts="123.123")["method"])
                await async_method(channel="C123", ts="123.123")
            elif method_name == "conversations_acceptSharedInvite":
                self.api_methods_to_call.remove(method(channel_name="test-channel-name", channel_id="C123")["method"])
                method(channel_name="test-channel-name", invite_id="123")
                # either invite_id or channel_id supplied or exception
                self.assertRaises(e.SlackRequestError, method, channel_name="test-channel-name")
                await async_method(channel_name="test-channel-name", channel_id="C123")
                await async_method(channel_name="test-channel-name", invite_id="123")
                with self.assertRaises(e.SlackRequestError):
                    await async_method(channel_name="test-channel-name")
            elif method_name == "conversations_approveSharedInvite":
                self.api_methods_to_call.remove(method(invite_id="123")["method"])
                await async_method(invite_id="123")
            elif method_name == "conversations_archive":
                self.api_methods_to_call.remove(method(channel="C123")["method"])
                await async_method(channel="C123")
            elif method_name == "conversations_close":
                self.api_methods_to_call.remove(method(channel="C123")["method"])
                await async_method(channel="C123")
            elif method_name == "conversations_open":
                self.api_methods_to_call.remove(method(channel="C123")["method"])
                await async_method(channel="C123")
            elif method_name == "conversations_create":
                self.api_methods_to_call.remove(method(name="announcements")["method"])
                await async_method(name="announcements")
            elif method_name == "conversations_declineSharedInvite":
                self.api_methods_to_call.remove(method(invite_id="123")["method"])
                await async_method(invite_id="123")
            elif method_name == "conversations_history":
                self.api_methods_to_call.remove(method(channel="C123")["method"])
                await async_method(channel="C123")
            elif method_name == "conversations_info":
                self.api_methods_to_call.remove(method(channel="C123")["method"])
                await async_method(channel="C123")
            elif method_name == "conversations_invite":
                self.api_methods_to_call.remove(method(channel="C123", users=["U2345678901", "U3456789012"])["method"])
                method(channel="C123", users="U2345678901,U3456789012")
                await async_method(channel="C123", users=["U2345678901", "U3456789012"])
            elif method_name == "conversations_inviteShared":
                self.api_methods_to_call.remove(method(channel="C123", emails="test@example.com")["method"])
                method(channel="C123", emails=["test2@example.com", "test3@example.com"])
                method(channel="C123", user_ids="U2345678901")
                method(channel="C123", user_ids=["U2345678901", "U3456789012"])
                self.assertRaises(e.SlackRequestError, method, channel="C123")
                await async_method(channel="C123", emails="test@example.com")
                with self.assertRaises(e.SlackRequestError):
                    await async_method(channel="C123")
            elif method_name == "conversations_join":
                self.api_methods_to_call.remove(method(channel="C123")["method"])
                await async_method(channel="C123")
            elif method_name == "conversations_kick":
                self.api_methods_to_call.remove(method(channel="C123", user="U123")["method"])
                await async_method(channel="C123", user="U123")
            elif method_name == "conversations_listConnectInvites":
                self.api_methods_to_call.remove(method()["method"])
                await async_method()
            elif method_name == "conversations_leave":
                self.api_methods_to_call.remove(method(channel="C123")["method"])
                await async_method(channel="C123")
            elif method_name == "conversations_mark":
                self.api_methods_to_call.remove(method(channel="C123", ts="123.123")["method"])
                await async_method(channel="C123", ts="123.123")
            elif method_name == "conversations_members":
                self.api_methods_to_call.remove(method(channel="C123")["method"])
                await async_method(channel="C123")
            elif method_name == "conversations_rename":
                self.api_methods_to_call.remove(method(channel="C123", name="new-name")["method"])
                await async_method(channel="C123", name="new-name")
            elif method_name == "conversations_replies":
                self.api_methods_to_call.remove(method(channel="C123", ts="123.123")["method"])
                await async_method(channel="C123", ts="123.123")
            elif method_name == "conversations_requestSharedInvite_approve":
                self.api_methods_to_call.remove(method(invite_id="I123")["method"])
                await async_method(invite_id="I123")
            elif method_name == "conversations_requestSharedInvite_deny":
                self.api_methods_to_call.remove(method(invite_id="I123")["method"])
                await async_method(invite_id="I123")
            elif method_name == "conversations_setPurpose":
                self.api_methods_to_call.remove(method(channel="C123", purpose="The purpose")["method"])
                await async_method(channel="C123", purpose="The purpose")
            elif method_name == "conversations_setTopic":
                self.api_methods_to_call.remove(method(channel="C123", topic="The topic")["method"])
                await async_method(channel="C123", topic="The topic")
            elif method_name == "conversations_unarchive":
                self.api_methods_to_call.remove(method(channel="C123")["method"])
                await async_method(channel="C123")
            elif method_name == "dialog_open":
                self.api_methods_to_call.remove(method(dialog={}, trigger_id="123")["method"])
                await async_method(dialog={}, trigger_id="123")
            elif method_name == "dnd_setSnooze":
                self.api_methods_to_call.remove(method(num_minutes=120)["method"])
                await async_method(num_minutes=120)
            elif method_name == "dnd_teamInfo":
                self.api_methods_to_call.remove(method(users=["123", "U234"])["method"])
                method(users="U123,U234")
                await async_method(users=["123", "U234"])
            elif method_name == "files_comments_delete":
                self.api_methods_to_call.remove(method(file="F123", id="FC123")["method"])
                await async_method(file="F123", id="FC123")
            elif method_name == "files_delete":
                self.api_methods_to_call.remove(method(file="F123")["method"])
                await async_method(file="F123")
            elif method_name == "files_info":
                self.api_methods_to_call.remove(method(file="F123")["method"])
                await async_method(file="F123")
            elif method_name == "files_revokePublicURL":
                self.api_methods_to_call.remove(method(file="F123")["method"])
                await async_method(file="F123")
            elif method_name == "files_sharedPublicURL":
                self.api_methods_to_call.remove(method(file="F123")["method"])
                await async_method(file="F123")
            elif method_name == "files_upload":
                self.api_methods_to_call.remove(method(content="This is the content")["method"])
                await async_method(content="This is the content")
            elif method_name == "files_remote_add":
                self.api_methods_to_call.remove(
                    method(
                        external_id="123",
                        external_url="https://www.example.com/remote-files/123",
                        title="File title",
                    )["method"]
                )
                await async_method(
                    external_id="123",
                    external_url="https://www.example.com/remote-files/123",
                    title="File title",
                )
            elif method_name == "files_remote_share":
                self.api_methods_to_call.remove(method(external_id="xxx", channels="C123,G123")["method"])
                method(external_id="xxx", channels=["C123", "G123"])
                method(external_id="xxx", channels="C123,G123")
                await async_method(external_id="xxx", channels="C123,G123")
            elif method_name == "files_getUploadURLExternal":
                self.api_methods_to_call.remove(method(filename="foo.png", length=123)["method"])
                await async_method(filename="foo.png", length=123)
            elif method_name == "files_completeUploadExternal":
                self.api_methods_to_call.remove(method(files=[{"id": "F111"}])["method"])
                await async_method(files=[{"id": "F111"}])
            elif method_name == "functions_completeSuccess":
                self.api_methods_to_call.remove(method(function_execution_id="Fn111", outputs={"num": 123})["method"])
                await async_method(function_execution_id="Fn111", outputs={"num": 123})
            elif method_name == "functions_completeError":
                self.api_methods_to_call.remove(method(function_execution_id="Fn111", error="something wrong")["method"])
                await async_method(function_execution_id="Fn111", error="something wrong")
            elif method_name == "migration_exchange":
                self.api_methods_to_call.remove(method(users="U123,U234")["method"])
                method(users="U123,U234")
                await async_method(users="U123,U234")
            elif method_name == "mpim_open":
                self.api_methods_to_call.remove(method(users="U123,U234")["method"])
                method(users="U123,U234")
                await async_method(users="U123,U234")
            elif method_name == "pins_add":
                self.api_methods_to_call.remove(method(channel="C123")["method"])
                await async_method(channel="C123")
            elif method_name == "pins_list":
                self.api_methods_to_call.remove(method(channel="C123")["method"])
                await async_method(channel="C123")
            elif method_name == "pins_remove":
                self.api_methods_to_call.remove(method(channel="C123")["method"])
                await async_method(channel="C123")
            elif method_name == "reactions_add":
                self.api_methods_to_call.remove(method(name="eyes", channel="C111", timestamp="111.222")["method"])
                await async_method(name="eyes", channel="C111", timestamp="111.222")
            elif method_name == "reactions_remove":
                self.api_methods_to_call.remove(method(name="eyes")["method"])
                await async_method(name="eyes")
            elif method_name == "reminders_add":
                self.api_methods_to_call.remove(method(text="The task", time=123)["method"])
                await async_method(text="The task", time=123)
            elif method_name == "reminders_complete":
                self.api_methods_to_call.remove(method(reminder="R123")["method"])
                await async_method(reminder="R123")
            elif method_name == "reminders_delete":
                self.api_methods_to_call.remove(method(reminder="R123")["method"])
                await async_method(reminder="R123")
            elif method_name == "reminders_info":
                self.api_methods_to_call.remove(method(reminder="R123")["method"])
                await async_method(reminder="R123")
            elif method_name == "search_all":
                self.api_methods_to_call.remove(method(query="Slack")["method"])
                await async_method(query="Slack")
            elif method_name == "search_files":
                self.api_methods_to_call.remove(method(query="Slack")["method"])
                await async_method(query="Slack")
            elif method_name == "search_messages":
                self.api_methods_to_call.remove(method(query="Slack")["method"])
                await async_method(query="Slack")
            elif method_name == "team_externalTeams_disconnect":
                self.api_methods_to_call.remove(method(target_team="T111")["method"])
                await async_method(target_team="T111")
            elif method_name == "tooling_tokens_rotate":
                self.api_methods_to_call.remove(method(refresh_token="xoxe-refresh")["method"])
                await async_method(refresh_token="xoxe-refresh")
            elif method_name == "usergroups_create":
                self.api_methods_to_call.remove(method(name="Engineering Team")["method"])
                await async_method(name="Engineering Team")
            elif method_name == "usergroups_disable":
                self.api_methods_to_call.remove(method(usergroup="UG123")["method"])
                await async_method(usergroup="UG123")
            elif method_name == "usergroups_enable":
                self.api_methods_to_call.remove(method(usergroup="UG123")["method"])
                await async_method(usergroup="UG123")
            elif method_name == "usergroups_update":
                self.api_methods_to_call.remove(method(usergroup="UG123")["method"])
                await async_method(usergroup="UG123")
            elif method_name == "usergroups_users_list":
                self.api_methods_to_call.remove(method(usergroup="UG123")["method"])
                await async_method(usergroup="UG123")
            elif method_name == "usergroups_users_update":
                self.api_methods_to_call.remove(method(usergroup="UG123", users=["U123", "U234"])["method"])
                method(usergroup="UG123", users="U123,U234")
                await async_method(usergroup="UG123", users="U123,U234")
            elif method_name == "users_getPresence":
                self.api_methods_to_call.remove(method(user="U123")["method"])
                await async_method(user="U123")
            elif method_name == "users_info":
                self.api_methods_to_call.remove(method(user="U123")["method"])
                await async_method(user="U123")
            elif method_name == "users_lookupByEmail":
                self.api_methods_to_call.remove(method(email="test@example.com")["method"])
                await async_method(email="test@example.com")
            elif method_name == "users_setPhoto":
                self.api_methods_to_call.remove(method(image="README.md")["method"])
                await async_method(image="README.md")
            elif method_name == "users_setPresence":
                self.api_methods_to_call.remove(method(presence="away")["method"])
                await async_method(presence="away")
            elif method_name == "views_open":
                self.api_methods_to_call.remove(method(trigger_id="123123", view={})["method"])
                method(
                    trigger_id="123123",
                    view=View(type="modal", blocks=[DividerBlock()]),
                )
                await async_method(
                    trigger_id="123123",
                    view=View(type="modal", blocks=[DividerBlock()]),
                )
            elif method_name == "views_publish":
                self.api_methods_to_call.remove(method(user_id="U123", view={})["method"])
                await async_method(user_id="U123", view={})
            elif method_name == "views_push":
                self.api_methods_to_call.remove(method(trigger_id="123123", view={})["method"])
                await async_method(trigger_id="123123", view={})
            elif method_name == "views_update":
                self.api_methods_to_call.remove(method(view_id="V123", view={})["method"])
                await async_method(view_id="V123", view={})
            elif method_name == "workflows_featured_add":
                self.api_methods_to_call.remove(method(channel_id="C123", trigger_ids=["Ft123", "Ft234"])["method"])
                method(channel_id="C123", trigger_ids="Ft123,Ft234")
                await async_method(channel_id="C123", trigger_ids=["Ft123", "Ft234"])
                await async_method(channel_id="C123", trigger_ids="Ft123,Ft234")
            elif method_name == "workflows_featured_list":
                self.api_methods_to_call.remove(method(channel_ids=["C123", "C234"])["method"])
                method(channel_ids="C123,C234")
                await async_method(channel_ids=["C123", "C234"])
                await async_method(channel_ids="C123,C234")
            elif method_name == "workflows_featured_remove":
                self.api_methods_to_call.remove(method(channel_id="C123", trigger_ids=["Ft123", "Ft234"])["method"])
                method(channel_id="C123", trigger_ids="Ft123,Ft234")
                await async_method(channel_id="C123", trigger_ids=["Ft123", "Ft234"])
                await async_method(channel_id="C123", trigger_ids="Ft123,Ft234")
            elif method_name == "workflows_featured_set":
                self.api_methods_to_call.remove(method(channel_id="C123", trigger_ids=["Ft123", "Ft234"])["method"])
                method(channel_id="C123", trigger_ids="Ft123,Ft234")
                await async_method(channel_id="C123", trigger_ids=["Ft123", "Ft234"])
                await async_method(channel_id="C123", trigger_ids="Ft123,Ft234")
            elif method_name == "workflows_stepCompleted":
                self.api_methods_to_call.remove(method(workflow_step_execute_id="S123", outputs={})["method"])
                await async_method(workflow_step_execute_id="S123", outputs={})
            elif method_name == "workflows_stepFailed":
                self.api_methods_to_call.remove(method(workflow_step_execute_id="S456", error={})["method"])
                await async_method(workflow_step_execute_id="S456", error={})
            elif method_name == "workflows_updateStep":
                self.api_methods_to_call.remove(method(workflow_step_edit_id="S789", inputs={}, outputs=[])["method"])
                await async_method(workflow_step_edit_id="S789", inputs={}, outputs=[])
            elif method_name == "channels_archive":
                self.api_methods_to_call.remove(method(channel="C123")["method"])
                await async_method(channel="C123")
            elif method_name == "channels_create":
                self.api_methods_to_call.remove(method(name="channel-name")["method"])
                await async_method(name="channel-name")
            elif method_name == "channels_history":
                self.api_methods_to_call.remove(method(channel="C123")["method"])
                await async_method(channel="C123")
            elif method_name == "channels_info":
                self.api_methods_to_call.remove(method(channel="C123")["method"])
                await async_method(channel="C123")
            elif method_name == "channels_invite":
                self.api_methods_to_call.remove(method(channel="C123", user="U123")["method"])
                await async_method(channel="C123", user="U123")
            elif method_name == "channels_join":
                self.api_methods_to_call.remove(method(name="channel-name")["method"])
                await async_method(name="channel-name")
            elif method_name == "channels_kick":
                self.api_methods_to_call.remove(method(channel="C123", user="U123")["method"])
                await async_method(channel="C123", user="U123")
            elif method_name == "channels_leave":
                self.api_methods_to_call.remove(method(channel="C123")["method"])
                await async_method(channel="C123")
            elif method_name == "channels_mark":
                self.api_methods_to_call.remove(method(channel="C123", ts="123.123")["method"])
                await async_method(channel="C123", ts="123.123")
            elif method_name == "channels_rename":
                self.api_methods_to_call.remove(method(channel="C123", name="new-name")["method"])
                await async_method(channel="C123", name="new-name")
            elif method_name == "channels_replies":
                self.api_methods_to_call.remove(method(channel="C123", thread_ts="123.123")["method"])
                await async_method(channel="C123", thread_ts="123.123")
            elif method_name == "channels_setPurpose":
                self.api_methods_to_call.remove(method(channel="C123", purpose="The purpose")["method"])
                await async_method(channel="C123", purpose="The purpose")
            elif method_name == "channels_setTopic":
                self.api_methods_to_call.remove(method(channel="C123", topic="The topic")["method"])
                await async_method(channel="C123", topic="The topic")
            elif method_name == "channels_unarchive":
                self.api_methods_to_call.remove(method(channel="C123")["method"])
                await async_method(channel="C123")
            elif method_name == "groups_archive":
                self.api_methods_to_call.remove(method(channel="G123")["method"])
                await async_method(channel="G123")
            elif method_name == "groups_create":
                self.api_methods_to_call.remove(method(name="private-channel-name")["method"])
                await async_method(name="private-channel-name")
            elif method_name == "groups_createChild":
                self.api_methods_to_call.remove(method(channel="G123")["method"])
                await async_method(channel="G123")
            elif method_name == "groups_history":
                self.api_methods_to_call.remove(method(channel="G123")["method"])
                await async_method(channel="G123")
            elif method_name == "groups_info":
                self.api_methods_to_call.remove(method(channel="G123")["method"])
                await async_method(channel="G123")
            elif method_name == "groups_invite":
                self.api_methods_to_call.remove(method(channel="G123", user="U123")["method"])
                await async_method(channel="G123", user="U123")
            elif method_name == "groups_kick":
                self.api_methods_to_call.remove(method(channel="G123", user="U123")["method"])
                await async_method(channel="G123", user="U123")
            elif method_name == "groups_leave":
                self.api_methods_to_call.remove(method(channel="G123")["method"])
                await async_method(channel="G123")
            elif method_name == "groups_mark":
                self.api_methods_to_call.remove(method(channel="C123", ts="123.123")["method"])
                await async_method(channel="C123", ts="123.123")
            elif method_name == "groups_open":
                self.api_methods_to_call.remove(method(channel="G123")["method"])
                await async_method(channel="G123")
            elif method_name == "groups_rename":
                self.api_methods_to_call.remove(method(channel="G123", name="new-name")["method"])
                await async_method(channel="G123", name="x")
            elif method_name == "groups_replies":
                self.api_methods_to_call.remove(method(channel="G123", thread_ts="123.123")["method"])
                await async_method(channel="G123", thread_ts="x")
            elif method_name == "groups_setPurpose":
                self.api_methods_to_call.remove(method(channel="G123", purpose="The purpose")["method"])
                await async_method(channel="G123", purpose="x")
            elif method_name == "groups_setTopic":
                self.api_methods_to_call.remove(method(channel="G123", topic="The topic")["method"])
                await async_method(channel="G123", topic="x")
            elif method_name == "groups_unarchive":
                self.api_methods_to_call.remove(method(channel="G123")["method"])
                await async_method(channel="G123")
            elif method_name == "im_close":
                self.api_methods_to_call.remove(method(channel="D123")["method"])
                await async_method(channel="G123")
            elif method_name == "im_history":
                self.api_methods_to_call.remove(method(channel="D123")["method"])
                await async_method(channel="D123")
            elif method_name == "im_mark":
                self.api_methods_to_call.remove(method(channel="D123", ts="123.123")["method"])
                await async_method(channel="D123", ts="x")
            elif method_name == "im_open":
                self.api_methods_to_call.remove(method(user="U123")["method"])
                await async_method(user="U123")
            elif method_name == "im_replies":
                self.api_methods_to_call.remove(method(channel="D123", thread_ts="123.123")["method"])
                await async_method(channel="D123", thread_ts="x")
            elif method_name == "mpim_close":
                self.api_methods_to_call.remove(method(channel="D123")["method"])
                await async_method(channel="D123")
            elif method_name == "mpim_history":
                self.api_methods_to_call.remove(method(channel="D123")["method"])
                await async_method(channel="D123")
            elif method_name == "mpim_mark":
                self.api_methods_to_call.remove(method(channel="D123", ts="123.123")["method"])
                await async_method(channel="D123", ts="x")
            elif method_name == "mpim_open":
                self.api_methods_to_call.remove(method(users=["U123", "U234"])["method"])
                method(users="U123,U234")
                await async_method(users=["U123", "U234"])
            elif method_name == "mpim_replies":
                self.api_methods_to_call.remove(method(channel="D123", thread_ts="123.123")["method"])
                await async_method(channel="D123", thread_ts="123.123")
            elif method_name == "admin_conversations_restrictAccess_addGroup":
                self.api_methods_to_call.remove(method(channel_id="D123", group_id="G123")["method"])
                await async_method(channel_id="D123", group_id="G123")
            elif method_name == "admin_conversations_restrictAccess_listGroups":
                self.api_methods_to_call.remove(method(channel_id="D123", group_id="G123")["method"])
                await async_method(channel_id="D123", group_id="G123")
            elif method_name == "admin_conversations_restrictAccess_removeGroup":
                self.api_methods_to_call.remove(method(channel_id="D123", group_id="G123", team_id="T13")["method"])
                await async_method(channel_id="D123", group_id="G123", team_id="T123")
            elif method_name == "admin_conversations_create":
                self.api_methods_to_call.remove(method(is_private=False, name="Foo", team_id="T123")["method"])
                await async_method(is_private=False, name="Foo", team_id="T123")
            elif method_name == "admin_conversations_delete":
                self.api_methods_to_call.remove(method(channel_id="C123")["method"])
                await async_method(channel_id="C123")
            elif method_name == "admin_conversations_invite":
                self.api_methods_to_call.remove(method(channel_id="C123", user_ids=["U123", "U456"])["method"])
                await async_method(channel_id="C123", user_ids=["U123", "U456"])
            elif method_name == "admin_conversations_archive":
                self.api_methods_to_call.remove(method(channel_id="C123")["method"])
                await async_method(channel_id="C123")
            elif method_name == "admin_conversations_unarchive":
                self.api_methods_to_call.remove(method(channel_id="C123")["method"])
                await async_method(channel_id="C123")
            elif method_name == "admin_conversations_rename":
                self.api_methods_to_call.remove(method(channel_id="C123", name="Foo")["method"])
                await async_method(channel_id="C123", name="Foo")
            elif method_name == "admin_conversations_search":
                self.api_methods_to_call.remove(method()["method"])
                await async_method()
            elif method_name == "admin_conversations_convertToPrivate":
                self.api_methods_to_call.remove(method(channel_id="C123")["method"])
                await async_method(channel_id="C123")
            elif method_name == "admin_conversations_setConversationPrefs":
                self.api_methods_to_call.remove(
                    method(
                        channel_id="C123",
                        prefs={"who_can_post": "type:admin,user:U1234,subteam:S1234"},
                    )["method"]
                )
                await async_method(
                    channel_id="C123",
                    prefs={"who_can_post": "type:admin,user:U1234,subteam:S1234"},
                )
            elif method_name == "admin_conversations_getConversationPrefs":
                self.api_methods_to_call.remove(method(channel_id="C123")["method"])
                await async_method(channel_id="C123")
            elif method_name == "admin_conversations_setTeams":
                self.api_methods_to_call.remove(method(channel_id="C123")["method"])
                await async_method(channel_id="C123")
            elif method_name == "admin_conversations_getTeams":
                self.api_methods_to_call.remove(method(channel_id="C123")["method"])
                await async_method(channel_id="C123")
            elif method_name == "admin_conversations_disconnectShared":
                self.api_methods_to_call.remove(method(channel_id="C123")["method"])
                await async_method(channel_id="C123")
            elif method_name == "admin_conversations_ekm_listOriginalConnectedChannelInfo":
                self.api_methods_to_call.remove(method()["method"])
                await async_method()
            elif method_name == "admin_conversations_getCustomRetention":
                self.api_methods_to_call.remove(method(channel_id="C123")["method"])
                await async_method(channel_id="C123")
            elif method_name == "admin_conversations_removeCustomRetention":
                self.api_methods_to_call.remove(method(channel_id="C123")["method"])
                await async_method(channel_id="C123")
            elif method_name == "admin_conversations_setCustomRetention":
                self.api_methods_to_call.remove(method(channel_id="C123", duration_days=365)["method"])
                await async_method(channel_id="C123", duration_days=365)
            elif method_name == WebClient.admin_conversations_bulkArchive.__name__:
                self.api_methods_to_call.remove(method(channel_ids=["C123", "C234"])["method"])
                await async_method(channel_ids=["C123", "C234"])
            elif method_name == WebClient.admin_conversations_bulkDelete.__name__:
                self.api_methods_to_call.remove(method(channel_ids=["C123", "C234"])["method"])
                await async_method(channel_ids=["C123", "C234"])
            elif method_name == WebClient.admin_conversations_bulkMove.__name__:
                self.api_methods_to_call.remove(method(channel_ids=["C123", "C234"], target_team_id="T123")["method"])
                await async_method(channel_ids=["C123", "C234"], target_team_id="T123")
            elif method_name == "admin_conversations_convertToPublic":
                self.api_methods_to_call.remove(method(channel_id="C123")["method"])
                await async_method(channel_id="C123")
            elif method_name == "admin_conversations_lookup":
                self.api_methods_to_call.remove(method(team_ids=["T111", "T222"], last_message_activity_before=10)["method"])
                await async_method(team_ids=["T111", "T222"], last_message_activity_before=10)
            elif method_name == "users_discoverableContacts_lookup":
                self.api_methods_to_call.remove(method(email="foo@example.com")["method"])
                await async_method(email="foo@example.com")
            else:
                self.api_methods_to_call.remove(method(*{})["method"])
                await async_method(*{})
        else:
            # Verify if the expected method is supported
            self.assertTrue(callable(method), f"{method_name} is not supported yet")

    @async_test
    async def test_coverage(self):
        print(self.api_methods_to_call)
        for api_method in self.all_api_methods:
            if self.api_methods_to_call.count(api_method) == 0:
                continue
            method_name = api_method.replace(".", "_")
            method = getattr(self.client, method_name, None)
            async_method = getattr(self.async_client, method_name, None)
            await self.run_method(method_name, method, async_method)

        self.assertEqual(self.api_methods_to_call, [], "All methods should be supported")

    @async_test
    async def test_legacy_coverage(self):
        for api_method in self.all_api_methods:
            if self.api_methods_to_call.count(api_method) == 0:
                continue
            method_name = api_method.replace(".", "_")
            method = getattr(self.legacy_client, method_name, None)
            async_method = getattr(self.async_client, method_name, None)
            await self.run_method(method_name, method, async_method)

        self.assertEqual(self.api_methods_to_call, [], "All methods should be supported")
