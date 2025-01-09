from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from common.event.event import Event
from common.aggregate.aggregate import Aggregate

T = TypeVar('T', bound=Aggregate)

class TransformationEvent(Event[T], ABC, Generic[T]):
    @abstractmethod
    def transform_aggregate(self, aggregate: T) -> T:
        pass
