import logging # <-- Import logging
from crewai import Agent
from app.models.prompt import PromptRequest
from app.models.response import TopicAnalysisResult # Assuming TopicAnalysisResult is in app.models.response
from app.services.lmstudio import LMStudioService
from typing import Dict, Any, Optional # Import Optional
from datetime import datetime
import json

# Configure logger for this module
logger = logging.getLogger(__name__)
# You might want to set a specific level for this logger if needed,
# or rely on the basicConfig level set in run.py or main.py
# logger.setLevel(logging.INFO)


class TopicAnalysisAgent:
    """Agent responsible for analyzing the core topics of a prompt"""

    def __init__(self, config: Dict[str, Any], lmstudio_service: LMStudioService, llm: Any): # Add llm parameter
        self.lmstudio_service = lmstudio_service
        self.agent = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            verbose=config.get("verbose", False), # Use .get for safer access with default
            allow_delegation=config.get("allow_delegation", False), # Use .get for safer access with default
            # Add other agent config parameters here if needed, using .get
            max_iter=config.get("max_iter", 15),
            max_rpm=config.get("max_rpm", 100),
            llm=llm # Pass the llm instance to the CrewAI Agent
        )
        # You might want to store the last result here if needed elsewhere
        self.last_result: Optional[TopicAnalysisResult] = None


    def process(self, prompt_request: PromptRequest) -> TopicAnalysisResult:
        """Process the input prompt and extract core topics"""
        logger.info(f"Processing prompt for topic analysis: {prompt_request.content[:50]}...")
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
        # In a real application, you'd add error handling around this service call
        try:
            response = self.lmstudio_service.generate_completion(analysis_prompt)
            logger.info(f"Received response from LMStudio (first 50 chars): {response[:50]}...")
        except Exception as e:
            logger.error(f"Error calling LMStudio service: {e}")
            # Return an error result if the service call fails
            return TopicAnalysisResult(
                status="error",
                processing_time=0.0, # Set to 0 or calculate time before error
                core_topics=["error"],
                domain_classification="unknown",
                complexity_level=1,
                key_entities=[],
                timestamp=datetime.now(),
                message=f"Failed to get response from LMStudio: {e}"
            )


        # Parse response and create result object
        try:
            analysis_data = json.loads(response)
            result = TopicAnalysisResult(
                status="success",
                processing_time=0.5,  # TODO: Replace with actual timing
                core_topics=analysis_data.get("core_topics", []), # Use .get for safer access
                domain_classification=analysis_data.get("domain_classification", "unknown"), # Use .get
                complexity_level=analysis_data.get("complexity_level", 1), # Use .get
                key_entities=analysis_data.get("key_entities", []), # Use .get
                timestamp=datetime.now()
            )
            logger.info("Successfully parsed LMStudio response.")
        except json.JSONDecodeError:
            # Handle invalid JSON response from LMStudio
            logger.error(f"LMStudio returned invalid JSON: {response}") # Log the invalid response
            result = TopicAnalysisResult(
                status="error",
                processing_time=0.5, # TODO: Replace with actual timing
                core_topics=["error"],
                domain_classification="unknown",
                complexity_level=1,
                key_entities=[],
                timestamp=datetime.now(),
                message="Failed to parse LMStudio response as JSON."
            )
        except KeyError as e:
             # Handle missing keys if LMStudio returns valid JSON but misses expected fields
             logger.error(f"LMStudio response missing expected key: {e}. Response: {response}")
             result = TopicAnalysisResult(
                status="error",
                processing_time=0.5, # TODO: Replace with actual timing
                core_topics=["error"],
                domain_classification="unknown",
                complexity_level=1,
                key_entities=[],
                timestamp=datetime.now(),
                message=f"LMStudio response missing expected key: {e}"
            )
        except Exception as e:
             # Catch any other unexpected errors during processing
             logger.error(f"An unexpected error occurred during topic analysis processing: {e}")
             result = TopicAnalysisResult(
                status="error",
                processing_time=0.5, # TODO: Replace with actual timing
                core_topics=["error"],
                domain_classification="unknown",
                complexity_level=1,
                key_entities=[],
                timestamp=datetime.now(),
                message=f"An unexpected error occurred: {e}"
            )

        self.last_result = result # Store the result if needed
        logger.info(f"Topic analysis process finished with status: {result.status}")
        return result

# You would add other agent classes here if they are in the same file
# class CategoryBreakdownAgent:
#     ...
