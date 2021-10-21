from typing import Optional, List, Union, Any, Dict


class User:
    id: Optional[str]
    name: Optional[str]
    email: Optional[str]
    team: Optional[str]
    unknown_fields: Dict[str, Any]

    def __init__(
        self,
        *,
        id: Optional[str] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        team: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.id = id
        self.name = name
        self.email = email
        self.team = team
        self.unknown_fields = kwargs


class Actor:
    type: Optional[str]
    user: Optional[User]
    unknown_fields: Dict[str, Any]

    def __init__(
        self,
        type: Optional[str] = None,
        user: Optional[User] = None,
        **kwargs,
    ) -> None:
        self.type = type
        self.user = User(**user) if isinstance(user, dict) else user
        self.unknown_fields = kwargs


class Location:
    type: Optional[str]
    id: Optional[str]
    name: Optional[str]
    domain: Optional[str]
    unknown_fields: Dict[str, Any]

    def __init__(
        self,
        *,
        type: Optional[str] = None,
        id: Optional[str] = None,
        name: Optional[str] = None,
        domain: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.type = type
        self.id = id
        self.name = name
        self.domain = domain
        self.unknown_fields = kwargs


class Context:
    location: Optional[Location]
    ua: Optional[str]
    ip_address: Optional[str]
    session_id: Optional[str]
    unknown_fields: Dict[str, Any]

    def __init__(
        self,
        *,
        location: Optional[Location] = None,
        ua: Optional[str] = None,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.location = Location(**location) if isinstance(location, dict) else location
        self.ua = ua
        self.ip_address = ip_address
        self.session_id = session_id
        self.unknown_fields = kwargs


class RetentionPolicy:
    type: Optional[str]
    duration_days: Optional[int]

    def __init__(
        self,
        *,
        type: Optional[str] = None,
        duration_days: Optional[int] = None,
        **kwargs,
    ) -> None:
        self.type = type
        self.duration_days = duration_days
        self.unknown_fields = kwargs


class ConversationPref:
    type: Optional[List[str]]
    user: Optional[List[str]]

    def __init__(
        self,
        *,
        type: Optional[List[str]] = None,
        user: Optional[List[str]] = None,
        **kwargs,
    ) -> None:
        self.type = type
        self.user = user
        self.unknown_fields = kwargs


class Details:
    name: Optional[str]
    new_value: Optional[Union[str, List[str], Dict[str, Any]]]
    previous_value: Optional[Union[str, List[str], Dict[str, Any]]]
    expires_on: Optional[int]
    mobile_only: Optional[bool]
    web_only: Optional[bool]
    non_sso_only: Optional[bool]
    type: Optional[str]
    is_workflow: Optional[bool]
    inviter: Optional[User]
    kicker: Optional[User]
    shared_to: Optional[str]
    reason: Optional[str]
    origin_team: Optional[str]
    target_team: Optional[str]
    is_internal_integration: Optional[bool]
    cleared_resolution: Optional[str]
    app_owner_id: Optional[str]
    bot_scopes: Optional[List[str]]
    new_scopes: Optional[List[str]]
    previous_scopes: Optional[List[str]]
    granular_bot_token: Optional[bool]
    scopes: Optional[List[str]]
    resolution: Optional[str]
    app_previously_resolved: Optional[bool]
    admin_app_id: Optional[str]
    bot_id: Optional[str]
    installer_user_id: Optional[str]
    approver_id: Optional[str]
    approval_type: Optional[str]
    app_previously_approved: Optional[bool]
    old_scopes: Optional[List[str]]
    channels: Optional[List[str]]
    permissions: Optional[List[Dict[str, Any]]]
    new_version_id: Optional[str]
    trigger: Optional[str]
    export_type: Optional[str]
    export_start_ts: Optional[str]
    export_end_ts: Optional[str]
    barrier_id: Optional[str]
    primary_usergroup_id: Optional[str]
    barriered_from_usergroup_ids: Optional[List[str]]
    restricted_subjects: Optional[List[str]]
    duration: Optional[int]
    desktop_app_browser_quit: Optional[bool]
    invite_id: Optional[str]
    external_organization_id: Optional[str]
    external_organization_name: Optional[str]
    external_user_id: Optional[str]
    external_user_email: Optional[str]
    channel_id: Optional[str]
    added_team_id: Optional[str]
    unknown_fields: Dict[str, Any]
    is_token_rotation_enabled_app: Optional[bool]
    old_retention_policy: Optional[RetentionPolicy]
    new_retention_policy: Optional[RetentionPolicy]
    who_can_post: Optional[ConversationPref]
    can_thread: Optional[ConversationPref]

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        new_value: Optional[Union[str, List[str], Dict[str, Any]]] = None,
        previous_value: Optional[Union[str, List[str], Dict[str, Any]]] = None,
        expires_on: Optional[int] = None,
        mobile_only: Optional[bool] = None,
        web_only: Optional[bool] = None,
        non_sso_only: Optional[bool] = None,
        type: Optional[str] = None,
        is_workflow: Optional[bool] = None,
        inviter: Optional[Union[Dict[str, Any], User]] = None,
        kicker: Optional[Union[Dict[str, Any], User]] = None,
        shared_to: Optional[str] = None,
        reason: Optional[str] = None,
        origin_team: Optional[str] = None,
        target_team: Optional[str] = None,
        is_internal_integration: Optional[bool] = None,
        cleared_resolution: Optional[str] = None,
        app_owner_id: Optional[str] = None,
        bot_scopes: Optional[List[str]] = None,
        new_scopes: Optional[List[str]] = None,
        previous_scopes: Optional[List[str]] = None,
        granular_bot_token: Optional[bool] = None,
        scopes: Optional[List[str]] = None,
        resolution: Optional[str] = None,
        app_previously_resolved: Optional[bool] = None,
        admin_app_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        installer_user_id: Optional[str] = None,
        approver_id: Optional[str] = None,
        approval_type: Optional[str] = None,
        app_previously_approved: Optional[bool] = None,
        old_scopes: Optional[List[str]] = None,
        channels: Optional[List[str]] = None,
        permissions: Optional[List[Dict[str, Any]]] = None,
        new_version_id: Optional[str] = None,
        trigger: Optional[str] = None,
        export_type: Optional[str] = None,
        export_start_ts: Optional[str] = None,
        export_end_ts: Optional[str] = None,
        barrier_id: Optional[str] = None,
        primary_usergroup_id: Optional[str] = None,
        barriered_from_usergroup_ids: Optional[List[str]] = None,
        restricted_subjects: Optional[List[str]] = None,
        duration: Optional[int] = None,
        desktop_app_browser_quit: Optional[bool] = None,
        invite_id: Optional[str] = None,
        external_organization_id: Optional[str] = None,
        external_organization_name: Optional[str] = None,
        external_user_id: Optional[str] = None,
        external_user_email: Optional[str] = None,
        channel_id: Optional[str] = None,
        added_team_id: Optional[str] = None,
        is_token_rotation_enabled_app: Optional[bool] = None,
        old_retention_policy: Optional[Union[Dict[str, Any], RetentionPolicy]] = None,
        new_retention_policy: Optional[Union[Dict[str, Any], RetentionPolicy]] = None,
        who_can_post: Optional[Union[Dict[str, List[str]], ConversationPref]] = None,
        can_thread: Optional[Union[Dict[str, List[str]], ConversationPref]] = None,
        **kwargs,
    ) -> None:
        self.name = name
        self.new_value = new_value
        self.previous_value = previous_value
        self.expires_on = expires_on
        self.mobile_only = mobile_only
        self.web_only = web_only
        self.non_sso_only = non_sso_only
        self.type = type
        self.is_workflow = is_workflow
        self.inviter = inviter if isinstance(inviter, User) else User(**inviter)
        self.kicker = kicker if isinstance(kicker, User) else User(**kicker)
        self.shared_to = shared_to
        self.reason = reason
        self.origin_team = origin_team
        self.target_team = target_team
        self.is_internal_integration = is_internal_integration
        self.cleared_resolution = cleared_resolution
        self.app_owner_id = app_owner_id
        self.bot_scopes = bot_scopes
        self.new_scopes = new_scopes
        self.previous_scopes = previous_scopes
        self.granular_bot_token = granular_bot_token
        self.scopes = scopes
        self.resolution = resolution
        self.app_previously_resolved = app_previously_resolved
        self.admin_app_id = admin_app_id
        self.bot_id = bot_id
        self.unknown_fields = kwargs
        self.installer_user_id = installer_user_id
        self.approver_id = approver_id
        self.approval_type = approval_type
        self.app_previously_approved = app_previously_approved
        self.old_scopes = old_scopes
        self.channels = channels
        self.permissions = permissions
        self.new_version_id = new_version_id
        self.trigger = trigger
        self.export_type = export_type
        self.export_start_ts = export_start_ts
        self.export_end_ts = export_end_ts
        self.barrier_id = barrier_id
        self.primary_usergroup_id = primary_usergroup_id
        self.barriered_from_usergroup_ids = barriered_from_usergroup_ids
        self.restricted_subjects = restricted_subjects
        self.duration = duration
        self.desktop_app_browser_quit = desktop_app_browser_quit
        self.invite_id = invite_id
        self.external_organization_id = external_organization_id
        self.external_organization_name = external_organization_name
        self.external_user_id = external_user_id
        self.external_user_email = external_user_email
        self.channel_id = channel_id
        self.added_team_id = added_team_id
        self.is_token_rotation_enabled_app = is_token_rotation_enabled_app
        self.old_retention_policy = (
            old_retention_policy
            if isinstance(old_retention_policy, RetentionPolicy)
            else RetentionPolicy(**old_retention_policy)
        )
        self.new_retention_policy = (
            new_retention_policy
            if isinstance(new_retention_policy, RetentionPolicy)
            else RetentionPolicy(**new_retention_policy)
        )
        self.who_can_post = (
            who_can_post
            if isinstance(who_can_post, ConversationPref)
            else ConversationPref(**who_can_post)
        )
        self.can_thread = (
            can_thread
            if isinstance(can_thread, ConversationPref)
            else ConversationPref(**can_thread)
        )


class App:
    id: Optional[str]
    name: Optional[str]
    is_distributed: Optional[bool]
    is_directory_approved: Optional[bool]
    is_workflow_app: Optional[bool]
    scopes: Optional[List[str]]
    unknown_fields: Dict[str, Any]

    def __init__(
        self,
        *,
        id: Optional[str] = None,
        name: Optional[str] = None,
        is_distributed: Optional[bool] = None,
        is_directory_approved: Optional[bool] = None,
        is_workflow_app: Optional[bool] = None,
        scopes: Optional[List[str]] = None,
        **kwargs,
    ) -> None:
        self.id = id
        self.name = name
        self.is_distributed = is_distributed
        self.is_directory_approved = is_directory_approved
        self.is_workflow_app = is_workflow_app
        self.scopes = scopes
        self.unknown_fields = kwargs


class Channel:
    id: Optional[str]
    privacy: Optional[str]
    name: Optional[str]
    is_shared: Optional[bool]
    is_org_shared: Optional[bool]
    teams_shared_with: Optional[List[str]]
    original_connected_channel_id: Optional[str]
    unknown_fields: Dict[str, Any]

    def __init__(
        self,
        *,
        id: Optional[str] = None,
        privacy: Optional[str] = None,
        name: Optional[str] = None,
        is_shared: Optional[bool] = None,
        is_org_shared: Optional[bool] = None,
        teams_shared_with: Optional[List[str]] = None,
        original_connected_channel_id: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.id = id
        self.privacy = privacy
        self.name = name
        self.is_shared = is_shared
        self.is_org_shared = is_org_shared
        self.teams_shared_with = teams_shared_with
        self.original_connected_channel_id = original_connected_channel_id
        self.unknown_fields = kwargs


class File:
    id: Optional[str]
    name: Optional[str]
    filetype: Optional[str]
    title: Optional[str]
    unknown_fields: Dict[str, Any]

    def __init__(
        self,
        *,
        id: Optional[str] = None,
        name: Optional[str] = None,
        filetype: Optional[str] = None,
        title: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.id = id
        self.name = name
        self.filetype = filetype
        self.title = title
        self.unknown_fields = kwargs


class Usergroup:
    id: Optional[str]
    name: Optional[str]
    unknown_fields: Dict[str, Any]

    def __init__(
        self,
        *,
        id: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.id = id
        self.name = name
        self.unknown_fields = kwargs


class Workflow:
    id: Optional[str]
    name: Optional[str]
    domain: Optional[str]
    unknown_fields: Dict[str, Any]

    def __init__(
        self,
        *,
        id: Optional[str] = None,
        name: Optional[str] = None,
        domain: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.id = id
        self.name = name
        self.domain = domain
        self.unknown_fields = kwargs


class InformationBarrier:
    id: Optional[str]
    primary_usergroup: Optional[str]
    barriered_from_usergroups: Optional[List[str]]
    restricted_subjects: Optional[List[str]]
    unknown_fields: Dict[str, Any]

    def __init__(
        self,
        *,
        id: Optional[str] = None,
        primary_usergroup: Optional[str] = None,
        barriered_from_usergroups: Optional[List[str]] = None,
        restricted_subjects: Optional[List[str]] = None,
        **kwargs,
    ) -> None:
        self.id = id
        self.primary_usergroup = primary_usergroup
        self.barriered_from_usergroups = barriered_from_usergroups
        self.restricted_subjects = restricted_subjects
        self.unknown_fields = kwargs


class Entity:
    type: Optional[str]
    user: Optional[User]
    workspace: Optional[Location]
    enterprise: Optional[Location]
    channel: Optional[Channel]
    file: Optional[File]
    app: Optional[App]
    usergroup: Optional[Usergroup]
    workflow: Optional[Workflow]
    barrier: Optional[InformationBarrier]
    unknown_fields: Dict[str, Any]

    def __init__(
        self,
        *,
        type: Optional[str] = None,
        user: Optional[Union[User, dict]] = None,
        workspace: Optional[Union[Location, dict]] = None,
        enterprise: Optional[Union[Location, dict]] = None,
        channel: Optional[Union[Channel, dict]] = None,
        file: Optional[Union[File, dict]] = None,
        app: Optional[Union[App, dict]] = None,
        usergroup: Optional[Usergroup] = None,
        workflow: Optional[Workflow] = None,
        barrier: Optional[InformationBarrier] = None,
        **kwargs,
    ) -> None:
        self.type = type
        self.user = User(**user) if isinstance(user, dict) else user
        self.workspace = (
            Location(**workspace) if isinstance(workspace, dict) else workspace
        )
        self.enterprise = (
            Location(**enterprise) if isinstance(enterprise, dict) else enterprise
        )
        self.channel = Channel(**channel) if isinstance(channel, dict) else channel
        self.file = File(**file) if isinstance(file, dict) else file
        self.app = App(**app) if isinstance(app, dict) else app
        self.usergroup = (
            Usergroup(**usergroup) if isinstance(usergroup, dict) else usergroup
        )
        self.workflow = Workflow(**workflow) if isinstance(workflow, dict) else workflow
        self.barrier = (
            InformationBarrier(**barrier) if isinstance(barrier, dict) else barrier
        )
        self.unknown_fields = kwargs


class Entry:
    id: Optional[str]
    date_create: Optional[int]
    action: Optional[str]
    actor: Optional[Actor]
    entity: Optional[Entity]
    context: Optional[Context]
    details: Optional[Details]
    unknown_fields: Dict[str, Any]

    def __init__(
        self,
        *,
        id: Optional[str] = None,
        date_create: Optional[int] = None,
        action: Optional[str] = None,
        actor: Optional[Actor] = None,
        entity: Optional[Entity] = None,
        context: Optional[Context] = None,
        details: Optional[Details] = None,
        **kwargs,
    ) -> None:
        self.id = id
        self.date_create = date_create
        self.action = action
        self.actor = Actor(**actor) if isinstance(actor, dict) else actor
        self.entity = Entity(**entity) if isinstance(entity, dict) else entity
        self.context = Context(**context) if isinstance(context, dict) else context
        self.details = Details(**details) if isinstance(details, dict) else details
        self.unknown_fields = kwargs


class ResponseMetadata:
    next_cursor: Optional[str]
    unknown_fields: Dict[str, Any]

    def __init__(
        self,
        *,
        next_cursor: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.next_cursor = next_cursor
        self.unknown_fields = kwargs


class LogsResponse:
    entries: Optional[List[Entry]]
    response_metadata: Optional[ResponseMetadata]
    ok: Optional[bool]
    error: Optional[str]
    needed: Optional[str]
    provided: Optional[str]
    unknown_fields: Dict[str, Any]

    def __init__(
        self,
        *,
        entries: Optional[List[Union[Entry, dict]]] = None,
        response_metadata: Optional[Union[ResponseMetadata, dict]] = None,
        ok: Optional[bool] = None,
        error: Optional[str] = None,
        needed: Optional[str] = None,
        provided: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.entries = [Entry(**e) if isinstance(e, dict) else e for e in entries]
        self.response_metadata = (
            ResponseMetadata(**response_metadata)
            if isinstance(response_metadata, dict)
            else response_metadata
        )
        self.ok = ok
        self.error = error
        self.needed = needed
        self.provided = provided
        self.unknown_fields = kwargs
