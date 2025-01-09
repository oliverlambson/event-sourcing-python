from pydantic import BaseModel
from common.serialized_event.serialized_event import SerializedEvent

class AmbarHttpRequest(BaseModel):
    data_source_id: str
    data_source_description: str
    data_destination_id: str
    data_destination_description: str
    payload: SerializedEvent

    class Config:
        from_attributes = True