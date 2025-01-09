from typing import List

from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from common.query.query_handler import QueryHandler
from domain.cooking_club.membership.projection.members_by_cuisine.cuisine import Cuisine
from domain.cooking_club.membership.projection.members_by_cuisine.cuisine_repository import CuisineRepository
from domain.cooking_club.membership.query.members_by_cuisine.members_by_cuisine_query import MembersByCuisineQuery

class MembersByCuisineQueryHandler(QueryHandler[List[Cuisine]]):
    def __init__(
        self,
        mongo_operator: MongoTransactionalProjectionOperator,
        cuisine_repository: CuisineRepository
    ):
        super().__init__(mongo_operator)
        self._cuisine_repository = cuisine_repository

    async def handle_query(self, query: MembersByCuisineQuery) -> List[Cuisine]:
        return await self._cuisine_repository.find_all()