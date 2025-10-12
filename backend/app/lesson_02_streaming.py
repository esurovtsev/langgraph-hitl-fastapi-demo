# Lesson 2: Advanced Streaming API with Server-Sent Events (SSE)
# Real-time streaming of LangGraph outputs using SSE

from fastapi import APIRouter, Request
from uuid import uuid4
from app.models import StartRequest, GraphResponse, ResumeRequest
from app.graph import graph
from sse_starlette.sse import EventSourceResponse
import json

router = APIRouter()

# In-memory storage for run configurations
run_configs = {}

@router.post("/graph/stream/create", response_model=GraphResponse)
def create_graph_streaming(request: StartRequest):
    thread_id = str(uuid4())
    
    run_configs[thread_id] = {
        "type": "start",
        "human_request": request.human_request
    }
    
    return GraphResponse(
        thread_id=thread_id,
        run_status="pending", 
        assistant_response=None
    )

@router.post("/graph/stream/resume", response_model=GraphResponse)
def resume_graph_streaming(request: ResumeRequest):
    thread_id = request.thread_id
    
    run_configs[thread_id] = {
        "type": "resume",
        "review_action": request.review_action,
        "human_comment": request.human_comment
    }
    
    return GraphResponse(
        thread_id=thread_id,
        run_status="pending",
        assistant_response=None
    )

@router.get("/graph/stream/{thread_id}")
async def stream_graph(request: Request, thread_id: str):
    # Check if thread_id exists in our configurations
    if thread_id not in run_configs:
        return {"error": "Thread ID not found. You must first call /graph/stream/create or /graph/stream/resume"}
    
    # Get the stored configuration
    run_data = run_configs[thread_id]
    config = {"configurable": {"thread_id": thread_id}}
    
    input_state = None
    if run_data["type"] == "start":
        event_type = "start"
        input_state = {"human_request": run_data["human_request"]}
    else:
        event_type = "resume"

        state_update = {"status": run_data["review_action"]}
        if run_data["human_comment"] is not None:
            state_update["human_comment"] = run_data["human_comment"]
        
        graph.update_state(config, state_update)
        # For resume operations, we pass None as the input state
        # input_state is already None
    
    async def event_generator():       
        # Initial event with thread_id
        initial_data = json.dumps({"thread_id": thread_id})
        print(f"DEBUG: Sending initial {event_type} event with data: {initial_data}")

        yield {"event": event_type, "data": initial_data}
        
        try:
            print(f"DEBUG: Starting to stream graph messages for thread_id={thread_id}")
            for msg, metadata in graph.stream(input_state, config, stream_mode="messages"):
                if await request.is_disconnected():
                    print("DEBUG: Client disconnected, breaking stream loop")
                    break
                    
                if metadata.get('langgraph_node') in ['assistant_draft', 'assistant_finalize']:
                    token_data = json.dumps({"content": msg.content})
                    print(f"DEBUG: Sending token event with data: {token_data[:30]}...")
                    yield {"event": "token", "data": token_data}
            
            # After streaming completes, check if human feedback is needed
            state = graph.get_state(config)
            if state.next and 'human_feedback' in state.next:
                status_data = json.dumps({"status": "user_feedback"})
                print(f"DEBUG: Sending status event (feedback): {status_data}")
                yield {"event": "status", "data": status_data}
            else:
                status_data = json.dumps({"status": "finished"})
                print(f"DEBUG: Sending status event (finished): {status_data}")
                yield {"event": "status", "data": status_data}
                
            # Clean up the thread configuration after streaming is complete
            if thread_id in run_configs:
                print(f"DEBUG: Cleaning up thread_id={thread_id} from run_configs")
                del run_configs[thread_id]
                
        except Exception as e:
            print(f"DEBUG: Exception in event_generator: {str(e)}")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
            
            # Clean up on error as well
            if thread_id in run_configs:
                print(f"DEBUG: Cleaning up thread_id={thread_id} from run_configs after error")
                del run_configs[thread_id]
    
    return EventSourceResponse(event_generator())
