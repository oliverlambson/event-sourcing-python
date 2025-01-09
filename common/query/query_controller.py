from typing import TypeVar, Generic, Any
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from common.util.logger import log
from common.query.query_handler import QueryHandler
from common.query.query import Query

T = TypeVar('T')

class QueryController(Generic[T]):
    def __init__(self, mongo_transactional_projection_operator: MongoTransactionalProjectionOperator):
        self._mongo_transactional_projection_operator = mongo_transactional_projection_operator

    async def process_query(self, query: Query, query_handler: QueryHandler[T]) -> T:
        try:
            log.debug(f"Starting to process query: {query.__class__.__name__}")
            await self._mongo_transactional_projection_operator.start_transaction()
            result = await query_handler.handle_query(query)
            await self._mongo_transactional_projection_operator.commit_transaction()
            await self._mongo_transactional_projection_operator.abort_dangling_transactions_and_return_session_to_pool()

            log.debug(f"Successfully processed query: {query.__class__.__name__}")
            return result

        except Exception as error:
            await self._mongo_transactional_projection_operator.abort_dangling_transactions_and_return_session_to_pool()
            log.error(f"Exception in ProcessQuery: {error}", error=error)
            raise RuntimeError(f"Failed to process query: {error}")