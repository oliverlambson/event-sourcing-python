from dataclasses import dataclass
from typing import Generic, TypeVar
from common.aggregate.aggregate import Aggregate

T = TypeVar('T', bound=Aggregate)

@dataclass
class AggregateAndEventIdsInLastEvent(Generic[T]):
    aggregate: T
    event_id_of_last_event: str
    correlation_id_of_last_event: str