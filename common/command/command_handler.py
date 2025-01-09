from abc import ABC, abstractmethod
from typing import Any
from common.event_store.postgres_transactional_event_store import PostgresTransactionalEventStore
from common.command.command import Command

class CommandHandler(ABC):
    def __init__(self, postgres_transactional_event_store: PostgresTransactionalEventStore):
        self._postgres_transactional_event_store = postgres_transactional_event_store

    @abstractmethod
    async def handle_command(self, command: Command) -> None:
        pass