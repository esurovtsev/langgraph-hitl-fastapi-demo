from pydantic import BaseModel
from typing import Optional
from typing import Literal
from typing import Literal

# --- Start Graph Run ---
class StartRequest(BaseModel):
    human_request: str

# --- Resume Paused Graph Run ---
class ResumeRequest(BaseModel):
    thread_id: str
    review_action: Literal["approved", "feedback"]
    human_comment: Optional[str] = None

# --- Minimal API Response ---
class GraphResponse(BaseModel):
    thread_id: str
    run_status: Literal["finished", "user_feedback", "pending"]
    assistant_response: Optional[str] = None

class ApproveRequest(BaseModel):
    thread_id: str
    approve_action: Literal["approved", "rejected"]