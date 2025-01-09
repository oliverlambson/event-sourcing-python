from datetime import datetime
from common.command.command_handler import CommandHandler
from common.util.id_generator import IdGenerator
from domain.cooking_club.membership.event.application_submitted import ApplicationSubmitted
from domain.cooking_club.membership.command.submit_application.submit_application_command import SubmitApplicationCommand

class SubmitApplicationCommandHandler(CommandHandler):
    async def handle_command(self, command: SubmitApplicationCommand) -> None:
        event_id = IdGenerator.generate_random_id()
        aggregate_id = IdGenerator.generate_random_id()

        application_submitted = ApplicationSubmitted(
            event_id=event_id,
            aggregate_id=aggregate_id,
            aggregate_version=1,
            correlation_id=event_id,
            causation_id=event_id,
            recorded_on=datetime.utcnow(),
            first_name=command.first_name,
            last_name=command.last_name,
            favorite_cuisine=command.favorite_cuisine,
            years_of_professional_experience=command.years_of_professional_experience,
            number_of_cooking_books_read=command.number_of_cooking_books_read
        )

        await self._postgres_transactional_event_store.save_event(application_submitted)