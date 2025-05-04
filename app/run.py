import os
import argparse
import logging
import uvicorn
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("prompt_enhancer.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("prompt_enhancer")

def check_lmstudio_running():
    """Check if LMStudio is running and accessible"""
    import requests
    try:
        response = requests.get("http://localhost:1234/api/v0/models")
        if response.status_code == 200:
            logger.info("LMStudio is running")
            return True
    except:
        pass
    
    logger.error("LMStudio is not running. Please start LMStudio server.")
    return False

def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description="AI-Driven Prompt Enhancer")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()
    
    # Check if LMStudio is running
    if not check_lmstudio_running():
        logger.info("Attempting to start LMStudio...")
        try:
            import subprocess
            subprocess.Popen(["lms", "server", "start"])
            logger.info("LMStudio server started")
        except:
            logger.error("Failed to start LMStudio automatically. Please start it manually.")
            return
    
    # Run FastAPI
    logger.info(f"Starting FastAPI server on {args.host}:{args.port}")
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.debug
    )

if __name__ == "__main__":
    main()