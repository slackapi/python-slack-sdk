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


class Details:
    name: Optional[str]
    new_value: Optional[Union[str, List[str], Dict[str, Any]]]
    previous_value: Optional[Union[str, List[str], Dict[str, Any]]]
    expires_on: Optional[int]
    mobile_only: Optional[bool]
    web_only: Optional[bool]
    type: Optional[str]
    is_workflow: Optional[bool]
    inviter: Optional[User]
    kicker: Optional[User]
    shared_to: Optional[str]
    reason: Optional[str]
    origin_team: Optional[str]
    target_team: Optional[str]
    is_internal_integration: Optional[bool]
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
    unknown_fields: Dict[str, Any]

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        new_value: Optional[Union[str, List[str], Dict[str, Any]]] = None,
        previous_value: Optional[Union[str, List[str], Dict[str, Any]]] = None,
        expires_on: Optional[int] = None,
        mobile_only: Optional[bool] = None,
        web_only: Optional[bool] = None,
        type: Optional[str] = None,
        is_workflow: Optional[bool] = None,
        inviter: Optional[User] = None,
        kicker: Optional[User] = None,
        shared_to: Optional[str] = None,
        reason: Optional[str] = None,
        origin_team: Optional[str] = None,
        target_team: Optional[str] = None,
        is_internal_integration: Optional[bool] = None,
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
        **kwargs,
    ) -> None:
        self.name = name
        self.new_value = new_value
        self.previous_value = previous_value
        self.expires_on = expires_on
        self.mobile_only = mobile_only
        self.web_only = web_only
        self.type = type
        self.is_workflow = is_workflow
        self.inviter = inviter
        self.kicker = kicker
        self.shared_to = shared_to
        self.reason = reason
        self.origin_team = origin_team
        self.target_team = target_team
        self.is_internal_integration = is_internal_integration
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


class Entity:
    type: Optional[str]
    user: Optional[User]
    workspace: Optional[Location]
    enterprise: Optional[Location]
    channel: Optional[Channel]
    file: Optional[File]
    app: Optional[App]
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
