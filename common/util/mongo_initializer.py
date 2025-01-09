from common.util.mongo_session_pool import MongoSessionPool
from common.util.logger import log

class MongoInitializer:
    def __init__(
        self,
        session_pool: MongoSessionPool,
        database_name: str
    ):
        self._client = session_pool.get_client()
        self._database_name = database_name

    async def initialize(self) -> None:
        log.info('Initializing MongoDB collections and indexes...')

        try:
            db = self._client[self._database_name]

            # Create collections
            log.info('Creating collections...')
            await self._ensure_collections(db)
            log.info('Collections created successfully')

            # Create indexes
            log.info('Creating indexes...')
            await self._create_indexes(db)
            log.info('Indexes created successfully')

        except Exception as error:
            log.error('Error initializing MongoDB:', error=error)
            raise

    async def _ensure_collections(self, db) -> None:
        collections = [
            'CookingClub_MembersByCuisine_MembershipApplication',
            'CookingClub_MembersByCuisine_Cuisine',
            'ProjectionIdempotency_ProjectedEvent'
        ]

        for collection_name in collections:
            try:
                if collection_name not in db.list_collection_names():
                    db.create_collection(collection_name)
                    log.debug(f"Collection {collection_name} created")
                else:
                    log.debug(f"Collection {collection_name} already exists")
            except Exception as error:
                log.error(f"Error ensuring collection {collection_name}:", error=error)
                raise

    async def _create_indexes(self, db) -> None:
        try:
            membership_application = db['CookingClub_MembersByCuisine_MembershipApplication']
            membership_application.create_index(
                [('favorite_cuisine', 1)],
                background=True,
                name='favoriteCuisine_asc'
            )

            projection_idempotency = db['ProjectionIdempotency_ProjectedEvent']
            projection_idempotency.create_index(
                [('eventId', 1), ('projectionName', 1)],
                unique=True,
                background=True,
                name='eventId_ProjectionName_unique'
            )

            log.debug('Indexes created')
        except Exception as error:
            log.error('Error creating indexes:', error=error)
            raise