# -*- coding: utf-8 -*-
"""Store OAuth tokens/state in a Google Cloud Storage bucket."""

import logging
import time
from logging import Logger
from uuid import uuid4

from google.cloud.storage import Client  # type: ignore[import-untyped]

from slack_sdk.oauth.state_store.async_state_store import AsyncOAuthStateStore
from slack_sdk.oauth.state_store import OAuthStateStore


class GoogleCloudStorageOAuthStateStore(OAuthStateStore, AsyncOAuthStateStore):
    """Implements OAuthStateStore and AsyncOAuthStateStore for storing Slack bot auth data to Google Cloud Storage.

    Attributes:
        storage_client (Client): A Google Cloud Storage client to access the bucket
        bucket_name (str): Bucket to store OAuth data
        expiration_seconds (int): expiration time for the Oauth token
    """

    def __init__(
        self,
        *,
        storage_client: Client,
        bucket_name: str,
        expiration_seconds: int,
        logger: Logger = logging.getLogger(__name__),
    ):
        """Creates a new instance.

        Args:
            storage_client (Client): A Google Cloud Storage client to access the bucket
            bucket_name (str): Bucket to store OAuth data
            expiration_seconds (int): expiration time for the Oauth token
            logger (Logger): Custom logger for logging. Defaults to a new logger for this module.
        """
        self.storage_client = storage_client
        self.bucket_name = bucket_name
        self.expiration_seconds = expiration_seconds
        self._logger = logger

    @property
    def logger(self) -> Logger:
        """Gets the internal logger if it exists, otherwise creates a new one.

        Returns:
            Logger: the logger
        """
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
        return self._logger

    async def async_issue(self, *args, **kwargs) -> str:
        """Creates and stores a new OAuth token.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            str: the token
        """
        return self.issue(*args, **kwargs)

    async def async_consume(self, state: str) -> bool:
        """Reads the token and checks if it's a valid one.

        Args:
            state (str): the token

        Returns:
            bool: True if the token is valid
        """
        return self.consume(state)

    def issue(self, *args, **kwargs) -> str:
        """Creates and stores a new OAuth token.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            str: the token
        """
        state = str(uuid4())
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(state)
        blob.upload_from_string(str(time.time()))
        self.logger.debug("Issued %s to the Google bucket", state)
        return state

    def consume(self, state: str) -> bool:
        """Reads the token and checks if it's a valid one.

        Args:
            state (str): the token

        Returns:
            bool: True if the token is valid
        """
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(state)
            body = blob.download_as_text(encoding="utf-8")

            self.logger.debug("Downloaded %s from Google bucket", state)
            created = float(body)
            expiration = created + self.expiration_seconds
            still_valid: bool = time.time() < expiration

            blob.delete()
            self.logger.debug("Deleted %s from Google bucket", state)
            return still_valid
        except Exception as exc:  # pylint: disable=broad-except
            self.logger.warning("Failed to find any persistent data for state: %s - %s", state, exc)
            return False
