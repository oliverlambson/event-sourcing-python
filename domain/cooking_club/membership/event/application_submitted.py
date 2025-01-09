from datetime import datetime
from common.event.creation_event import CreationEvent
from domain.cooking_club.membership.aggregate.membership import Membership, MembershipStatus

class ApplicationSubmitted(CreationEvent[Membership]):
    def __init__(
        self,
        event_id: str,
        aggregate_id: str,
        aggregate_version: int,
        correlation_id: str,
        causation_id: str,
        recorded_on: datetime,
        first_name: str,
        last_name: str,
        favorite_cuisine: str,
        years_of_professional_experience: int,
        number_of_cooking_books_read: int,
    ):
        super().__init__(
            event_id=event_id,
            aggregate_id=aggregate_id,
            aggregate_version=aggregate_version,
            correlation_id=correlation_id,
            causation_id=causation_id,
            recorded_on=recorded_on
        )
        self.first_name = first_name
        self.last_name = last_name
        self.favorite_cuisine = favorite_cuisine
        self.years_of_professional_experience = years_of_professional_experience
        self.number_of_cooking_books_read = number_of_cooking_books_read

    def create_aggregate(self) -> Membership:
        return Membership(
            aggregate_id=self.aggregate_id,
            aggregate_version=self.aggregate_version,
            first_name=self.first_name,
            last_name=self.last_name,
            status=MembershipStatus.REQUESTED
        )