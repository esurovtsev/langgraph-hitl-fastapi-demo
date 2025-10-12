# Lesson 1: Basic Blocking API
# Traditional RESTful API with blocking request/response pattern

from fastapi import APIRouter
from uuid import uuid4
from app.models import StartRequest, GraphResponse, ResumeRequest
from app.graph import graph

router = APIRouter()


def run_graph_and_response(input_state, config):
    result = graph.invoke(input_state, config)
    state = graph.get_state(config)
    next_nodes = state.next
    thread_id = config["configurable"]["thread_id"]
    if next_nodes and "human_feedback" in next_nodes:
        run_status = "user_feedback"
    else:
        run_status = "finished"
    return GraphResponse(
        thread_id=thread_id,
        run_status=run_status,
        assistant_response=result["assistant_response"]
    )

@router.post("/graph/start", response_model=GraphResponse)
def start_graph(request: StartRequest):
    thread_id = str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {"human_request": request.human_request}

    return run_graph_and_response(initial_state, config)

@router.post("/graph/resume", response_model=GraphResponse)
def resume_graph(request: ResumeRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    state = {"status": request.review_action}
    if request.human_comment is not None:
        state["human_comment"] = request.human_comment
    print(f"State to update: {state}")
    graph.update_state(config, state)

    return run_graph_and_response(None, config)
