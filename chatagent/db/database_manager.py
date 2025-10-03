# chatagent/db/database_manager.py
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from pgvector.psycopg import register_vector_async
from chatagent.config.settings import settings
from fastapi import Request
import logging

# Set up logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

class DatabaseManager:
    _pool: AsyncConnectionPool = None

    @classmethod
    async def get_pool(cls, request: Request = None) -> AsyncConnectionPool:
        if cls._pool is None:
            if request:
                cls._pool = request.app.state.pool
                # logger.debug("Using existing pool from request state")
            else:
                # Log settings values to confirm
                # logger.debug(f"Settings: PSQL_HOST={settings.PSQL_HOST}, "
                #             f"PSQL_USERNAME={settings.PSQL_USERNAME}, "
                #             f"PSQL_PORT={settings.PSQL_PORT}, "
                #             f"PSQL_DATABASE={settings.PSQL_DATABASE}, "
                #             f"PSQL_SSLMODE={settings.PSQL_SSLMODE}")
                conninfo = (
                    f"postgres://{settings.PSQL_USERNAME}:{settings.PSQL_PASSWORD}"
                    f"@{settings.PSQL_HOST}:{settings.PSQL_PORT}/{settings.PSQL_DATABASE}"
                    f"?sslmode={settings.PSQL_SSLMODE}"
                )
                # logger.debug(f"Creating new pool with conninfo: {conninfo.replace(settings.PSQL_PASSWORD, '****')}")
                try:
                    cls._pool = AsyncConnectionPool(
                        conninfo=conninfo,
                        max_size=20,
                        kwargs={
                            "autocommit": True,
                            "prepare_threshold": 0,
                            "row_factory": dict_row,
                        },
                    )
                    await cls._pool.open()  # Fix deprecation warning
                    # logger.debug("Connection pool opened successfully")
                    async with cls._pool.connection() as conn:
                        await register_vector_async(conn)
                        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
                        # logger.debug("pgvector extension ensured")
                except Exception as e:
                    # logger.error(f"Failed to initialize connection pool: {e}")
                    raise
        return cls._pool