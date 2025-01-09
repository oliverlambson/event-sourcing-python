from flask import Request, Response, jsonify
from common.query.query_controller import QueryController
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from domain.cooking_club.membership.query.members_by_cuisine.members_by_cuisine_query import MembersByCuisineQuery
from domain.cooking_club.membership.query.members_by_cuisine.members_by_cuisine_query_handler import MembersByCuisineQueryHandler

class MembersByCuisineQueryController(QueryController):
    def __init__(
        self,
        mongo_operator: MongoTransactionalProjectionOperator,
        members_by_cuisine_query_handler: MembersByCuisineQueryHandler
    ):
        super().__init__(mongo_operator)
        self._members_by_cuisine_query_handler = members_by_cuisine_query_handler

    async def handle_members_by_cuisine(self, request: Request)  -> tuple[Response, int]:
        query = MembersByCuisineQuery()
        result = await self.process_query(query, self._members_by_cuisine_query_handler)
        return jsonify([{
            'cuisine': cuisine._id,
            'members': cuisine.member_names
        } for cuisine in result]), 200