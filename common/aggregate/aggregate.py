from abc import ABC
from typing import Generic, TypeVar

T = TypeVar('T')

class Aggregate(ABC, Generic[T]):
    def __init__(self, aggregate_id: str, aggregate_version: int):
        self._aggregate_id = aggregate_id
        self._aggregate_version = aggregate_version

    @property
    def aggregate_id(self) -> str:
        return self._aggregate_id

    @property
    def aggregate_version(self) -> int:
        return self._aggregate_version
