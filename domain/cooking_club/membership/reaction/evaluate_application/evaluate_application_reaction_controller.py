from flask import Request, Response
from common.reaction.reaction_controller import ReactionController
from common.event_store.postgres_transactional_event_store import PostgresTransactionalEventStore
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from common.serialized_event.deserializer import Deserializer
from common.ambar.ambar_http_request import AmbarHttpRequest
from domain.cooking_club.membership.reaction.evaluate_application.evaluate_application_reaction_handler import EvaluateApplicationReactionHandler

class EvaluateApplicationReactionController(ReactionController):
    def __init__(
        self,
        event_store: PostgresTransactionalEventStore,
        mongo_operator: MongoTransactionalProjectionOperator,
        deserializer: Deserializer,
        evaluate_application_reaction_handler: EvaluateApplicationReactionHandler
    ):
        super().__init__(event_store, mongo_operator, deserializer)
        self._evaluate_application_reaction_handler = evaluate_application_reaction_handler

    async def handle_reaction_request(self, request: Request) -> tuple[Response, int]:
        return await self.process_reaction_http_request(
            AmbarHttpRequest.model_validate(request.get_json()),
            self._evaluate_application_reaction_handler,
        )