import lmstudio as lms
import os
import requests
from typing import Dict, Any, Optional

class LMStudioService:
    """Service for interacting with LMStudio local LLM"""
    
    def __init__(self, model_name: str = "llama-3-8b-instruct", api_base: str = "http://localhost:1234"):
        self.api_base = api_base
        self.model_name = model_name
        self.ensure_model_loaded()
        
    def ensure_model_loaded(self):
        """Ensure the model is loaded in LMStudio"""
        models_url = f"{self.api_base}/api/v0/models"
        models = requests.get(models_url).json()
        
        if not any(model["id"] == self.model_name for model in models["data"]):
            # Use LMStudio Python client to load model
            import subprocess
            subprocess.run(["lms", "load", self.model_name])
    
    def generate_completion(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate text completion using LMStudio"""
        try:
            model = lms.llm(self.model_name)
            result = model.respond(prompt, temperature=temperature)
            return result
        except Exception as e:
            print(f"Error in LMStudio completion: {e}")
            # Fallback to REST API if Python client fails
            response = requests.post(
                f"{self.api_base}/api/v0/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature
                }
            )
            return response.json()["choices"][0]["message"]["content"]