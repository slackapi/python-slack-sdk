import asyncio
import unittest

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from slack_sdk.oauth.state_store.sqlalchemy import AsyncSQLAlchemyOAuthStateStore


class TestSQLAlchemy(unittest.IsolatedAsyncioTestCase):
    engine: AsyncEngine

    async def asyncSetUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        self.store = AsyncSQLAlchemyOAuthStateStore(engine=self.engine, expiration_seconds=2)
        async with self.engine.begin() as conn:
            await conn.run_sync(self.store.metadata.create_all)

    async def asyncTearDown(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.store.metadata.drop_all)
        await self.engine.dispose()

    async def test_issue_and_consume(self):
        state = await self.store.async_issue()
        result = await self.store.async_consume(state)
        self.assertTrue(result)
        result = await self.store.async_consume(state)
        self.assertFalse(result)

    async def test_expiration(self):
        state = await self.store.async_issue()
        await asyncio.sleep(3)
        result = await self.store.async_consume(state)
        self.assertFalse(result)
