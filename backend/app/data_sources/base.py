"""Base class for all data source clients."""

from abc import ABC, abstractmethod
from datetime import datetime


class BaseDataSource(ABC):
    """Abstract base for all traffic data source integrations."""

    def __init__(self, name: str, demo_mode: bool = True):
        self.name = name
        self.demo_mode = demo_mode
        self.last_fetched: datetime | None = None

    @abstractmethod
    async def fetch(self) -> dict:
        """Fetch latest data from the source."""
        ...

    def freshness_label(self) -> str:
        if self.last_fetched is None:
            return f"No data yet from {self.name}"
        delta = (datetime.utcnow() - self.last_fetched).total_seconds()
        if delta < 60:
            return f"Updated {int(delta)} seconds ago via {self.name}"
        return f"Updated {int(delta // 60)} minutes ago via {self.name}"
