from logging import Logger


class OAuthStateStore:
    @property
    def logger(self) -> Logger:
        raise NotImplementedError()

    def issue(self) -> str:
        raise NotImplementedError()

    def consume(self, state: str) -> bool:
        raise NotImplementedError()
