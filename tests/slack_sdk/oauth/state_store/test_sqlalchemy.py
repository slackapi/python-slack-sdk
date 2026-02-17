import time
import unittest

import sqlalchemy
from sqlalchemy.engine import Engine

from slack_sdk.oauth.state_store.sqlalchemy import SQLAlchemyOAuthStateStore


class TestSQLAlchemy(unittest.TestCase):
    engine: Engine

    def setUp(self):
        self.engine = sqlalchemy.create_engine("sqlite:///:memory:")
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
        """Test that timezone-aware datetimes work with database storage"""
        # Issue a state (tests INSERT with timezone-aware datetime)
        state = self.store.issue()
        self.assertIsNotNone(state)

        # Consume it immediately (tests WHERE clause comparison with timezone-aware datetime)
        result = self.store.consume(state)
        self.assertTrue(result)

        # Second consume should fail (state already consumed)
        result = self.store.consume(state)
        self.assertFalse(result)
