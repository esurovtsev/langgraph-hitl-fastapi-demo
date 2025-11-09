# Lesson 3: Async MCP Tools with HITL Approval
# Async API with MCP tool approval using ainvoke()

from fastapi import APIRouter
from uuid import uuid4
from app.models import StartRequest, GraphResponse, ApproveRequest
from app.mcp_agent import get_agent
from langgraph.types import Command
from langchain_core.messages import HumanMessage

router = APIRouter()


async def run_agent_and_response(input_data, config):
    """
    Run the agent and return a response based on the state.
    Handles both initial requests and resuming after approval.
    """
    agent = await get_agent()
    response = await agent.ainvoke(input_data, config)
    thread_id = config["configurable"]["thread_id"]
    
    # Check if interrupted for tool approval
    if "__interrupt__" in response:
        interrupts = response["__interrupt__"]
        interrupt_data = interrupts[0].value
        
        # Extract tool details
        tool_name = interrupt_data.get("awaiting", "unknown")
        tool_args = interrupt_data.get("args", {})
        assistant_response = f"I want to call the tool '{tool_name}' with arguments: {tool_args}"
        
        return GraphResponse(
            thread_id=thread_id,
            run_status="user_feedback",
            assistant_response=assistant_response
        )
    else:
        # Graph finished - extract final response
        assistant_response = response["messages"][-1].content
        
        return GraphResponse(
            thread_id=thread_id,
            run_status="finished",
            assistant_response=assistant_response
        )


@router.post("/mcp/start", response_model=GraphResponse)
async def start_mcp_agent(request: StartRequest):
    """
    Start a new MCP agent conversation.
    """
    thread_id = str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    input_data = {"messages": [HumanMessage(content=request.human_request)]}
    
    return await run_agent_and_response(input_data, config)


@router.post("/mcp/approve", response_model=GraphResponse)
async def approve_mcp_tool(request: ApproveRequest):
    """
    Approve or reject a tool execution and continue the agent.
    """
    config = {"configurable": {"thread_id": request.thread_id}}
    decision = {"approved": request.approve_action == "approved"}
    input_data = Command(resume=decision)
    
    return await run_agent_and_response(input_data, config)
