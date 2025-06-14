"""
Workflow Module

This module is responsible for managing the workflow execution, including tracking
nodes, variables, and workflow types.
"""
from typing import Dict, List, Optional, Any, Union
import uuid
import asyncio
import time
from datetime import datetime

class Workflow:
    """
    Workflow class for managing the execution of agent tasks and workflows.
    """
    
    def __init__(self):
        """Initialize the workflow module"""
        # Store for active workflows
        self.active_workflows = {}
        
        # Store for workflow nodes
        self.nodes = {}
        
        # Store for workflow variables
        self.variables = {}
        
        # Supported workflow types
        self.workflow_types = ["sequential", "parallel", "conditional"]
    
    async def initialize(self, task_queue: List[Dict[str, Any]], actions: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> str:
        """
        Initialize a new workflow.
        
        Args:
            task_queue: List of tasks to execute
            actions: List of actions to perform
            context: Optional context for the workflow
        
        Returns:
            The ID of the new workflow
        """
        # Generate a unique ID for this workflow
        workflow_id = str(uuid.uuid4())
        
        # Create workflow structure
        workflow = {
            "id": workflow_id,
            "type": "sequential",  # Default type
            "task_queue": task_queue,
            "actions": actions,
            "context": context or {},
            "current_task_index": 0,
            "status": "initialized",
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "results": [],
            "errors": []
        }
        
        # Store the workflow
        self.active_workflows[workflow_id] = workflow
        
        # Initialize nodes for this workflow
        self.nodes[workflow_id] = []
        for i, task in enumerate(task_queue):
            node = {
                "id": str(uuid.uuid4()),
                "workflow_id": workflow_id,
                "task": task,
                "status": "pending",
                "index": i,
                "result": None,
                "error": None
            }
            self.nodes[workflow_id].append(node)
        
        # Initialize variables for this workflow
        self.variables[workflow_id] = context.copy() if context else {}
        
        return workflow_id
    
    async def execute(self, workflow_id: str, reasoning=None, memory=None) -> Dict[str, Any]:
        """
        Execute a workflow.
        
        Args:
            workflow_id: The ID of the workflow to execute
            reasoning: The reasoning module instance
            memory: The memory module instance
        
        Returns:
            The result of the workflow execution
        """
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.active_workflows[workflow_id]
        workflow["status"] = "running"
        
        # Save workflow status to memory if available
        if memory:
            await memory.set(f"workflow_{workflow_id}", workflow, "short_term")
        
        # Execute each task in the queue
        task_results = []
        
        for i, task in enumerate(workflow["task_queue"]):
            workflow["current_task_index"] = i
            
            # Update node status
            self.nodes[workflow_id][i]["status"] = "running"
            
            try:
                # Execute the task using reasoning if available
                if reasoning:
                    # Include any workflow context and previous results as context
                    context = {
                        **workflow["context"],
                        "previous_results": task_results,
                        "current_task_index": i,
                        "total_tasks": len(workflow["task_queue"])
                    }
                    
                    result = await reasoning.execute_task(task, context)
                    
                    # Save result
                    task_results.append(result)
                    
                    # Update node with result
                    self.nodes[workflow_id][i]["result"] = result
                    self.nodes[workflow_id][i]["status"] = "completed"
                    
                    # Save to memory if available
                    if memory:
                        await memory.set(f"task_result_{task.get('task_description')}", result, "long_term")
                        await memory.set("intermediate_outcomes", {f"task_{i}": result}, "short_term")
                else:
                    # Mock execution
                    await asyncio.sleep(1)  # Simulate work
                    result = {"status": "success", "message": f"Executed task {i}: {task.get('task_description')}"}
                    task_results.append(result)
                    self.nodes[workflow_id][i]["result"] = result
                    self.nodes[workflow_id][i]["status"] = "completed"
            
            except Exception as e:
                # Handle error
                error = {"message": str(e), "task_index": i, "task": task}
                workflow["errors"].append(error)
                self.nodes[workflow_id][i]["status"] = "failed"
                self.nodes[workflow_id][i]["error"] = error
                break
        
        # Update workflow status
        if len(workflow["errors"]) > 0:
            workflow["status"] = "failed"
        else:
            workflow["status"] = "completed"
            workflow["results"] = task_results
        
        workflow["completed_at"] = datetime.now().isoformat()
        
        # Execute any "task_complete" actions
        if workflow["status"] == "completed":
            for action in workflow["actions"]:
                if action.get("action_trigger") == "task_complete":
                    action["action_response"] = {"status": "success", "message": "Action executed"}
        
        # Save final workflow status to memory if available
        if memory:
            await memory.set(f"workflow_{workflow_id}", workflow, "long_term")
            # Also save the last completed workflow
            await memory.set("last_completed_workflow", workflow_id, "short_term")
        
        return workflow
    
    async def get_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a workflow.
        
        Args:
            workflow_id: The ID of the workflow
        
        Returns:
            The status of the workflow, or None if not found
        """
        if workflow_id not in self.active_workflows:
            return None
        
        workflow = self.active_workflows[workflow_id]
        
        return {
            "id": workflow["id"],
            "status": workflow["status"],
            "current_task_index": workflow["current_task_index"],
            "total_tasks": len(workflow["task_queue"]),
            "started_at": workflow["started_at"],
            "completed_at": workflow["completed_at"],
            "result": workflow.get("results", []),
            "errors": workflow.get("errors", [])
        }
    
    # A2A Workflow Support Methods
    async def register_workflow(self, workflow_name: str, workflow_definition: Dict[str, Any]) -> None:
        """
        Register a workflow template for A2A agents.
        
        Args:
            workflow_name: Name of the workflow
            workflow_definition: Workflow definition dictionary
        """
        if not hasattr(self, 'registered_workflows'):
            self.registered_workflows = {}
        
        self.registered_workflows[workflow_name] = workflow_definition
        print(f"Registered workflow: {workflow_name}")
    
    async def update_task_status(self, task_id: str, status: str, result: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the status of a task for A2A agents.
        
        Args:
            task_id: Task identifier
            status: New status
            result: Optional result data
        """
        if task_id in self.active_workflows:
            workflow = self.active_workflows[task_id]
            workflow["status"] = status
            if result:
                workflow["result"] = result
            if status == "completed":
                workflow["completed_at"] = datetime.now().isoformat()
        else:
            # Create new task entry
            self.active_workflows[task_id] = {
                "id": task_id,
                "status": status,
                "result": result,
                "created_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat() if status == "completed" else None
            }
    
    async def get_workflow_template(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a registered workflow template.
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            Workflow definition or None
        """
        if not hasattr(self, 'registered_workflows'):
            return None
        
        return self.registered_workflows.get(workflow_name)
    
    async def list_registered_workflows(self) -> List[str]:
        """
        List all registered workflow names.
        
        Returns:
            List of workflow names
        """
        if not hasattr(self, 'registered_workflows'):
            return []
        
        return list(self.registered_workflows.keys())