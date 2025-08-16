"""Pydantic models for strict inter-agent communication contracts."""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

class TaskType(str, Enum):
    """Types of tasks agents can handle"""
    DECOMPOSITION = "decomposition"
    PROPOSAL = "proposal"
    VERIFICATION = "verification"
    VALIDATION = "validation"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"

class ProposalContent(BaseModel):
    """Standardized proposal content structure"""
    claim_id: str = Field(..., description="Unique identifier for the claim")
    content: str = Field(..., min_length=10, description="Main proposal content")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    reasoning: Optional[str] = Field(None, description="Reasoning behind the proposal")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    agent_id: Optional[str] = Field(None, description="ID of the proposing agent")
    
    @validator('content')
    def content_must_be_non_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()
    
    @validator('confidence')
    def confidence_bounds(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v

class ValidationInput(BaseModel):
    """Input for validation agents"""
    content: str = Field(..., min_length=1, description="Content to validate")
    context: Optional[str] = Field(None, description="Additional context for validation")
    validation_type: str = Field("general", description="Type of validation requested")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('content')
    def content_must_be_string(cls, v):
        if not isinstance(v, str):
            raise ValueError('Content must be a string')
        return v.strip()

class ValidationResult(BaseModel):
    """Result from validation agents"""
    validation_result: str = Field(..., description="Overall validation result")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in validation")
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall validation score")
    issues: List[str] = Field(default_factory=list, description="Issues found during validation")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")
    aspect_scores: Dict[str, float] = Field(default_factory=dict, description="Scores for specific validation aspects")
    summary: str = Field(..., description="Summary of validation results")
    checker_type: str = Field(..., description="Type of checker that performed validation")
    execution_time: float = Field(default=0.0, description="Time taken for validation")

class AgentTask(BaseModel):
    """Standardized task structure for agents"""
    task_type: TaskType = Field(..., description="Type of task")
    description: str = Field(..., min_length=1, description="Task description")
    content: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Task content")
    context: Dict[str, Any] = Field(default_factory=dict, description="Task context")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Task metadata")
    
    @validator('description')
    def description_must_be_non_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()

class AgentResponse(BaseModel):
    """Standardized response structure from agents"""
    agent_id: str = Field(..., description="ID of the responding agent")
    agent_role: str = Field(..., description="Role of the responding agent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in response")
    content: str = Field(..., description="Main response content")
    reasoning: Optional[str] = Field(None, description="Reasoning behind the response")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    @validator('confidence')
    def confidence_bounds(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v

def prepare_validation_input(proposal_data: Any) -> str:
    """Extract the actual content for validation from various input types"""
    if isinstance(proposal_data, str):
        return proposal_data
    
    if isinstance(proposal_data, dict):
        # Handle different proposal structures
        content_fields = ['content', 'proposal', 'analysis', 'response', 'description']
        
        for field in content_fields:
            if field in proposal_data and proposal_data[field]:
                content = proposal_data[field]
                if isinstance(content, str):
                    return content.strip()
                elif isinstance(content, dict):
                    # Try to extract from nested structure
                    for nested_field in content_fields:
                        if nested_field in content and isinstance(content[nested_field], str):
                            return content[nested_field].strip()
        
        # If no content field found, try to convert the whole thing to string
        if 'type' in proposal_data and proposal_data['type'] == 'verification':
            # This is a verification task, extract from the proposal field
            if 'proposal' in proposal_data and isinstance(proposal_data['proposal'], dict):
                nested_proposal = proposal_data['proposal']
                for field in content_fields:
                    if field in nested_proposal and isinstance(nested_proposal[field], str):
                        return nested_proposal[field].strip()
        
        # Last resort: convert to string representation
        return str(proposal_data)
    
    # Final fallback
    return str(proposal_data)

def create_validation_task(proposal: Dict[str, Any]) -> AgentTask:
    """Create a properly structured validation task from a proposal"""
    content = prepare_validation_input(proposal)
    
    return AgentTask(
        task_type=TaskType.VERIFICATION,
        description=f"Validate proposal content: {content[:100]}...",
        content=content,
        context={
            "original_proposal": proposal,
            "validation_required": True
        },
        metadata={
            "proposal_id": proposal.get("subclaim_id", "unknown"),
            "agent_id": proposal.get("agent_id", "unknown"),
            "confidence": proposal.get("confidence", 0.5)
        }
    )