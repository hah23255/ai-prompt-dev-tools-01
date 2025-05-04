from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# Assuming you want a base response model
class BaseResponse(BaseModel):
    """Base response model for all API responses"""
    status: str = Field(..., description="Status of the operation (e.g., 'success', 'error')")
    processing_time: float = Field(..., description="Time taken for processing in seconds")
    timestamp: datetime = Field(..., description="Timestamp of the response")
    # You might add a message field for errors or general info
    message: Optional[str] = Field(None, description="Optional message related to the response")

class TopicAnalysisResult(BaseResponse):
    """Response model for the Topic Analysis Agent"""
    core_topics: List[str] = Field(..., description="List of core topics identified in the prompt")
    domain_classification: str = Field(..., description="Classification of the prompt's domain")
    complexity_level: int = Field(..., description="Complexity level of the prompt (1-10)")
    key_entities: List[str] = Field(..., description="List of key entities mentioned in the prompt")
    # Add any other fields specific to topic analysis results

# You would add other response models here as needed for other agents/tasks
# class CategoryBreakdownResult(BaseResponse):
#     ...

# class IterativeRefinementResult(BaseResponse):
#     ...

# class ResearchIntegrationResult(BaseResponse):
#     ...

# class EnhancedPromptResponse(BaseResponse):
#     """Final response model for the enhanced prompt API"""
#     enhanced_prompt: str = Field(..., description="The final enhanced prompt")
#     processing_details: Dict[str, Any] = Field(..., description="Details about each processing stage")
