"""
Agent Server - Main Entry Point

This is the main entry point for the agent server, which orchestrates the
planning, reasoning, memory, and workflow components.
"""
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Union

# Import our modules
from agent_server.planning.planning import Planning
from agent_server.reasoning.reasoning import Reasoning
from agent_server.memory.memory import Memory
from agent_server.workflow.workflow import Workflow
from agent_server.action.action import Action

# Import A2A research agents
from agent_server.agent_server.reasoning.a2a_api import router as a2a_router, initialize_a2a_service

app = FastAPI(
    title="Agent Server", 
    description="Agent Execution Server with A2A Research Capabilities",
    version="1.0.0"
)

class AgentRequest(BaseModel):
    """Request model for agent execution"""
    agent_goal: str
    agent_role: Optional[str] = None
    task: str
    tool: Optional[str] = None
    expected_output: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    """Response model from agent execution"""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class A2AResearchRequest(BaseModel):
    """Request model for A2A research"""
    user_id: str
    research_query: str
    research_type: str = "general"
    depth: str = "moderate"
    sources: Optional[List[str]] = None

class A2AResearchResponse(BaseModel):
    """Response model for A2A research"""
    session_id: str
    research_query: str
    status: str
    results: Dict[str, Any]
    summary: str

# Singleton instances
planning = Planning()
reasoning = Reasoning()
memory = Memory()
workflow = Workflow()
action = Action()

# Include A2A research router
app.include_router(a2a_router)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    # Initialize A2A service with existing memory and workflow services
    await initialize_a2a_service(memory, workflow)
    print("Agent Server started with A2A Research Agents")

@app.post("/execute", response_model=AgentResponse)
async def execute_agent(request: AgentRequest):
    """
    Execute an agent task based on the provided request.
    This orchestrates the planning, reasoning, and execution components.
    """
    try:
        # Create planning input
        planning_input = {
            "agent_goal": request.agent_goal,
            "agent_role": request.agent_role,
            "task": request.task,
            "tool": request.tool,
            "expected_output": request.expected_output
        }
        
        # Generate plan
        planning_output = await planning.generate_plan(planning_input)
        
        # Create task queue and actions
        task_queue = planning_output.get("sub_task_queue", [])
        actions = planning_output.get("actions", [])
        
        # Initialize workflow
        task_id = await workflow.initialize(
            task_queue=task_queue,
            actions=actions,
            context=request.context
        )
        
        # Start execution in the background
        asyncio.create_task(execute_workflow(task_id))
        
        return AgentResponse(
            task_id=task_id,
            status="running"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def execute_workflow(task_id: str):
    """Background task to execute the workflow"""
    try:
        # Execute workflow
        await workflow.execute(task_id, reasoning=reasoning, memory=memory)
    except Exception as e:
        # Log error
        print(f"Error executing workflow {task_id}: {str(e)}")

@app.get("/status/{task_id}", response_model=AgentResponse)
async def get_task_status(task_id: str):
    """Get the status of a running task"""
    status = await workflow.get_status(task_id)
    
    if not status:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return AgentResponse(
        task_id=task_id,
        status=status.get("status", "unknown"),
        result=status.get("result")
    )

@app.get("/memory/{key}")
async def get_memory(key: str):
    """Retrieve an item from memory"""
    value = await memory.get(key)
    
    if value is None:
        raise HTTPException(status_code=404, detail=f"Memory key {key} not found")
    
    return {"key": key, "value": value}

@app.post("/research", response_model=A2AResearchResponse)
async def conduct_a2a_research(request: A2AResearchRequest):
    """
    Conduct research using A2A agents (simplified endpoint)
    """
    try:
        from agent_server.reasoning.a2a_api import get_a2a_service
        
        # Get A2A service
        service = await get_a2a_service()
        
        # Create research session
        session_id = await service.create_research_session(
            user_id=request.user_id,
            research_goal=f"Research: {request.research_query}"
        )
        
        # Conduct research
        result = await service.conduct_research(
            session_id=session_id,
            research_query=request.research_query,
            research_type=request.research_type,
            depth=request.depth,
            sources=request.sources
        )
        
        return A2AResearchResponse(
            session_id=session_id,
            research_query=request.research_query,
            status=result.get("status", "completed"),
            results=result,
            summary=result.get("summary", "Research completed successfully")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"A2A research failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with basic server info"""
    return {
        "name": "Agent Server",
        "version": "1.0.0",
        "description": "Agent Execution Server with A2A Research Capabilities",
        "endpoints": [
            {"path": "/execute", "method": "POST", "description": "Execute an agent task"},
            {"path": "/status/{task_id}", "method": "GET", "description": "Get task status"},
            {"path": "/memory/{key}", "method": "GET", "description": "Get memory item"},
            {"path": "/research", "method": "POST", "description": "Conduct A2A research"},
            {"path": "/a2a-research/*", "method": "Various", "description": "A2A research endpoints"}
        ],
        "services": {
            "planning": "active",
            "reasoning": "active", 
            "memory": "active",
            "workflow": "active",
            "a2a_research": "active"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 