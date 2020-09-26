from datetime import datetime
from typing import Optional, Union, List, Dict, Any


class Bot:
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
        bot_scopes: Union[str, List[str]] = [],
        # timestamps
        installed_at: float,
    ):
        self.app_id = app_id
        self.enterprise_id = enterprise_id
        self.team_id = team_id

        self.bot_token = bot_token
        self.bot_id = bot_id
        self.bot_user_id = bot_user_id
        if isinstance(bot_scopes, str):
            self.bot_scopes = bot_scopes.split(",")
        else:
            self.bot_scopes = bot_scopes
        self.installed_at = installed_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "app_id": self.app_id,
            "enterprise_id": self.enterprise_id,
            "team_id": self.team_id,
            "bot_token": self.bot_token,
            "bot_id": self.bot_id,
            "bot_user_id": self.bot_user_id,
            "bot_scopes": ",".join(self.bot_scopes) if self.bot_scopes else None,
            "installed_at": datetime.utcfromtimestamp(self.installed_at),
        }
