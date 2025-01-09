from typing import Optional
import psycopg2
from psycopg2.pool import SimpleConnectionPool


class PostgresConnectionPool:
    def __init__(self, connection_string: str):
        self._pool_config = {
            'dsn': connection_string,
            'minconn': 5,
            'maxconn': 10,
        }
        self._pool: Optional[SimpleConnectionPool] = None
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        self._pool = SimpleConnectionPool(**self._pool_config)

    async def open_connection(self) -> psycopg2.extensions.connection:
        if not self._pool:
            raise RuntimeError("Connection pool not initialized")

        try:
            return self._pool.getconn()
        except Exception as e:
            raise RuntimeError(f"Failed to open database connection: {e}")

    async def return_connection(self, connection) -> None:
        if not self._pool:
            raise RuntimeError("Connection pool not initialized")

        try:
            self._pool.putconn(connection)
        except Exception as e:
            raise RuntimeError(f"Failed to return connection to the pool: {e}")