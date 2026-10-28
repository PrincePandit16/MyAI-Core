from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseConnector(ABC):
    """
    Base interface for all external service connectors (Email, Calendar, etc.)
    """

    @abstractmethod
    async def authorize(self, user_id: str) -> bool:
        """
        Handle the authorization flow for the connector.
        Returns True if authorized, False otherwise.
        """
        pass

    @abstractmethod
    async def fetch(self, query: str) -> Any:
        """
        Fetch data from the external service.
        """
        pass

    @abstractmethod
    async def perform_action(
        self, action_name: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a specific action on the external service.
        """
        pass
