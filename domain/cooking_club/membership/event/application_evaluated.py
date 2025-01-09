from datetime import datetime
from common.event.transformation_event import TransformationEvent
from domain.cooking_club.membership.aggregate.membership import Membership, MembershipStatus

class ApplicationEvaluated(TransformationEvent[Membership]):
    def __init__(
        self,
        event_id: str,
        aggregate_id: str,
        aggregate_version: int,
        correlation_id: str,
        causation_id: str,
        recorded_on: datetime,
        evaluation_outcome: MembershipStatus,
    ):
        super().__init__(
            event_id=event_id,
            aggregate_id=aggregate_id,
            aggregate_version=aggregate_version,
            correlation_id=correlation_id,
            causation_id=causation_id,
            recorded_on=recorded_on
        )
        self.evaluation_outcome = evaluation_outcome

    def transform_aggregate(self, aggregate: Membership) -> Membership:
        return Membership(
            aggregate_id=self.aggregate_id,
            aggregate_version=self.aggregate_version,
            first_name=aggregate.first_name,
            last_name=aggregate.last_name,
            status=self.evaluation_outcome
        )