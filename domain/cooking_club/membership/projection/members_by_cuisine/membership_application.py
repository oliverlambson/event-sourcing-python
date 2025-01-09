from dataclasses import dataclass

@dataclass
class MembershipApplication:
    _id: str  # needs to be _id to be recognized as an _id field by MongoDB
    first_name: str
    last_name: str
    favorite_cuisine: str