import logging
import time
from datetime import datetime
from logging import Logger
from uuid import uuid4

from ..state_store import OAuthStateStore
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, DateTime, and_
from sqlalchemy.engine import Engine


class SQLAlchemyOAuthStateStore(OAuthStateStore):
    engine: Engine
    expiration_seconds: int

    metadata = sqlalchemy.MetaData()
    oauth_states: Table = sqlalchemy.Table(
        "oauth_states",
        metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("state", String, nullable=False),
        Column("expire_at", DateTime, nullable=False),
    )

    def __init__(
        self,
        expiration_seconds: int,
        engine: Engine,
        logger: Logger = logging.getLogger(__name__),
    ):
        self.expiration_seconds = expiration_seconds
        self._logger = logger
        self.engine = engine

    @property
    def logger(self) -> Logger:
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
        return self._logger

    def issue(self) -> str:
        state: str = str(uuid4())
        now = datetime.utcfromtimestamp(time.time() + self.expiration_seconds)
        with self.engine.begin() as conn:
            conn.execute(
                self.oauth_states.insert(), {"state": state, "expire_at": now},
            )
        return state

    def consume(self, state: str) -> bool:
        try:
            with self.engine.begin() as conn:
                c = self.oauth_states.c
                query = self.oauth_states.select().where(
                    and_(c.state == state, c.expire_at > datetime.utcnow())
                )
                result = conn.execute(query)
                for row in result:
                    self.logger.debug(f"consume's query result: {row}")
                    conn.execute(self.oauth_states.delete().where(c.id == row["id"]))
                    return True
            return False
        except Exception as e:  # skipcq: PYL-W0703
            message = f"Failed to find any persistent data for state: {state} - {e}"
            self.logger.warning(message)
            return False
