from logging import Logger
from typing import Optional, Dict

from slack_sdk.oauth.installation_store import Bot, Installation
from slack_sdk.oauth.installation_store.async_installation_store import (
    AsyncInstallationStore,
)


class AsyncCacheableInstallationStore(AsyncInstallationStore):
    underlying: AsyncInstallationStore
    cached_bots: Dict[str, Bot]

    def __init__(self, installation_store: AsyncInstallationStore):
        """A simple memory cache wrapper for any installation stores.

        :param installation_store: the installation store to wrap
        """
        self.underlying = installation_store
        self.cached_bots = {}

    @property
    def logger(self) -> Logger:
        return self.underlying.logger

    async def async_save(self, installation: Installation):
        return await self.underlying.async_save(installation)

    async def async_find_bot(
        self, *, enterprise_id: Optional[str], team_id: Optional[str]
    ) -> Optional[Bot]:
        key = f"{enterprise_id}-{team_id}"
        if key in self.cached_bots:
            return self.cached_bots[key]
        bot = await self.underlying.async_find_bot(
            enterprise_id=enterprise_id, team_id=team_id
        )
        if bot:
            self.cached_bots[key] = bot
        return bot
