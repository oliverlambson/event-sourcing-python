from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class SerializedEvent(BaseModel):
    id: Optional[int] = None
    event_id: str
    aggregate_id: str
    causation_id: str
    correlation_id: str
    aggregate_version: int 
    json_payload: str
    json_metadata: str
    recorded_on: str
    event_name: str

    class Config:
        from_attributes = True
