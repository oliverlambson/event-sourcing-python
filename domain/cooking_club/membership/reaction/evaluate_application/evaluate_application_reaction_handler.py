from typing import cast
from common.reaction.reaction_handler import ReactionHandler
from common.event.event import Event
from common.util.id_generator import IdGenerator
from domain.cooking_club.membership.event.application_submitted import ApplicationSubmitted
from domain.cooking_club.membership.event.application_evaluated import ApplicationEvaluated
from domain.cooking_club.membership.aggregate.membership import Membership, MembershipStatus


class EvaluateApplicationReactionHandler(ReactionHandler):
    async def react(self, event: Event) -> None:
        if not isinstance(event, ApplicationSubmitted):
            return

        aggregate_data = await self._postgres_transactional_event_store.find_aggregate(event.aggregate_id)
        membership = cast(Membership, aggregate_data.aggregate)

        if membership.status != MembershipStatus.REQUESTED:
            return

        reaction_event_id = IdGenerator.generate_deterministic_id(
            f"CookingClub_Membership_ReviewedApplication:{event.event_id}"
        )

        if await self._postgres_transactional_event_store.does_event_already_exist(reaction_event_id):
            return

        # Business logic: approve if no professional experience but has read cooking books
        should_approve = (event.years_of_professional_experience == 0 and
                          event.number_of_cooking_books_read > 0)

        status = MembershipStatus.APPROVED if should_approve else MembershipStatus.REJECTED

        reaction_event = ApplicationEvaluated(
            event_id=reaction_event_id,
            aggregate_id=membership.aggregate_id,
            aggregate_version=membership.aggregate_version + 1,
            correlation_id=aggregate_data.correlation_id_of_last_event,
            causation_id=aggregate_data.event_id_of_last_event,
            recorded_on=event.recorded_on,
            evaluation_outcome=status
        )

        await self._postgres_transactional_event_store.save_event(reaction_event)