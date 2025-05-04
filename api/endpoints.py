from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.orchestrator.main import Orchestrator

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str

# Initialize the Orchestrator class
orchestrator = Orchestrator()

@app.post("/submit-prompt")
async def submit_prompt(request: PromptRequest):
    try:
        orchestrator.initiate_orchestration(request.prompt)
        return {"message": "Orchestration initiated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/processing-status")
async def processing_status():
    try:
        status = orchestrator.get_processing_status()
        return {"status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))