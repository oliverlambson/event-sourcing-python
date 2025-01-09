from abc import ABC
from datetime import datetime
from typing import Generic, TypeVar

T = TypeVar('T')

class Event(ABC, Generic[T]):
    def __init__(
        self,
        event_id: str,
        aggregate_id: str,
        aggregate_version: int,
        correlation_id: str,
        causation_id: str,
        recorded_on: datetime
    ):
        self._event_id = event_id
        self._aggregate_id = aggregate_id
        self._aggregate_version = aggregate_version
        self._correlation_id = correlation_id
        self._causation_id = causation_id
        self._recorded_on = recorded_on

    @property
    def event_id(self) -> str:
        return self._event_id

    @property
    def aggregate_id(self) -> str:
        return self._aggregate_id

    @property
    def aggregate_version(self) -> int:
        return self._aggregate_version

    @property
    def correlation_id(self) -> str:
        return self._correlation_id

    @property
    def causation_id(self) -> str:
        return self._causation_id

    @property
    def recorded_on(self) -> datetime:
        return self._recorded_on
