import asyncio
import os
import unittest
from tests.helpers import async_test
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from slack_sdk.oauth.state_store.sqlalchemy import AsyncSQLAlchemyOAuthStateStore

database_url = os.environ.get("ASYNC_TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")


def setUpModule():
    """Emit database configuration for CI visibility across builds."""
    print(f"\n[StateStore/AsyncSQLAlchemy] Database: {database_url}")


class TestSQLAlchemy(unittest.TestCase):
    engine: AsyncEngine

    @async_test
    async def setUp(self):
        self.engine = create_async_engine(database_url)
        self.store = AsyncSQLAlchemyOAuthStateStore(engine=self.engine, expiration_seconds=2)
        async with self.engine.begin() as conn:
            await conn.run_sync(self.store.metadata.create_all)

    @async_test
    async def tearDown(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.store.metadata.drop_all)
        await self.engine.dispose()

    @async_test
    async def test_issue_and_consume(self):
        state = await self.store.async_issue()
        result = await self.store.async_consume(state)
        self.assertTrue(result)
        result = await self.store.async_consume(state)
        self.assertFalse(result)

    @async_test
    async def test_expiration(self):
        state = await self.store.async_issue()
        await asyncio.sleep(3)
        result = await self.store.async_consume(state)
        self.assertFalse(result)

    @async_test
    async def test_timezone_aware_datetime_compatibility(self):
        # Issue a state (tests INSERT with timezone-aware datetime)
        state = await self.store.async_issue()
        self.assertIsNotNone(state)

        # Consume it immediately (tests WHERE clause comparison with timezone-aware datetime)
        result = await self.store.async_consume(state)
        self.assertTrue(result)

        # Second consume should fail (state already consumed)
        result = await self.store.async_consume(state)
        self.assertFalse(result)
