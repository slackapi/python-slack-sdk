from datetime import datetime
from typing import Optional, Union, Dict, Any, Sequence


class Bot:
    app_id: Optional[str]
    enterprise_id: Optional[str]
    enterprise_name: Optional[str]
    team_id: Optional[str]
    team_name: Optional[str]
    bot_token: str
    bot_id: str
    bot_user_id: str
    bot_scopes: Sequence[str]
    is_enterprise_install: bool
    installed_at: float

    custom_values: Dict[str, Any]

    def __init__(
        self,
        *,
        app_id: Optional[str] = None,
        # org / workspace
        enterprise_id: Optional[str] = None,
        enterprise_name: Optional[str] = None,
        team_id: Optional[str] = None,
        team_name: Optional[str] = None,
        # bot
        bot_token: str,
        bot_id: str,
        bot_user_id: str,
        bot_scopes: Union[str, Sequence[str]] = "",
        is_enterprise_install: Optional[bool] = False,
        # timestamps
        installed_at: float,
        # custom values
        custom_values: Optional[Dict[str, Any]] = None
    ):
        self.app_id = app_id
        self.enterprise_id = enterprise_id
        self.enterprise_name = enterprise_name
        self.team_id = team_id
        self.team_name = team_name

        self.bot_token = bot_token
        self.bot_id = bot_id
        self.bot_user_id = bot_user_id
        if isinstance(bot_scopes, str):
            self.bot_scopes = bot_scopes.split(",") if len(bot_scopes) > 0 else []
        else:
            self.bot_scopes = bot_scopes
        self.is_enterprise_install = is_enterprise_install or False
        self.installed_at = installed_at
        self.custom_values = custom_values if custom_values is not None else {}

    def set_custom_value(self, name: str, value: Any):
        self.custom_values[name] = value

    def get_custom_value(self, name: str) -> Optional[Any]:
        return self.custom_values.get(name)

    def to_dict(self) -> Dict[str, Any]:
        standard_values = {
            "app_id": self.app_id,
            "enterprise_id": self.enterprise_id,
            "enterprise_name": self.enterprise_name,
            "team_id": self.team_id,
            "team_name": self.team_name,
            "bot_token": self.bot_token,
            "bot_id": self.bot_id,
            "bot_user_id": self.bot_user_id,
            "bot_scopes": ",".join(self.bot_scopes) if self.bot_scopes else None,
            "is_enterprise_install": self.is_enterprise_install,
            "installed_at": datetime.utcfromtimestamp(self.installed_at),
        }
        # prioritize standard_values over custom_values
        # when the same keys exist in both
        return {**self.custom_values, **standard_values}
