from flask import Request, Response
from common.projection.projection_controller import ProjectionController
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from common.serialized_event.deserializer import Deserializer
from common.ambar.ambar_http_request import AmbarHttpRequest
from domain.cooking_club.membership.projection.members_by_cuisine.members_by_cuisine_projection_handler import MembersByCuisineProjectionHandler

class MembersByCuisineProjectionController(ProjectionController):
    def __init__(
        self,
        mongo_operator: MongoTransactionalProjectionOperator,
        deserializer: Deserializer,
        members_by_cuisine_projection_handler: MembersByCuisineProjectionHandler,
    ):
        super().__init__(mongo_operator, deserializer)
        self._members_by_cuisine_projection_handler = members_by_cuisine_projection_handler

    async def handle_projection_request(self, request: Request) -> tuple[Response, int]:
        return await self.process_projection_http_request(
            AmbarHttpRequest.model_validate(request.get_json()),
            self._members_by_cuisine_projection_handler,
            'CookingClub_MembersByCuisine'
        )