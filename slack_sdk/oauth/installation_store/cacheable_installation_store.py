from logging import Logger
from typing import Optional, Dict

from slack_sdk.oauth import InstallationStore
from slack_sdk.oauth.installation_store import Bot, Installation


class CacheableInstallationStore(InstallationStore):
    underlying: InstallationStore
    cached_bots: Dict[str, Bot]

    def __init__(self, installation_store: InstallationStore):
        """A simple memory cache wrapper for any installation stores.

        :param installation_store: the installation store to wrap
        """
        self.underlying = installation_store
        self.cached_bots = {}

    @property
    def logger(self) -> Logger:
        return self.underlying.logger

    def save(self, installation: Installation):
        return self.underlying.save(installation)

    def find_bot(
        self, *, enterprise_id: Optional[str], team_id: Optional[str]
    ) -> Optional[Bot]:
        key = f"{enterprise_id}-{team_id}"
        if key in self.cached_bots:
            return self.cached_bots[key]
        bot = self.underlying.find_bot(enterprise_id=enterprise_id, team_id=team_id)
        if bot:
            self.cached_bots[key] = bot
        return bot
