from crewai import Agent
from app.models.prompt import PromptRequest, TopicAnalysisResult
from app.services.lmstudio import LMStudioService
from typing import Dict, Any

class TopicAnalysisAgent:
    """Agent responsible for analyzing the core topics of a prompt"""
    
    def __init__(self, config: Dict[str, Any], lmstudio_service: LMStudioService):
        self.lmstudio_service = lmstudio_service
        self.agent = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            verbose=config["verbose"],
            allow_delegation=config["allow_delegation"]
        )
        
    def process(self, prompt_request: PromptRequest) -> TopicAnalysisResult:
        """Process the input prompt and extract core topics"""
        # Construct prompt for LMStudio
        analysis_prompt = f"""
        Analyze the following prompt and identify:
        1. Core topics (list 3-5 main subjects)
        2. Domain classification (e.g., technology, science, arts, business)
        3. Complexity level (1-10, where 10 is most complex)
        4. Key entities (people, organizations, products, concepts)
        
        Prompt to analyze: {prompt_request.content}
        
        Format your response as a JSON object with keys: core_topics, domain_classification, complexity_level, key_entities.
        """
        
        # Get analysis from LMStudio
        response = self.lmstudio_service.generate_completion(analysis_prompt)
        
        # Parse response and create result object
        # In a real implementation, add proper error handling and response parsing
        import json
        try:
            analysis_data = json.loads(response)
            return TopicAnalysisResult(
                status="success",
                processing_time=0.5,  # Replace with actual timing
                core_topics=analysis_data["core_topics"],
                domain_classification=analysis_data["domain_classification"],
                complexity_level=analysis_data["complexity_level"],
                key_entities=analysis_data["key_entities"],
                timestamp=datetime.now()
            )
        except json.JSONDecodeError:
            # Handle invalid JSON response
            return TopicAnalysisResult(
                status="error",
                processing_time=0.5,
                core_topics=["error"],
                domain_classification="unknown",
                complexity_level=1,
                key_entities=[],
                timestamp=datetime.now()
            )