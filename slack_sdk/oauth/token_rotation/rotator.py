from time import time
from typing import Optional

from slack_sdk.errors import SlackApiError, SlackTokenRotationError
from slack_sdk.web import WebClient
from slack_sdk.oauth.installation_store import Installation, Bot


class TokenRotator:
    client: WebClient
    client_id: str
    client_secret: str

    def __init__(self, *, client_id: str, client_secret: str, client: Optional[WebClient] = None):
        self.client = client if client is not None else WebClient(token=None)
        self.client_id = client_id
        self.client_secret = client_secret

    def perform_token_rotation(  # type: ignore
        self,
        *,
        installation: Installation,
        minutes_before_expiration: int = 120,  # 2 hours by default
    ) -> Optional[Installation]:
        """Performs token rotation if the underlying tokens (bot / user) are expired / expiring.

        Args:
            installation: the current installation data
            minutes_before_expiration: the minutes before the token expiration

        Returns:
            None if no rotation is necessary for now.
        """

        # TODO: make the following two calls in parallel for better performance

        # bot
        rotated_bot: Optional[Bot] = self.perform_bot_token_rotation(  # type: ignore
            bot=installation.to_bot(),
            minutes_before_expiration=minutes_before_expiration,
        )

        # user
        rotated_installation: Optional[Installation] = self.perform_user_token_rotation(  # type: ignore
            installation=installation,
            minutes_before_expiration=minutes_before_expiration,
        )

        if rotated_bot is not None:
            if rotated_installation is None:
                rotated_installation = Installation(**installation.to_dict())  # type: ignore
            rotated_installation.bot_token = rotated_bot.bot_token
            rotated_installation.bot_refresh_token = rotated_bot.bot_refresh_token
            rotated_installation.bot_token_expires_at = rotated_bot.bot_token_expires_at

        return rotated_installation

    def perform_bot_token_rotation(  # type: ignore
        self,
        *,
        bot: Bot,
        minutes_before_expiration: int = 120,  # 2 hours by default
    ) -> Optional[Bot]:
        """Performs bot token rotation if the underlying bot token is expired / expiring.

        Args:
            bot: the current bot installation data
            minutes_before_expiration: the minutes before the token expiration

        Returns:
            None if no rotation is necessary for now.
        """
        if bot.bot_token_expires_at is None:
            return None
        if bot.bot_token_expires_at > time() + minutes_before_expiration * 60:
            return None

        try:
            refresh_response = self.client.oauth_v2_access(
                client_id=self.client_id,
                client_secret=self.client_secret,
                grant_type="refresh_token",
                refresh_token=bot.bot_refresh_token,
            )
            if refresh_response.get("token_type") != "bot":
                return None

            refreshed_bot = Bot(**bot.to_dict())  # type: ignore
            refreshed_bot.bot_token = refresh_response.get("access_token")
            refreshed_bot.bot_refresh_token = refresh_response.get("refresh_token")
            refreshed_bot.bot_token_expires_at = int(time()) + int(refresh_response.get("expires_in"))
            return refreshed_bot

        except SlackApiError as e:
            raise SlackTokenRotationError(e)

    def perform_user_token_rotation(  # type: ignore
        self,
        *,
        installation: Installation,
        minutes_before_expiration: int = 120,  # 2 hours by default
    ) -> Optional[Installation]:
        """Performs user token rotation if the underlying user token is expired / expiring.

        Args:
            installation: the current installation data
            minutes_before_expiration: the minutes before the token expiration

        Returns:
            None if no rotation is necessary for now.
        """
        if installation.user_token_expires_at is None:
            return None
        if installation.user_token_expires_at > time() + minutes_before_expiration * 60:
            return None

        try:
            refresh_response = self.client.oauth_v2_access(
                client_id=self.client_id,
                client_secret=self.client_secret,
                grant_type="refresh_token",
                refresh_token=installation.user_refresh_token,
            )

            if refresh_response.get("token_type") != "user":
                return None

            refreshed_installation = Installation(**installation.to_dict())  # type: ignore
            refreshed_installation.user_token = refresh_response.get("access_token")
            refreshed_installation.user_refresh_token = refresh_response.get("refresh_token")
            refreshed_installation.user_token_expires_at = int(time()) + int(refresh_response.get("expires_in"))
            return refreshed_installation

        except SlackApiError as e:
            raise SlackTokenRotationError(e)
