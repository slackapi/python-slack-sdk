import os
import time
import unittest

import sqlalchemy
from sqlalchemy.engine import Engine

from slack_sdk.oauth.state_store.sqlalchemy import SQLAlchemyOAuthStateStore

database_url = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")


def setUpModule():
    """Emit database configuration for CI visibility across builds."""
    print(f"\n[StateStore/SQLAlchemy] Database: {database_url}")


class TestSQLAlchemy(unittest.TestCase):
    engine: Engine

    def setUp(self):
        self.engine = sqlalchemy.create_engine(database_url)
        self.store = SQLAlchemyOAuthStateStore(engine=self.engine, expiration_seconds=2)
        self.store.metadata.create_all(self.engine)

    def tearDown(self):
        self.store.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_issue_and_consume(self):
        state = self.store.issue()
        result = self.store.consume(state)
        self.assertTrue(result)
        result = self.store.consume(state)
        self.assertFalse(result)

    def test_expiration(self):
        state = self.store.issue()
        time.sleep(3)
        result = self.store.consume(state)
        self.assertFalse(result)

    def test_timezone_aware_datetime_compatibility(self):
        # Issue a state (tests INSERT with timezone-aware datetime)
        state = self.store.issue()
        self.assertIsNotNone(state)

        # Consume it immediately (tests WHERE clause comparison with timezone-aware datetime)
        result = self.store.consume(state)
        self.assertTrue(result)

        # Second consume should fail (state already consumed)
        result = self.store.consume(state)
        self.assertFalse(result)
