from flask import Request, Response, jsonify
from pydantic import BaseModel, Field
from common.command.command_controller import CommandController
from common.event_store.postgres_transactional_event_store import PostgresTransactionalEventStore
from common.projection.mongo_transactional_projection_operator import MongoTransactionalProjectionOperator
from domain.cooking_club.membership.command.submit_application.submit_application_command import SubmitApplicationCommand
from domain.cooking_club.membership.command.submit_application.submit_application_command_handler import SubmitApplicationCommandHandler


class SubmitApplicationRequest(BaseModel):
    first_name: str = Field(..., alias="firstName", min_length=1, max_length=100)
    last_name: str = Field(..., alias="lastName", min_length=1, max_length=100)
    favorite_cuisine: str = Field(..., alias="favoriteCuisine", min_length=1, max_length=100)
    years_of_professional_experience: int = Field(..., alias="yearsOfProfessionalExperience", ge=0, le=100)
    number_of_cooking_books_read: int = Field(..., alias="numberOfCookingBooksRead", ge=0)


class SubmitApplicationCommandController(CommandController):
    def __init__(
            self,
            event_store: PostgresTransactionalEventStore,
            mongo_operator: MongoTransactionalProjectionOperator,
            submit_application_command_handler: SubmitApplicationCommandHandler
    ):
        super().__init__(event_store, mongo_operator)
        self._submit_application_command_handler = submit_application_command_handler

    async def handle_submit_application(self, request: Request) -> tuple[Response, int]:
        session_token = request.headers.get('X-With-Session-Token')
        if not session_token:
            return jsonify({'error': 'Session token is required'}), 400

        request_data = SubmitApplicationRequest(**request.get_json())

        command = SubmitApplicationCommand(
            first_name=request_data.first_name,
            last_name=request_data.last_name,
            favorite_cuisine=request_data.favorite_cuisine,
            years_of_professional_experience=request_data.years_of_professional_experience,
            number_of_cooking_books_read=request_data.number_of_cooking_books_read
        )

        await self.process_command(command, self._submit_application_command_handler)
        return jsonify({}), 200