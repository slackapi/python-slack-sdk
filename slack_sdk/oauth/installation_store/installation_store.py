from abc import abstractmethod
from logging import Logger
from typing import Optional

from .models.bot import Bot
from .models.installation import Installation


class InstallationStore:
    @property
    @abstractmethod
    def logger(self) -> Logger:
        raise NotImplementedError()

    @abstractmethod
    def save(self, installation: Installation):
        raise NotImplementedError()

    @abstractmethod
    def find_bot(
        self, *, enterprise_id: Optional[str], team_id: Optional[str],
    ) -> Optional[Bot]:
        raise NotImplementedError()
