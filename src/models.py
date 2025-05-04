from pydantic import BaseModel

class PromptModel(BaseModel):
    user_prompt: str

class AgentOutputModel(BaseModel):
    agent_response: str

class FinalOutputModel(BaseModel):
    enhanced_document: str