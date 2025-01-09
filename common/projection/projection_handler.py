from abc import ABC, abstractmethod
from common.event.event import Event

class ProjectionHandler(ABC):
    @abstractmethod
    async def project(self, event: Event) -> None:
        pass