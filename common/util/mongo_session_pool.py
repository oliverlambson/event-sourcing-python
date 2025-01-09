from pymongo import MongoClient
from pymongo.server_api import ServerApi


class MongoSessionPool:
    def __init__(self, connection_string: str):
        settings = {
            'maxPoolSize': 20,
            'minPoolSize': 5,
            'maxIdleTimeMS': 10 * 60 * 1000,  # 10 minutes
            'waitQueueTimeoutMS': 2000,
            'replicaSet': 'rs0',
            'server_api': ServerApi('1'),
        }

        self._transactional_client = MongoClient(connection_string, **settings)

    async def start_session(self):
        self._transactional_client.admin.command('ping')  # Ensure connected
        return self._transactional_client.start_session()

    def get_client(self) -> MongoClient:
        return self._transactional_client