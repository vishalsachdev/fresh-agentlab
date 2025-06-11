from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class IdeaRequest(BaseModel):
    prompt: str
    num_ideas: int = 5
    context: Optional[Dict[str, Any]] = None

class IdeaResponse(BaseModel):
    ideas: List[Dict[str, Any]]
    session_id: str
    timestamp: datetime = datetime.now()

class ValidationRequest(BaseModel):
    idea: Dict[str, Any]
    session_id: str
    validation_criteria: Optional[List[str]] = None

class ValidationResponse(BaseModel):
    validation_score: float
    market_analysis: Dict[str, Any]
    competitive_analysis: Dict[str, Any]
    feasibility_assessment: Dict[str, Any]
    recommendations: List[str]

class PRDRequest(BaseModel):
    idea: Dict[str, Any]
    validation_data: Dict[str, Any]
    session_id: str
    requirements_focus: Optional[List[str]] = None

class PRDResponse(BaseModel):
    prd_document: Dict[str, Any]
    executive_summary: str
    technical_requirements: List[str]
    business_requirements: List[str]
    timeline: Dict[str, Any]

class AgentStatus(BaseModel):
    agent_id: str
    status: str
    current_task: Optional[str] = None
    performance_metrics: Dict[str, Any]
    last_activity: datetime

class SessionState(BaseModel):
    session_id: str
    created_at: datetime
    last_updated: datetime
    ideas_generated: List[Dict[str, Any]]
    validations_completed: List[Dict[str, Any]]
    prds_created: List[Dict[str, Any]]
    agent_interactions: List[Dict[str, Any]]