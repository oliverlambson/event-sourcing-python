from typing import Optional, List
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from domain.cooking_club.membership.projection.members_by_cuisine.cuisine import Cuisine


class CuisineRepository:
    COLLECTION_NAME = 'CookingClub_MembersByCuisine_Cuisine'

    def __init__(self, mongo_operator: MongoTransactionalProjectionOperator):
        self._mongo_operator = mongo_operator

    async def save(self, cuisine: Cuisine) -> None:
        await self._mongo_operator.replace_one(
            self.COLLECTION_NAME,
            {'_id': cuisine._id},
            {
                '_id': cuisine._id,
                'member_names': cuisine.member_names
            },
            {'upsert': True}
        )

    async def find_one_by_id(self, _id: str) -> Optional[Cuisine]:
        results = await self._mongo_operator.find(
            self.COLLECTION_NAME,
            {'_id': _id}
        )
        if not results:
            return None

        doc = results[0]
        return Cuisine(
            _id=doc['_id'],
            member_names=doc['member_names']
        )

    async def find_all(self) -> List[Cuisine]:
        docs = await self._mongo_operator.find(self.COLLECTION_NAME, {})
        return [
            Cuisine(
                _id=doc['_id'],
                member_names=doc['member_names']
            )
            for doc in docs
        ]