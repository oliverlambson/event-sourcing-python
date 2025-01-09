import json
from datetime import datetime
from domain.cooking_club.membership.event.application_submitted import ApplicationSubmitted
from domain.cooking_club.membership.event.application_evaluated import ApplicationEvaluated
from domain.cooking_club.membership.aggregate.membership import MembershipStatus
from common.event.event import Event
from common.serialized_event.serialized_event import SerializedEvent

class Deserializer:
    def __init__(self):
        self._event_types = {
            'CookingClub_Membership_ApplicationSubmitted': ApplicationSubmitted,
            'CookingClub_Membership_ApplicationEvaluated': ApplicationEvaluated
        }

    def deserialize(self, serialized_event: SerializedEvent) -> Event:
        event_class = self._event_types.get(serialized_event.event_name)
        if not event_class:
            raise ValueError(f"Unknown event type: {serialized_event.event_name}")

        recorded_on = self._parse_datetime(serialized_event.recorded_on)
        payload = json.loads(serialized_event.json_payload)

        if event_class == ApplicationSubmitted:
            return ApplicationSubmitted(
                event_id=serialized_event.event_id,
                aggregate_id=serialized_event.aggregate_id,
                aggregate_version=serialized_event.aggregate_version,
                correlation_id=serialized_event.correlation_id,
                causation_id=serialized_event.causation_id,
                recorded_on=recorded_on,
                first_name=payload['firstName'],
                last_name=payload['lastName'],
                favorite_cuisine=payload['favoriteCuisine'],
                years_of_professional_experience=payload['yearsOfProfessionalExperience'],
                number_of_cooking_books_read=payload['numberOfCookingBooksRead']
            )
        elif event_class == ApplicationEvaluated:
            return ApplicationEvaluated(
                event_id=serialized_event.event_id,
                aggregate_id=serialized_event.aggregate_id,
                aggregate_version=serialized_event.aggregate_version,
                correlation_id=serialized_event.correlation_id,
                causation_id=serialized_event.causation_id,
                recorded_on=recorded_on,
                evaluation_outcome=MembershipStatus(payload['evaluationOutcome'])
            )
        else:
            raise ValueError(f"Unknown event type: {serialized_event.event_name}")

    def _parse_datetime(self, date_str: str) -> datetime:
        if not date_str.endswith(' UTC'):
            raise ValueError(f"Invalid date format: {date_str}")
        return datetime.strptime(date_str[:-4], '%Y-%m-%d %H:%M:%S')