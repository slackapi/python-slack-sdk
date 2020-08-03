import logging
import sqlite3
from logging import Logger
from sqlite3 import Connection
from typing import Optional

from slack_sdk.oauth.installation_store.async_installation_store import (
    AsyncInstallationStore,
)
from slack_sdk.oauth.installation_store.installation_store import InstallationStore
from slack_sdk.oauth.installation_store.models.bot import Bot
from slack_sdk.oauth.installation_store.models.installation import Installation


class SQLite3InstallationStore(InstallationStore, AsyncInstallationStore):
    def __init__(
        self,
        *,
        database: str,
        client_id: str,
        logger: Logger = logging.getLogger(__name__),
    ):
        self.database = database
        self.client_id = client_id
        self.init_called = False
        self._logger = logger

    @property
    def logger(self) -> Logger:
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
        return self._logger

    def init(self):
        try:
            with sqlite3.connect(database=self.database) as conn:
                cur = conn.execute("select count(1) from installations;")
                row_num = cur.fetchone()[0]
                self.logger.debug(
                    f"{row_num} installations are stored in {self.database}"
                )
        except:
            self.create_tables()
        self.init_called = True

    def connect(self) -> Connection:
        if not self.init_called:
            self.init()
        return sqlite3.connect(database=self.database)

    def create_tables(self):
        with sqlite3.connect(database=self.database) as conn:
            conn.execute(
                """
            create table installations (
                id integer primary key autoincrement,
                client_id text not null,
                app_id text not null,
                enterprise_id text not null default '',
                team_id text not null default '',
                bot_token text not null,
                bot_id text not null,
                bot_user_id text not null,
                bot_scopes text,
                installer_user_id text not null,
                installer_user_token text,
                installer_user_scopes text,
                incoming_webhook_url text,
                incoming_webhook_channel_id text,
                incoming_webhook_configuration_url text,
                installed_at datetime not null default current_timestamp
            );
            """
            )
            conn.execute(
                """
            create index installations_idx on installations (client_id, enterprise_id, team_id, installer_user_id);
            """
            )
            conn.execute(
                """
            create table bots (
                id integer primary key autoincrement,
                client_id text not null,
                app_id text not null,
                enterprise_id text not null default '',
                team_id text not null default '',
                bot_token text not null,
                bot_id text not null,
                bot_user_id text not null,
                bot_scopes text,
                installed_at datetime not null default current_timestamp
            );
            """
            )
            conn.execute(
                """
            create index bots_idx on bots (client_id, enterprise_id, team_id);
            """
            )
            self.logger.debug(f"Tables have been created (database: {self.database})")
            conn.commit()

    async def async_save(self, installation: Installation):
        return self.save(installation)

    def save(self, installation: Installation):
        with self.connect() as conn:
            conn.execute(
                """
                insert into bots (
                    client_id,
                    app_id,
                    enterprise_id,
                    team_id,
                    bot_token,
                    bot_id,
                    bot_user_id,
                    bot_scopes
                )
                values
                (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                );
                """,
                [
                    self.client_id,
                    installation.app_id,
                    installation.enterprise_id or "",
                    installation.team_id or "",
                    installation.bot_token,
                    installation.bot_id,
                    installation.bot_user_id,
                    ",".join(installation.bot_scopes),
                ],
            )
            conn.execute(
                """
                insert into installations (
                    client_id,
                    app_id,
                    enterprise_id,
                    team_id,
                    bot_token,
                    bot_id,
                    bot_user_id,
                    bot_scopes,
                    installer_user_id,
                    installer_user_token,
                    installer_user_scopes,
                    incoming_webhook_url,
                    incoming_webhook_channel_id,
                    incoming_webhook_configuration_url
                )
                values
                (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                );
                """,
                [
                    self.client_id,
                    installation.app_id,
                    installation.enterprise_id or "",
                    installation.team_id or "",
                    installation.bot_token,
                    installation.bot_id,
                    installation.bot_user_id,
                    ",".join(installation.bot_scopes),
                    installation.user_id,
                    installation.user_token,
                    ",".join(installation.user_scopes)
                    if installation.user_scopes
                    else None,
                    installation.incoming_webhook_url,
                    installation.incoming_webhook_channel_id,
                    installation.incoming_webhook_configuration_url,
                ],
            )
            self.logger.debug(
                f"New rows in bots and installations) have been created (database: {self.database})"
            )
            conn.commit()

    async def async_find_bot(
        self, *, enterprise_id: Optional[str], team_id: Optional[str],
    ) -> Optional[Bot]:
        return self.find_bot(enterprise_id=enterprise_id, team_id=team_id)

    def find_bot(
        self, *, enterprise_id: Optional[str], team_id: Optional[str],
    ) -> Optional[Bot]:
        # TODO: org-apps support
        try:
            with self.connect() as conn:
                cur = conn.execute(
                    """
                    select
                        app_id,
                        enterprise_id,
                        team_id,
                        bot_token,
                        bot_id,
                        bot_user_id,
                        bot_scopes,
                        installed_at
                    from
                        bots
                    where
                        client_id = ?
                        and
                        enterprise_id = ?
                        and
                        team_id = ?
                    order by installed_at desc
                    limit 1
                    """,
                    [self.client_id, enterprise_id or "", team_id or "",],
                )
                row = cur.fetchone()
                result = "found" if row and len(row) > 0 else "not found"
                self.logger.debug(
                    f"find_bot's query result: {result} (database: {self.database})"
                )
                if row and len(row) > 0:
                    bot = Bot(
                        app_id=row[0],
                        enterprise_id=row[1],
                        team_id=row[2],
                        bot_token=row[3],
                        bot_id=row[4],
                        bot_user_id=row[5],
                        bot_scopes=row[6],
                        installed_at=row[7],
                    )
                    return bot
                return None

        except Exception as e:
            message = f"Failed to find bot installation data for enterprise: {enterprise_id}, team: {team_id}: {e}"
            self.logger.warning(message)
            return None
