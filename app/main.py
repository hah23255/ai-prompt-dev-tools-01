import os
import time
import uuid
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from typing import Dict, List, Any

from app.models.prompt import PromptRequest
from app.orchestrator.crew import PromptEnhancerCrew

# Initialize FastAPI app
app = FastAPI(
    title="AI-Driven Prompt Enhancer API",
    description="API for enhancing user prompts using specialized AI agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize CrewAI orchestrator
prompt_enhancer = PromptEnhancerCrew()

# WebSocket connections
active_connections: List[WebSocket] = []

@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Serve the home page"""
    with open("app/static/index.html", "r") as f:
        return f.read()

@app.post("/api/enhance-prompt")
async def enhance_prompt(prompt_data: Dict[str, Any]):
    """Enhance a prompt using the AI system"""
    try:
        # Create a PromptRequest from the input data
        request_id = str(uuid.uuid4())
        prompt_request = PromptRequest(
            request_id=request_id,
            content=prompt_data.get("prompt", ""),
            context=prompt_data.get("context", {})
        )
        
        # Process the prompt using CrewAI
        start_time = time.time()
        result = prompt_enhancer.enhance_prompt(prompt_request)
        processing_time = time.time() - start_time
        
        # Return the enhanced prompt
        return {
            "request_id": request_id,
            "status": "success",
            "processing_time": processing_time,
            "enhanced_prompt": result["enhanced_prompt"],
            "processing_details": result["processing_details"]
        }
    except ValidationError as e:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid request data", "details": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Internal server error", "details": str(e)}
        )

@app.websocket("/ws/enhance-prompt")
async def websocket_enhance_prompt(websocket: WebSocket):
    """WebSocket endpoint for real-time prompt enhancement updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Receive prompt data
            data = await websocket.receive_json()
            
            try:
                # Create a PromptRequest
                request_id = str(uuid.uuid4())
                prompt_request = PromptRequest(
                    request_id=request_id,
                    content=data.get("prompt", ""),
                    context=data.get("context", {})
                )
                
                # Send status updates for each stage
                await websocket.send_json({
                    "status": "processing",
                    "stage": "topic_analysis",
                    "message": "Analyzing prompt topics..."
                })
                
                # Process with CrewAI (this would be modified to provide real-time updates)
                result = prompt_enhancer.enhance_prompt(prompt_request)
                
                # Send the final result
                await websocket.send_json({
                    "status": "complete",
                    "request_id": request_id,
                    "enhanced_prompt": result["enhanced_prompt"],
                    "processing_details": result["processing_details"]
                })
                
            except ValidationError as e:
                await websocket.send_json({
                    "status": "error",
                    "message": "Invalid request data",
                    "details": str(e)
                })
            except Exception as e:
                await websocket.send_json({
                    "status": "error",
                    "message": "Internal server error",
                    "details": str(e)
                })
                
    except WebSocketDisconnect:
        active_connections.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)