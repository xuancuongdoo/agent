"""
Action Module

This module is responsible for handling actions in the agent system, including
action triggers, parameters, and responses.
"""
from typing import Dict, List, Optional, Any, Union
import asyncio

class Action:
    """
    Action class for handling action triggers and execution.
    """
    
    def __init__(self):
        """Initialize the action module"""
        self.registered_actions = {}
        self.action_history = []
    
    def register_action(self, trigger: str, handler) -> bool:
        """
        Register an action handler for a specific trigger.
        
        Args:
            trigger: The action trigger name
            handler: The function to call when the trigger is activated
        
        Returns:
            True if successful, False otherwise
        """
        self.registered_actions[trigger] = handler
        return True
    
    async def execute(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action.
        
        Args:
            action: The action to execute, containing:
                - action_trigger: The trigger name
                - actual_task: The task to execute
                - parameters: Parameters for the action
        
        Returns:
            The action response
        """
        trigger = action.get("action_trigger")
        task = action.get("actual_task")
        parameters = action.get("parameters", {})
        
        if not trigger or not task:
            return {"status": "error", "message": "Invalid action: missing trigger or task"}
        
        # Check if we have a registered handler for this trigger
        if trigger in self.registered_actions:
            try:
                # Call the registered handler
                handler = self.registered_actions[trigger]
                response = await handler(task, parameters)
                
                # Record the action in history
                action_record = {
                    "trigger": trigger,
                    "task": task,
                    "parameters": parameters,
                    "response": response,
                    "status": "success"
                }
                self.action_history.append(action_record)
                
                return response
            except Exception as e:
                # Handle error
                error_response = {"status": "error", "message": str(e)}
                
                # Record the action in history
                action_record = {
                    "trigger": trigger,
                    "task": task,
                    "parameters": parameters,
                    "response": None,
                    "error": str(e),
                    "status": "failed"
                }
                self.action_history.append(action_record)
                
                return error_response
        else:
            # Default action handling
            await asyncio.sleep(0.5)  # Simulate work
            
            # Create a mock response
            response = {
                "status": "success",
                "message": f"Executed action: {task}",
                "trigger": trigger,
                "result": f"Action {trigger} completed for task {task}"
            }
            
            # Record the action in history
            action_record = {
                "trigger": trigger,
                "task": task,
                "parameters": parameters,
                "response": response,
                "status": "success"
            }
            self.action_history.append(action_record)
            
            return response
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the action execution history.
        
        Args:
            limit: Maximum number of history items to return
        
        Returns:
            List of action execution records
        """
        return self.action_history[-limit:] if limit else self.action_history.copy() 