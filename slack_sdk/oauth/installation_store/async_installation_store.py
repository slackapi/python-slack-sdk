from logging import Logger
from typing import Optional

from .models.bot import Bot
from .models.installation import Installation


class AsyncInstallationStore:
    @property
    def logger(self) -> Logger:
        raise NotImplementedError()

    async def async_save(self, installation: Installation):
        raise NotImplementedError()

    async def async_find_bot(
        self, *, enterprise_id: Optional[str], team_id: Optional[str],
    ) -> Optional[Bot]:
        raise NotImplementedError()
