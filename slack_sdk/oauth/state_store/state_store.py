from abc import abstractmethod
from logging import Logger


class OAuthStateStore:
    @property
    @abstractmethod
    def logger(self) -> Logger:
        raise NotImplementedError()

    @abstractmethod
    def issue(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def consume(self, state: str) -> bool:
        raise NotImplementedError()
