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
                cur = conn.execute("select count(1) from slack_installations;")
                row_num = cur.fetchone()[0]
                self.logger.debug(
                    f"{row_num} installations are stored in {self.database}"
                )
        except Exception:  # skipcq: PYL-W0703
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
            create table slack_installations (
                id integer primary key autoincrement,
                client_id text not null,
                app_id text not null,
                enterprise_id text not null default '',
                enterprise_name text,
                enterprise_url text,
                team_id text not null default '',
                team_name text,
                bot_token text not null,
                bot_id text not null,
                bot_user_id text not null,
                bot_scopes text,
                user_id text not null,
                user_token text,
                user_scopes text,
                incoming_webhook_url text,
                incoming_webhook_channel text,
                incoming_webhook_channel_id text,
                incoming_webhook_configuration_url text,
                is_enterprise_install boolean not null default 0,
                token_type text,
                installed_at datetime not null default current_timestamp
            );
            """
            )
            conn.execute(
                """
            create index slack_installations_idx on slack_installations (
                client_id,
                enterprise_id,
                team_id,
                user_id,
                installed_at
            );
            """
            )
            conn.execute(
                """
            create table slack_bots (
                id integer primary key autoincrement,
                client_id text not null,
                app_id text not null,
                enterprise_id text not null default '',
                enterprise_name text,
                team_id text not null default '',
                team_name text,
                bot_token text not null,
                bot_id text not null,
                bot_user_id text not null,
                bot_scopes text,
                is_enterprise_install boolean not null default 0,
                installed_at datetime not null default current_timestamp
            );
            """
            )
            conn.execute(
                """
            create index slack_bots_idx on slack_bots (
                client_id,
                enterprise_id,
                team_id,
                installed_at
            );
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
                insert into slack_bots (
                    client_id,
                    app_id,
                    enterprise_id,
                    enterprise_name,
                    team_id,
                    team_name,
                    bot_token,
                    bot_id,
                    bot_user_id,
                    bot_scopes,
                    is_enterprise_install
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
                    ?
                );
                """,
                [
                    self.client_id,
                    installation.app_id,
                    installation.enterprise_id or "",
                    installation.enterprise_name,
                    installation.team_id or "",
                    installation.team_name,
                    installation.bot_token,
                    installation.bot_id,
                    installation.bot_user_id,
                    ",".join(installation.bot_scopes),
                    installation.is_enterprise_install,
                ],
            )
            conn.execute(
                """
                insert into slack_installations (
                    client_id,
                    app_id,
                    enterprise_id,
                    enterprise_name,
                    enterprise_url,
                    team_id,
                    team_name,
                    bot_token,
                    bot_id,
                    bot_user_id,
                    bot_scopes,
                    user_id,
                    user_token,
                    user_scopes,
                    incoming_webhook_url,
                    incoming_webhook_channel,
                    incoming_webhook_channel_id,
                    incoming_webhook_configuration_url,
                    is_enterprise_install,
                    token_type
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
                    installation.enterprise_name,
                    installation.enterprise_url,
                    installation.team_id or "",
                    installation.team_name,
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
                    installation.incoming_webhook_channel,
                    installation.incoming_webhook_channel_id,
                    installation.incoming_webhook_configuration_url,
                    1 if installation.is_enterprise_install else 0,
                    installation.token_type,
                ],
            )
            self.logger.debug(
                f"New rows in slack_bots and slack_installations have been created (database: {self.database})"
            )
            conn.commit()

    async def async_find_bot(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Bot]:
        return self.find_bot(
            enterprise_id=enterprise_id,
            team_id=team_id,
            is_enterprise_install=is_enterprise_install,
        )

    def find_bot(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Bot]:
        if is_enterprise_install or team_id is None:
            team_id = ""

        try:
            with self.connect() as conn:
                cur = conn.execute(
                    """
                    select
                        app_id,
                        enterprise_id,
                        enterprise_name,
                        team_id,
                        team_name,
                        bot_token,
                        bot_id,
                        bot_user_id,
                        bot_scopes,
                        is_enterprise_install,
                        installed_at
                    from
                        slack_bots
                    where
                        client_id = ?
                        and
                        enterprise_id = ?
                        and
                        team_id = ?
                    order by installed_at desc
                    limit 1
                    """,
                    [self.client_id, enterprise_id or "", team_id or ""],
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
                        enterprise_name=row[2],
                        team_id=row[3],
                        team_name=row[4],
                        bot_token=row[5],
                        bot_id=row[6],
                        bot_user_id=row[7],
                        bot_scopes=row[8],
                        is_enterprise_install=row[9],
                        installed_at=row[10],
                    )
                    return bot
                return None

        except Exception as e:  # skipcq: PYL-W0703
            message = f"Failed to find bot installation data for enterprise: {enterprise_id}, team: {team_id}: {e}"
            self.logger.warning(message)
            return None

    async def async_find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        return self.find_installation(
            enterprise_id=enterprise_id,
            team_id=team_id,
            user_id=user_id,
            is_enterprise_install=is_enterprise_install,
        )

    def find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        if is_enterprise_install or team_id is None:
            team_id = ""

        try:
            with self.connect() as conn:
                row = None
                columns = """
                    app_id,
                    enterprise_id,
                    enterprise_name,
                    enterprise_url,
                    team_id,
                    team_name,
                    bot_token,
                    bot_id,
                    bot_user_id,
                    bot_scopes,
                    user_id,
                    user_token,
                    user_scopes,
                    incoming_webhook_url,
                    incoming_webhook_channel,
                    incoming_webhook_channel_id,
                    incoming_webhook_configuration_url,
                    is_enterprise_install,
                    token_type,
                    installed_at
                """
                if user_id is None:
                    cur = conn.execute(
                        f"""
                        select
                            {columns}
                        from
                            slack_installations
                        where
                            client_id = ?
                            and
                            enterprise_id = ?
                            and
                            team_id = ?
                        order by installed_at desc
                        limit 1
                        """,
                        [self.client_id, enterprise_id or "", team_id],
                    )
                    row = cur.fetchone()
                else:
                    cur = conn.execute(
                        f"""
                        select
                            {columns}
                        from
                            slack_installations
                        where
                            client_id = ?
                            and
                            enterprise_id = ?
                            and
                            team_id = ?
                            and
                            user_id = ?
                        order by installed_at desc
                        limit 1
                        """,
                        [self.client_id, enterprise_id or "", team_id, user_id],
                    )
                    row = cur.fetchone()

                if row is None:
                    return None

                result = "found" if row and len(row) > 0 else "not found"
                self.logger.debug(
                    f"find_installation's query result: {result} (database: {self.database})"
                )
                if row and len(row) > 0:
                    installation = Installation(
                        app_id=row[0],
                        enterprise_id=row[1],
                        enterprise_name=row[2],
                        enterprise_url=row[3],
                        team_id=row[4],
                        team_name=row[5],
                        bot_token=row[6],
                        bot_id=row[7],
                        bot_user_id=row[8],
                        bot_scopes=row[9],
                        user_id=row[10],
                        user_token=row[11],
                        user_scopes=row[12],
                        incoming_webhook_url=row[13],
                        incoming_webhook_channel=row[14],
                        incoming_webhook_channel_id=row[15],
                        incoming_webhook_configuration_url=row[16],
                        is_enterprise_install=row[17],
                        token_type=row[18],
                        installed_at=row[19],
                    )
                    return installation
                return None

        except Exception as e:  # skipcq: PYL-W0703
            message = f"Failed to find an installation data for enterprise: {enterprise_id}, team: {team_id}: {e}"
            self.logger.warning(message)
            return None

    def delete_bot(
        self, *, enterprise_id: Optional[str], team_id: Optional[str]
    ) -> None:
        try:
            with self.connect() as conn:
                conn.execute(
                    """
                    delete
                    from
                        slack_bots
                    where
                        client_id = ?
                        and
                        enterprise_id = ?
                        and
                        team_id = ?
                    """,
                    [self.client_id, enterprise_id or "", team_id or ""],
                )
                conn.commit()
        except Exception as e:  # skipcq: PYL-W0703
            message = f"Failed to delete bot installation data for enterprise: {enterprise_id}, team: {team_id}: {e}"
            self.logger.warning(message)

    def delete_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
    ) -> None:
        try:
            with self.connect() as conn:
                if user_id is None:
                    conn.execute(
                        """
                        delete
                        from
                            slack_installations
                        where
                            client_id = ?
                            and
                            enterprise_id = ?
                            and
                            team_id = ?
                        """,
                        [self.client_id, enterprise_id or "", team_id],
                    )
                else:
                    conn.execute(
                        """
                        delete
                        from
                            slack_installations
                        where
                            client_id = ?
                            and
                            enterprise_id = ?
                            and
                            team_id = ?
                            and
                            user_id = ?
                        """,
                        [self.client_id, enterprise_id or "", team_id, user_id],
                    )
                conn.commit()
        except Exception as e:  # skipcq: PYL-W0703
            message = f"Failed to delete installation data for enterprise: {enterprise_id}, team: {team_id}: {e}"
            self.logger.warning(message)
