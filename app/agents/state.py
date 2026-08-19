from typing import Annotated, Any, Dict, List, Optional, Sequence, TypedDict
import operator
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    Central State schema passed through the LangGraph StateGraph.
    """
    # Conversation and message history
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # High level goal and current subtask
    task_id: str
    goal: str
    requester_role: str
    
    # Routing & Execution
    next_step: Optional[str]
    current_agent: Optional[str]
    completed_steps: Annotated[List[Dict[str, Any]], operator.add]
    
    # Generated artifacts (e.g. invoice drafts, emails, reports)
    artifacts: Annotated[Dict[str, Any], operator.or_]
    
    # Approval staging
    requires_approval: bool
    pending_approval_id: Optional[str]
    approval_type: Optional[str]
    approval_payload: Optional[Dict[str, Any]]
    
    # Evaluation & final summary
    summary: Optional[str]
    status: str
