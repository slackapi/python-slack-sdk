from abc import abstractmethod
from logging import Logger


class AsyncOAuthStateStore:
    @property
    @abstractmethod
    def logger(self) -> Logger:
        raise NotImplementedError()

    @abstractmethod
    async def async_issue(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    async def async_consume(self, state: str) -> bool:
        raise NotImplementedError()
