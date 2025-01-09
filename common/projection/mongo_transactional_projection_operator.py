from typing import Optional, Dict, Any, List, TypeVar, Generic
from pymongo import MongoClient
from pymongo.client_session import ClientSession
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from pymongo.read_preferences import ReadPreference
from common.util.mongo_session_pool import MongoSessionPool

T = TypeVar('T')

class MongoTransactionalProjectionOperator:
    def __init__(self, session_pool: MongoSessionPool, database_name: str):
        self._session: Optional[ClientSession] = None
        self._db: Optional[MongoClient] = None
        self._session_pool = session_pool
        self._database_name = database_name

    async def start_transaction(self) -> None:
        if self._session is not None:
            raise RuntimeError('Session to MongoDB already active!')

        if self._db is not None:
            raise RuntimeError('Database already initialized in the current session.')

        try:
            self._session = await self._session_pool.start_session()
            client = self._session_pool.get_client()
            self._db = client[self._database_name]

            transaction_options = {
                'read_concern': ReadConcern('snapshot'),
                'write_concern': WriteConcern('majority'),
                'read_preference': ReadPreference.PRIMARY
            }

            self._session.start_transaction(**transaction_options)
        except Exception as e:
            raise RuntimeError(f"Failed to start MongoDB transaction: {e}")

    async def commit_transaction(self) -> None:
        if self._session is None:
            raise RuntimeError('Session must be active to commit transaction to MongoDB!')

        if not self._session.in_transaction:
            raise RuntimeError('Transaction must be active to commit transaction to MongoDB!')

        try:
            self._session.commit_transaction()
        except Exception as e:
            raise RuntimeError(f"Failed to commit MongoDB transaction: {e}")

    async def abort_dangling_transactions_and_return_session_to_pool(self) -> None:
        if self._session is None:
            self._db = None
            return

        try:
            if self._session.in_transaction:
                self._session.abort_transaction()
        except Exception as e:
            from common.util.logger import log
            log.error('Failed to abort Mongo transaction', error=e)

        try:
            self._session.end_session()
        except Exception as e:
            from common.util.logger import log
            log.error('Failed to release Mongo session', error=e)

        self._session = None
        self._db = None

    async def find(self, collection_name: str, filter_query: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> List[T]:
        session, db = await self._operate()
        collection = db[collection_name]
        cursor = collection.find(filter_query, session=session, **(options or {}))
        return list(cursor)

    async def replace_one(self, collection_name: str, filter_query: Dict[str, Any],
                         replacement: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        session, db = await self._operate()
        collection = db[collection_name]
        return collection.replace_one(filter_query, replacement, session=session, **(options or {}))

    async def insert_one(self, collection_name: str, document: Dict[str, Any],
                        options: Optional[Dict[str, Any]] = None) -> None:
        session, db = await self._operate()
        collection = db[collection_name]
        collection.insert_one(document, session=session, **(options or {}))

    async def count_documents(self, collection_name: str, filter_query: Dict[str, Any],
                            options: Optional[Dict[str, Any]] = None) -> int:
        session, db = await self._operate()
        collection = db[collection_name]
        return collection.count_documents(filter_query, session=session, **(options or {}))

    async def _operate(self):
        if self._session is None:
            raise RuntimeError('Session must be active to read or write to MongoDB!')

        if not self._session.in_transaction:
            raise RuntimeError('Transaction must be active to read or write to MongoDB!')

        if self._db is None:
            raise RuntimeError('Database must be initialized in the current session.')

        return self._session, self._db