from datetime import datetime
from time import time
from typing import Optional, List, Union, Dict, Any

from slack_sdk.oauth.installation_store.models.bot import Bot


class Installation:
    app_id: Optional[str]
    enterprise_id: Optional[str]
    team_id: Optional[str]
    bot_token: str
    bot_id: str
    bot_user_id: str
    bot_scopes: List[str]
    user_id: Optional[str]
    user_token: Optional[str]
    user_scopes: Optional[List[str]]
    incoming_webhook_url: Optional[str]
    incoming_webhook_channel_id: Optional[str]
    incoming_webhook_configuration_url: Optional[str]
    installed_at: float

    def __init__(
        self,
        *,
        app_id: Optional[str] = None,
        # org / workspace
        enterprise_id: Optional[str] = None,
        team_id: Optional[str] = None,
        # bot
        bot_token: str,
        bot_id: str,
        bot_user_id: str,
        bot_scopes: Union[str, List[str]] = "",
        # installer
        user_id: Optional[str] = None,
        user_token: Optional[str] = None,
        user_scopes: Union[str, List[str]] = "",
        # incoming webhook
        incoming_webhook_url: Optional[str] = None,
        incoming_webhook_channel_id: Optional[str] = None,
        incoming_webhook_configuration_url: Optional[str] = None,
        # timestamps
        installed_at: Optional[float] = None,
    ):
        self.app_id = app_id
        self.enterprise_id = enterprise_id
        self.team_id = team_id

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
        self.incoming_webhook_channel_id = incoming_webhook_channel_id
        self.incoming_webhook_configuration_url = incoming_webhook_configuration_url

        self.installed_at = time() if installed_at is None else installed_at

    def to_bot(self) -> Bot:
        return Bot(
            app_id=self.app_id,
            enterprise_id=self.enterprise_id,
            team_id=self.team_id,
            bot_token=self.bot_token,
            bot_id=self.bot_id,
            bot_user_id=self.bot_user_id,
            bot_scopes=self.bot_scopes,
            installed_at=self.installed_at,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "app_id": self.app_id,
            "enterprise_id": self.enterprise_id,
            "team_id": self.team_id,
            "bot_token": self.bot_token,
            "bot_id": self.bot_id,
            "bot_user_id": self.bot_user_id,
            "bot_scopes": ",".join(self.bot_scopes) if self.bot_scopes else None,
            "user_id": self.user_id,
            "user_token": self.user_token,
            "user_scopes": ",".join(self.user_scopes) if self.user_scopes else None,
            "incoming_webhook_url": self.incoming_webhook_url,
            "incoming_webhook_channel_id": self.incoming_webhook_channel_id,
            "incoming_webhook_configuration_url": self.incoming_webhook_configuration_url,
            "installed_at": datetime.utcfromtimestamp(self.installed_at),
        }
