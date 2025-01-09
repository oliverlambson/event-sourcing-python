from dataclasses import dataclass
from typing import List

@dataclass
class Cuisine:
    _id: str  # needs to be _id to be recognized as an _id field by MongoDB
    member_names: List[str]