from typing import Literal, Optional
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver

# --- Model Definition ---
# OpenAI API key configured in .env file
model = ChatOpenAI(model="gpt-4o-mini")


# --- Graph State Definition ---
class DraftReviewState(MessagesState):
    human_request: str
    human_comment: Optional[str]
    status: Literal["approved", "feedback"]
    assistant_response: str


# --- Graph Nodes Definition ---
def assistant_draft(state: DraftReviewState) -> DraftReviewState:
    user_message = HumanMessage(content=state["human_request"])
    status = state.get("status", "approved")

    if (status == "feedback" and state.get("human_comment")):
        # Create a system message that incorporates the feedback as instructions
        # rather than passing the feedback as a separate human message
        system_message = SystemMessage(content=(f"""
        You are an AI assistant revising your previous draft. 
        
        FEEDBACK FROM HUMAN: "{state["human_comment"]}"
        
        Carefully incorporate this feedback into your response. Address all comments, 
        corrections, or suggestions. Ensure your revised response fully integrates 
        the feedback, improves clarity, and resolves any issues raised.
        
        DO NOT repeat the feedback verbatim in your response.
        """))

        # Only include the original messages and system message with embedded feedback
        messages = [user_message] + state["messages"] + [system_message]
        
        # Don't add the human comment to the message history
        all_messages = state["messages"]

    else:
        system_message = SystemMessage(content=("""
        You are an AI assistant. Your goal is to fully understand and fulfill the user's 
        request by preparing a relevant, clear, and helpful draft reply. Focus on addressing 
        the user's needs directly and comprehensively. 
        Do not reference any previous human feedback at this stage.
        """))
        messages = [system_message, user_message]
        all_messages = state["messages"]
    
    response = model.invoke(messages)

    all_messages = all_messages + [response]

    return {
        **state,
        "messages": all_messages,
        "assistant_response": response.content
    }


def human_feedback(state: DraftReviewState):
    pass


def assistant_finalize(state: DraftReviewState) -> DraftReviewState:
    # Get the most recent assistant response from the state
    latest_response = state["assistant_response"]
    
    system_message = SystemMessage(content="""
    You are an AI assistant. The user has approved your draft. Carefully 
    review your reply and make any final improvements to clarity, tone, and 
    completeness. Ensure the response is polished, professional, and ready 
    to be delivered as the final answer.
    
    DO NOT expand the response significantly or revert to earlier versions.
    Focus on polishing the MOST RECENT draft that was approved.
    """)
    
    # Create a focused message list with just the original request and latest response
    user_message = HumanMessage(content=state["human_request"])
    assistant_message = HumanMessage(content=f"My previous draft: {latest_response}")
    
    # Use a more focused set of messages for the finalize step
    messages = [system_message, user_message, assistant_message]
    response = model.invoke(messages)

    # Add the finalized response to the message history
    all_messages = state['messages'] + [response]

    return {
        **state,
        "messages": all_messages,
        "assistant_response": response.content
    }
    

# --- Router Function ---
def feedback_router(state: DraftReviewState) -> str:
    if state['status'] == 'approved':
        return 'assistant_finalize'
    else:
        return 'assistant_draft'

# --- Graph Construction ---
builder = StateGraph(DraftReviewState)

# builder.add_node('start', start_node)
builder.add_node('assistant_draft', assistant_draft)
builder.add_node('human_feedback', human_feedback)
builder.add_node('assistant_finalize', assistant_finalize)

builder.add_edge(START, 'assistant_draft')
builder.add_edge('assistant_draft', 'human_feedback')
builder.add_conditional_edges('human_feedback', feedback_router, {'assistant_finalize': 'assistant_finalize', 'assistant_draft': 'assistant_draft'})
builder.add_edge('assistant_finalize', END)

memory = MemorySaver()
graph = builder.compile(interrupt_before=["human_feedback"], checkpointer=memory)

# --- Exports ---
__all__ = ["graph", "DraftReviewState"]
