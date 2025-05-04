from .base import BaseRequest, BaseResponse
from typing import List, Dict, Any, Optional
from pydantic import Field

class PromptRequest(BaseRequest):
    """Initial prompt request from user"""
    content: str = Field(..., min_length=10)
    context: Optional[Dict[str, Any]] = None
    
class TopicAnalysisResult(BaseResponse):
    """Result from Topic Analysis Agent"""
    core_topics: List[str]
    domain_classification: str
    complexity_level: int = Field(1, ge=1, le=10)
    key_entities: List[str]
    
# Create similar models for other agent outputs