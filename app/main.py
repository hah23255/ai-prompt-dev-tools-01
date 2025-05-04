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

from app.orchestrator.crew import PromptEnhancerCrew

# Configure logger for this module
logger = logging.getLogger(__name__)

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
        # The enhance_prompt method in crew.py now calls crew.kickoff
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
        # Log the error before returning
        logging.error(f"Error during prompt enhancement via HTTP: {e}", exc_info=True)
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
                    context=data.get("context", {}) # Include context from WebSocket data
                )

                # Send initial processing status
                await websocket.send_json({
                    "status": "processing",
                    "stage": "initial", # Use a general initial stage or the first agent's name
                    "message": "Starting prompt enhancement process..."
                })

                # Process with CrewAI
                # The enhance_prompt method in crew.py now calls crew.kickoff
                result = prompt_enhancer.enhance_prompt(prompt_request)

                # Send the final result
                await websocket.send_json({
                    "status": "complete",
                    "request_id": request_id,
                    "enhanced_prompt": result["enhanced_prompt"],
                    "processing_details": result["processing_details"]
                })

            except ValidationError as e:
                logging.error(f"Validation Error during WebSocket prompt enhancement: {e}", exc_info=True)
                await websocket.send_json({
                    "status": "error",
                    "message": "Invalid request data",
                    "details": str(e)
                })
            except Exception as e:
                # Log the error before sending over WebSocket
                logging.error(f"Error during prompt enhancement via WebSocket: {e}", exc_info=True)
                await websocket.send_json({
                    "status": "error",
                    "message": "Internal server error during processing",
                    "details": str(e)
                })

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected.")
        active_connections.remove(websocket)
    except Exception as e:
         # Catch any other exceptions during WebSocket handling
         logger.error(f"Unexpected error in WebSocket handler: {e}", exc_info=True)
         # Attempt to send an error message before closing
         try:
             await websocket.send_json({
                 "status": "error",
                 "message": "An unexpected server error occurred.",
                 "details": str(e)
             })
         except Exception:
             pass # Ignore if sending fails during cleanup
         finally:
             if websocket in active_connections:
                 active_connections.remove(websocket)


if __name__ == "__main__":
    import uvicorn
    # Configure basic logging for uvicorn and the application
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
