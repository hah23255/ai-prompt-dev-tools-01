from pydantic import BaseModel, Field, ValidationError # Ensure ValidationError is imported from pydantic
from typing import List, Dict, Any, Optional
from datetime import datetime

class BaseResponse(BaseModel):
    """Base response model for all agents - Corrected to make status and timestamp required"""
    # status is now required as it has no default value
    status: str = Field(..., description="Status of the operation (e.g., 'success', 'error')")
    # processing_time is required as it has no default value
    processing_time: float = Field(..., description="Time taken for processing in seconds")
    # timestamp is now required as it has no default value or factory
    timestamp: datetime = Field(..., description="Timestamp of the response")

class BaseRequest(BaseModel):
    """Base request model for all agents"""
    # request_id is required as it has no default value
    request_id: str = Field(..., description="Unique identifier for the request")
    # timestamp has a default factory, so it is optional
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the request")