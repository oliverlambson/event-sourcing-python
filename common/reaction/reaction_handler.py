from abc import ABC, abstractmethod
from common.event.event import Event
from common.event_store.postgres_transactional_event_store import PostgresTransactionalEventStore

class ReactionHandler(ABC):
    def __init__(self, postgres_transactional_event_store: PostgresTransactionalEventStore):
        self._postgres_transactional_event_store = postgres_transactional_event_store

    @abstractmethod
    async def react(self, event: Event) -> None:
        pass