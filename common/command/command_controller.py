from typing import Any
from common.event_store.postgres_transactional_event_store import PostgresTransactionalEventStore
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from common.util.logger import log
from common.command.command import Command
from common.command.command_handler import CommandHandler

class CommandController:
    def __init__(
        self,
        postgres_transactional_event_store: PostgresTransactionalEventStore,
        mongo_transactional_projection_operator: MongoTransactionalProjectionOperator,
    ):
        self._postgres_transactional_event_store = postgres_transactional_event_store
        self._mongo_transactional_projection_operator = mongo_transactional_projection_operator

    async def process_command(self, command: Command, command_handler: CommandHandler) -> None:
        try:
            log.debug(f"Starting to process command: {command.__class__.__name__}")
            await self._postgres_transactional_event_store.begin_transaction()
            await self._mongo_transactional_projection_operator.start_transaction()
            await command_handler.handle_command(command)
            await self._postgres_transactional_event_store.commit_transaction()
            await self._mongo_transactional_projection_operator.commit_transaction()

            await self._postgres_transactional_event_store.abort_dangling_transactions_and_return_connection_to_pool()
            await self._mongo_transactional_projection_operator.abort_dangling_transactions_and_return_session_to_pool()
            log.debug(f"Successfully processed command: {command.__class__.__name__}")

        except Exception as error:
            await self._postgres_transactional_event_store.abort_dangling_transactions_and_return_connection_to_pool()
            await self._mongo_transactional_projection_operator.abort_dangling_transactions_and_return_session_to_pool()
            log.error(f"Exception in ProcessCommand: {error}", error=error)
            raise RuntimeError(f"Failed to process command: {error}")