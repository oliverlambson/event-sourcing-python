from flask import Response
from common.serialized_event.deserializer import Deserializer
from common.ambar.ambar_http_request import AmbarHttpRequest
from common.ambar.ambar_response_factory import AmbarResponseFactory
from common.projection.projection_handler import ProjectionHandler
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from common.util.logger import log

class ProjectionController:
    def __init__(
        self,
        mongo_operator: MongoTransactionalProjectionOperator,
        deserializer: Deserializer,
    ):
        self._mongo_operator = mongo_operator
        self._deserializer = deserializer

    async def process_projection_http_request(
        self,
        ambar_http_request: AmbarHttpRequest,
        projection_handler: ProjectionHandler,
        projection_name: str
    )  -> tuple[Response, int]:
        try:
            log.debug(
                f"Starting to process projection for event name: {ambar_http_request.payload.event_name} "
                f"using handler: {projection_handler.__class__.__name__}"
            )

            event = self._deserializer.deserialize(ambar_http_request.payload)

            await self._mongo_operator.start_transaction()

            is_already_projected = await self._mongo_operator.count_documents(
                'ProjectionIdempotency_ProjectedEvent',
                {
                    'eventId': event.event_id,
                    'projectionName': projection_name
                }
            ) != 0

            if is_already_projected:
                await self._mongo_operator.abort_dangling_transactions_and_return_session_to_pool()
                log.debug(
                    f"Duplication projection ignored for event name: {ambar_http_request.payload.event_name} "
                    f"using handler: {projection_handler.__class__.__name__}"
                )
                return Response(AmbarResponseFactory.success_response(), content_type='application/json'), 200

            # Record projected event
            await self._mongo_operator.insert_one('ProjectionIdempotency_ProjectedEvent', {
                'eventId': event.event_id,
                'projectionName': projection_name
            })

            await projection_handler.project(event)

            await self._mongo_operator.commit_transaction()
            await self._mongo_operator.abort_dangling_transactions_and_return_session_to_pool()

            log.debug(
                f"Projection successfully processed for event name: {ambar_http_request.payload.event_name} "
                f"using handler: {projection_handler.__class__.__name__}"
            )
            return Response(AmbarResponseFactory.success_response(), content_type='application/json'), 200

        except Exception as ex:
            if isinstance(ex, ValueError) and str(ex).startswith('Unknown event type'):
                await self._mongo_operator.abort_dangling_transactions_and_return_session_to_pool()

                log.debug(
                    f"Unknown event in projection ignored for event name: {ambar_http_request.payload.event_name} "
                    f"using handler: {projection_handler.__class__.__name__}"
                )
                return Response(AmbarResponseFactory.success_response(), content_type='application/json'), 200

            await self._mongo_operator.abort_dangling_transactions_and_return_session_to_pool()
            log.error(
                f"Exception in ProcessProjectionHttpRequest: {ex}. "
                f"For event name: {ambar_http_request.payload.event_name} "
                f"using handler: {projection_handler.__class__.__name__}",
                ex
            )
            return Response(AmbarResponseFactory.retry_response(ex), content_type='application/json'), 200
