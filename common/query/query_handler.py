from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from common.query.query import Query

T = TypeVar('T')

class QueryHandler(ABC, Generic[T]):
    def __init__(self, mongo_transactional_projection_operator: MongoTransactionalProjectionOperator):
        self._mongo_transactional_projection_operator = mongo_transactional_projection_operator

    @abstractmethod
    async def handle_query(self, query: Query) -> T:
        pass