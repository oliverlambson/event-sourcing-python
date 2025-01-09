from typing import Optional
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from domain.cooking_club.membership.projection.members_by_cuisine.membership_application import MembershipApplication


class MembershipApplicationRepository:
    COLLECTION_NAME = 'CookingClub_MembersByCuisine_MembershipApplication'

    def __init__(self, mongo_operator: MongoTransactionalProjectionOperator):
        self._mongo_operator = mongo_operator

    async def save(self, membership_application: MembershipApplication) -> None:
        await self._mongo_operator.replace_one(
            self.COLLECTION_NAME,
            {'_id': membership_application._id},
            {
                '_id': membership_application._id,
                'first_name': membership_application.first_name,
                'last_name': membership_application.last_name,
                'favorite_cuisine': membership_application.favorite_cuisine
            },
            {'upsert': True}
        )

    async def find_one_by_id(self, _id: str) -> Optional[MembershipApplication]:
        results = await self._mongo_operator.find(
            self.COLLECTION_NAME,
            {'_id': _id}
        )
        if not results:
            return None

        doc = results[0]
        return MembershipApplication(
            _id=doc['_id'],
            first_name=doc['first_name'],
            last_name=doc['last_name'],
            favorite_cuisine=doc['favorite_cuisine']
        )