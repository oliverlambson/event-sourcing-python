from enum import Enum
from dataclasses import dataclass
from common.aggregate.aggregate import Aggregate

class MembershipStatus(Enum):
    REQUESTED = "Requested"
    APPROVED = "Approved"
    REJECTED = "Rejected"

@dataclass
class Membership(Aggregate):
    first_name: str
    last_name: str
    status: MembershipStatus

    def __init__(self, aggregate_id: str, aggregate_version: int, first_name: str, last_name: str, status: MembershipStatus):
        super().__init__(aggregate_id, aggregate_version)
        self.first_name = first_name
        self.last_name = last_name
        self.status = status