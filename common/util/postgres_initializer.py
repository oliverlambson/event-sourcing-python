from typing import Any
from common.util.postgres_connection_pool import PostgresConnectionPool
from common.util.logger import log

class PostgresInitializer:
    def __init__(
        self,
        connection_pool: PostgresConnectionPool,
        event_store_database_name: str,
        event_store_table: str,
        replication_username: str,
        replication_password: str,
        replication_publication: str
    ):
        self._connection_pool = connection_pool
        self._database_name = event_store_database_name
        self._table = event_store_table
        self._replication_username = replication_username
        self._replication_password = replication_password
        self._publication = replication_publication

    async def initialize(self) -> None:
        client = await self._connection_pool.open_connection()
        try:
            await self._create_table(client)
            await self._create_replication_user(client)
            await self._grant_permissions(client)
            await self._create_publication(client)
            await self._create_indexes(client)
        finally:
            await self._connection_pool.return_connection(client)

    async def _execute_statement_ignore_errors(self, client: Any, sql_statement: str) -> None:
        try:
            log.info(f"Executing SQL: {sql_statement}")
            with client.cursor() as cursor:
                cursor.execute(sql_statement)
                client.commit()
        except Exception as error:
            log.warn("Caught exception when executing SQL statement.", error=error)

    async def _create_table(self, client: Any) -> None:
        log.info(f"Creating table {self._table}")
        sql = f"""
        CREATE TABLE IF NOT EXISTS {self._table} (
            id BIGSERIAL NOT NULL,
            event_id TEXT NOT NULL UNIQUE,
            aggregate_id TEXT NOT NULL,
            aggregate_version BIGINT NOT NULL,
            causation_id TEXT NOT NULL,
            correlation_id TEXT NOT NULL,
            recorded_on TEXT NOT NULL,
            event_name TEXT NOT NULL,
            json_payload TEXT NOT NULL,
            json_metadata TEXT NOT NULL,
            PRIMARY KEY (id)
        );
        """
        await self._execute_statement_ignore_errors(client, sql)

    async def _create_replication_user(self, client: Any) -> None:
        log.info('Creating replication user')
        sql = f"""
        CREATE USER {self._replication_username} REPLICATION LOGIN PASSWORD '{self._replication_password}';
        """
        await self._execute_statement_ignore_errors(client, sql)

    async def _grant_permissions(self, client: Any) -> None:
        log.info('Granting permissions to replication user')
        sql = f"""
        GRANT CONNECT ON DATABASE "{self._database_name}" TO {self._replication_username};
        """
        await self._execute_statement_ignore_errors(client, sql)

        log.info('Granting select to replication user')
        sql = f"""
        GRANT SELECT ON TABLE {self._table} TO {self._replication_username};
        """
        await self._execute_statement_ignore_errors(client, sql)

    async def _create_publication(self, client: Any) -> None:
        log.info('Creating publication for table')
        sql = f"""
        CREATE PUBLICATION {self._publication} FOR TABLE {self._table};
        """
        await self._execute_statement_ignore_errors(client, sql)

    async def _create_indexes(self, client: Any) -> None:
        indexes = [
            (
                'aggregate id, aggregate version index',
                f"CREATE UNIQUE INDEX event_store_idx_event_aggregate_id_version ON {self._table}(aggregate_id, aggregate_version);"
            ),
            (
                'id index',
                f"CREATE UNIQUE INDEX event_store_idx_event_id ON {self._table}(event_id);"
            ),
            (
                'causation index',
                f"CREATE INDEX event_store_idx_event_causation_id ON {self._table}(causation_id);"
            ),
            (
                'correlation index',
                f"CREATE INDEX event_store_idx_event_correlation_id ON {self._table}(correlation_id);"
            ),
            (
                'recording index',
                f"CREATE INDEX event_store_idx_occurred_on ON {self._table}(recorded_on);"
            ),
            (
                'event name index',
                f"CREATE INDEX event_store_idx_event_name ON {self._table}(event_name);"
            )
        ]

        for index_name, sql in indexes:
            log.info(f'Creating {index_name}')
            await self._execute_statement_ignore_errors(client, sql)