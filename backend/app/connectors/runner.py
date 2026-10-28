import logging
from typing import Any, Dict

from .calendar import CalendarConnector

logger = logging.getLogger(__name__)


class ActionRunner:
    """
    Orchestrates the execution of actions triggered by the AI assistant.
    """

    def __init__(self):
        # Map of available connectors
        self.connectors = {
            "calendar": CalendarConnector(),
            # "email": EmailConnector(), # Future expansion
        }

    async def run_action(self, action_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes an action based on the provided request.
        Expected format: {"connector": "calendar", "action": "create_event", "params": {...}}
        """
        connector_name = action_request.get("connector")
        action_name = action_request.get("action")
        params = action_request.get("params", {})

        if not connector_name or not action_name:
            return {
                "status": "error",
                "message": "Missing connector or action name in request.",
            }

        connector = self.connectors.get(connector_name)
        if not connector:
            return {
                "status": "error",
                "message": f"Connector '{connector_name}' not supported.",
            }

        try:
            logger.info(f"ActionRunner triggering {action_name} on {connector_name}")
            # Ensure user is authorized (simplified for MVP)
            # In production, we'd pass the user_id from the request context
            await connector.authorize("current_user_id")

            result = await connector.perform_action(action_name, params)
            return result
        except Exception as e:
            logger.exception(f"Error running action {action_name} on {connector_name}")
            return {"status": "error", "message": str(e)}
