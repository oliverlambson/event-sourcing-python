from datetime import datetime
import json
import pytz
from domain.cooking_club.membership.event.application_submitted import ApplicationSubmitted
from domain.cooking_club.membership.event.application_evaluated import ApplicationEvaluated
from common.event.event import Event
from common.serialized_event.serialized_event import SerializedEvent

class Serializer:
    def serialize(self, event: Event) -> SerializedEvent:
        return SerializedEvent(
            event_id=event.event_id,
            aggregate_id=event.aggregate_id,
            aggregate_version=event.aggregate_version,
            correlation_id=event.correlation_id,
            causation_id=event.causation_id,
            recorded_on=self._format_datetime(event.recorded_on),
            event_name=self._determine_event_name(event),
            json_payload=self._create_json_payload(event),
            json_metadata='{}'
        )

    def _format_datetime(self, dt: datetime) -> str:
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        else:
            dt = dt.astimezone(pytz.UTC)
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')

    def _determine_event_name(self, event: Event) -> str:
        if isinstance(event, ApplicationSubmitted):
            return 'CookingClub_Membership_ApplicationSubmitted'
        if isinstance(event, ApplicationEvaluated):
            return 'CookingClub_Membership_ApplicationEvaluated'
        raise ValueError(f"Unknown event type: {event.__class__.__name__}")

    def _create_json_payload(self, event: Event) -> str:
        if isinstance(event, ApplicationSubmitted):
            payload = {
                'firstName': event.first_name,
                'lastName': event.last_name,
                'favoriteCuisine': event.favorite_cuisine,
                'yearsOfProfessionalExperience': event.years_of_professional_experience,
                'numberOfCookingBooksRead': event.number_of_cooking_books_read
            }
        elif isinstance(event, ApplicationEvaluated):
            payload = {
                'evaluationOutcome': event.evaluation_outcome.value
            }
        else:
            raise ValueError(f"Unknown event type: {event.__class__.__name__}")

        return json.dumps(payload)