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

# Define the CategoryAnalysisResult model
class CategoryAnalysisResult(BaseResponse):
    """Response model for the Category Breakdown Agent"""
    categories: List[str] = Field(..., description="List of categories or sub-topics identified")
    analysis_details: str = Field(..., description="Details of the category analysis process")
    # Add any other fields specific to category breakdown results

# Define the IterativeRefinementResult model
class IterativeRefinementResult(BaseResponse):
    """Response model for the Iterative Refinement Agent"""
    refined_prompt: str = Field(..., description="The refined version of the prompt")
    refinement_details: str = Field(..., description="Details of the refinement process")
    # Add any other fields specific to iterative refinement results

# Define the ResearchIntegrationResult model
class ResearchIntegrationResult(BaseResponse):
    """Response model for the Research Integration Agent"""
    integrated_output: str = Field(..., description="The prompt or output after integrating research findings")
    integration_details: str = Field(..., description="Details of the research integration process")
    # Add any other fields specific to research integration results

# Define the final EnhancedPromptResponse model
class EnhancedPromptResponse(BaseResponse):
    """Final response model for the enhanced prompt API"""
    enhanced_prompt: str = Field(..., description="The final enhanced prompt string")
    processing_details: Dict[str, Any] = Field(..., description="Details about each processing stage")
    # Add any other top-level fields for the final response
