from logging import Logger
from typing import Optional

from .models.bot import Bot
from .models.installation import Installation


class InstallationStore:
    @property
    def logger(self) -> Logger:
        raise NotImplementedError()

    def save(self, installation: Installation):
        raise NotImplementedError()

    def find_bot(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Bot]:
        raise NotImplementedError()

    def find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        raise NotImplementedError()
