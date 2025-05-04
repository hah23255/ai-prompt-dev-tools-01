from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class BaseResponse(BaseModel):
    """Base response model for all agents"""
    status: str = "success"
    processing_time: float
    timestamp: datetime = Field(default_factory=datetime.now)
    
class BaseRequest(BaseModel):
    """Base request model for all agents"""
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.now)