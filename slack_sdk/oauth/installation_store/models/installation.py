from datetime import datetime
from time import time
from typing import Optional, Union, Dict, Any, Sequence

from slack_sdk.oauth.installation_store.models.bot import Bot


class Installation:
    app_id: Optional[str]
    enterprise_id: Optional[str]
    enterprise_name: Optional[str]
    enterprise_url: Optional[str]
    team_id: Optional[str]
    team_name: Optional[str]
    bot_token: Optional[str]
    bot_id: Optional[str]
    bot_user_id: Optional[str]
    bot_scopes: Optional[Sequence[str]]
    user_id: str
    user_token: Optional[str]
    user_scopes: Optional[Sequence[str]]
    incoming_webhook_url: Optional[str]
    incoming_webhook_channel: Optional[str]
    incoming_webhook_channel_id: Optional[str]
    incoming_webhook_configuration_url: Optional[str]
    is_enterprise_install: bool
    token_type: Optional[str]
    installed_at: float

    def __init__(
        self,
        *,
        app_id: Optional[str] = None,
        # org / workspace
        enterprise_id: Optional[str] = None,
        enterprise_name: Optional[str] = None,
        enterprise_url: Optional[str] = None,
        team_id: Optional[str] = None,
        team_name: Optional[str] = None,
        # bot
        bot_token: Optional[str] = None,
        bot_id: Optional[str] = None,
        bot_user_id: Optional[str] = None,
        bot_scopes: Union[str, Sequence[str]] = "",
        # installer
        user_id: str,
        user_token: Optional[str] = None,
        user_scopes: Union[str, Sequence[str]] = "",
        # incoming webhook
        incoming_webhook_url: Optional[str] = None,
        incoming_webhook_channel: Optional[str] = None,
        incoming_webhook_channel_id: Optional[str] = None,
        incoming_webhook_configuration_url: Optional[str] = None,
        # org app
        is_enterprise_install: Optional[bool] = False,
        token_type: Optional[str] = None,
        # timestamps
        installed_at: Optional[float] = None,
    ):
        self.app_id = app_id
        self.enterprise_id = enterprise_id
        self.enterprise_name = enterprise_name
        self.enterprise_url = enterprise_url
        self.team_id = team_id
        self.team_name = team_name
        self.bot_token = bot_token
        self.bot_id = bot_id
        self.bot_user_id = bot_user_id
        if isinstance(bot_scopes, str):
            self.bot_scopes = bot_scopes.split(",") if len(bot_scopes) > 0 else []
        else:
            self.bot_scopes = bot_scopes

        self.user_id = user_id
        self.user_token = user_token
        if isinstance(user_scopes, str):
            self.user_scopes = user_scopes.split(",") if len(user_scopes) > 0 else []
        else:
            self.user_scopes = user_scopes

        self.incoming_webhook_url = incoming_webhook_url
        self.incoming_webhook_channel = incoming_webhook_channel
        self.incoming_webhook_channel_id = incoming_webhook_channel_id
        self.incoming_webhook_configuration_url = incoming_webhook_configuration_url

        self.is_enterprise_install = is_enterprise_install or False
        self.token_type = token_type

        self.installed_at = time() if installed_at is None else installed_at

    def to_bot(self) -> Bot:
        return Bot(
            app_id=self.app_id,
            enterprise_id=self.enterprise_id,
            enterprise_name=self.enterprise_name,
            team_id=self.team_id,
            team_name=self.team_name,
            bot_token=self.bot_token,
            bot_id=self.bot_id,
            bot_user_id=self.bot_user_id,
            bot_scopes=self.bot_scopes,
            is_enterprise_install=self.is_enterprise_install,
            installed_at=self.installed_at,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "app_id": self.app_id,
            "enterprise_id": self.enterprise_id,
            "enterprise_name": self.enterprise_name,
            "enterprise_url": self.enterprise_url,
            "team_id": self.team_id,
            "team_name": self.team_name,
            "bot_token": self.bot_token,
            "bot_id": self.bot_id,
            "bot_user_id": self.bot_user_id,
            "bot_scopes": ",".join(self.bot_scopes) if self.bot_scopes else None,
            "user_id": self.user_id,
            "user_token": self.user_token,
            "user_scopes": ",".join(self.user_scopes) if self.user_scopes else None,
            "incoming_webhook_url": self.incoming_webhook_url,
            "incoming_webhook_channel": self.incoming_webhook_channel,
            "incoming_webhook_channel_id": self.incoming_webhook_channel_id,
            "incoming_webhook_configuration_url": self.incoming_webhook_configuration_url,
            "is_enterprise_install": self.is_enterprise_install,
            "token_type": self.token_type,
            "installed_at": datetime.utcfromtimestamp(self.installed_at),
        }
