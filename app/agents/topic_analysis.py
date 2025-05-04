import logging
# Corrected import: Import BaseTool for subclassing
from crewai import Agent
from crewai.tools import BaseTool # Import BaseTool

from app.models.prompt import PromptRequest
from app.models.response import TopicAnalysisResult
from app.services.lmstudio import LMStudioService
from typing import Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Define the custom tool by subclassing BaseTool
class TopicAnalysisTool(BaseTool):
    """Tool for analyzing the core topics of a prompt using LMStudio."""

    name: str = "Topic Analysis Tool"
    description: str = (
        "Analyzes a given text prompt to identify core topics, domain, complexity, and key entities, "
        "returning the result as a JSON object. Input should be the text prompt string."
    )
    # Add service and llm as attributes that will be passed during instantiation
    lmstudio_service: LMStudioService
    llm: Any # Or a more specific type if available

    def _run(self, prompt_content: str) -> str:
        """
        Runs the topic analysis logic by prompting LMStudio.
        This method is called by the CrewAI agent when the tool is used.
        """
        logger.info(f"Executing Topic Analysis Tool for prompt: {prompt_content[:50]}...")

        # Construct prompt for LMStudio
        analysis_prompt = f"""
Analyze the following prompt and identify:
1. Core topics (list 3-5 main subjects)
2. Domain classification (e.g., technology, science, arts, business)
3. Complexity level (1-10, where 10 is most complex)
4. Key entities (people, organizations, products, concepts)

Prompt to analyze: {prompt_content}

Format your response as a JSON object with keys: core_topics, domain_classification, complexity_level, key_entities.
Ensure the output is valid JSON and contains only the JSON object.
"""

        try:
            # Use the LMStudio service instance passed to the tool
            response = self.lmstudio_service.generate_completion(analysis_prompt)
            logger.info(f"Received response from LMStudio (first 50 chars): {response[:50]}...")

            # Attempt to parse the response to ensure it's valid JSON before returning
            try:
                # Clean up potential extra text before/after JSON from LLM
                # Find the first '{' and last '}' to extract the JSON string
                json_start = response.find('{')
                json_end = response.rfind('}')
                if json_start != -1 and json_end != -1 and json_end > json_start:
                    json_string = response[json_start : json_end + 1]
                    json.loads(json_string) # Validate JSON
                    return json_string # Return the cleaned JSON string
                else:
                     logger.error(f"LMStudio response does not contain a valid JSON object: {response}")
                     return json.dumps({"status": "error", "message": "Tool received response without valid JSON object structure", "raw_response": response})

            except json.JSONDecodeError:
                logger.error(f"LMStudio returned invalid JSON from tool: {response}")
                # Return an error indicator or formatted message if JSON is invalid
                return json.dumps({"status": "error", "message": "Tool received invalid JSON from LLM", "raw_response": response})

        except Exception as e:
            logger.error(f"Error calling LMStudio service from tool: {e}")
            # Return an error message in a consistent format
            return json.dumps({"status": "error", "message": f"Tool execution failed: {e}"})


class TopicAnalysisAgent:
    """Agent responsible for analyzing the core topics of a prompt"""

    def __init__(self, config: Dict[str, Any], lmstudio_service: LMStudioService, llm: Any):
        self.lmstudio_service = lmstudio_service
        self.llm = llm # Store llm
        self.config = config # Store config if needed later

        # Instantiate the custom tool, passing necessary dependencies
        self.topic_analysis_tool = TopicAnalysisTool(
            lmstudio_service=self.lmstudio_service,
            llm=self.llm # Pass the llm to the tool if needed within _run
        )

        self.agent = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            verbose=config.get("verbose", False),
            allow_delegation=config.get("allow_delegation", False),
            max_iter=config.get("max_iter", 15),
            max_rpm=config.get("max_rpm", 100),
            llm=self.llm, # Assign the llm to the CrewAI Agent
            tools=[self.topic_analysis_tool] # Assign the instantiated tool to the agent
        )

        self.last_result: Optional[TopicAnalysisResult] = None

    # The original process method is no longer the primary way the task interacts.
    # The task will instruct the agent to use the TopicAnalysisTool, which calls TopicAnalysisTool._run().
    # You can remove this method if it's not needed elsewhere outside the CrewAI flow.
    def process(self, prompt_request: PromptRequest) -> TopicAnalysisResult:
         """Process the input prompt and extract core topics (now handled by the tool)."""
         logger.warning("TopicAnalysisAgent.process called directly. CrewAI task uses the TopicAnalysisTool.")
         # If you still need a way to trigger the analysis directly and get a TopicAnalysisResult,
         # you could call the tool's _run method and then parse the JSON string it returns
         # into a TopicAnalysisResult object here.
         tool_output_json_string = self.topic_analysis_tool._run(prompt_request.content)
         try:
             analysis_data = json.loads(tool_output_json_string)
             # Create and return TopicAnalysisResult from analysis_data
             result = TopicAnalysisResult(
                 status="success", # Assuming tool_output_json_string represents success
                 processing_time=0.0, # Placeholder
                 core_topics=analysis_data.get("core_topics", []),
                 domain_classification=analysis_data.get("domain_classification", "unknown"),
                 complexity_level=analysis_data.get("complexity_level", 1),
                 key_entities=analysis_data.get("key_entities", []),
                 timestamp=datetime.now()
             )
             self.last_result = result
             return result
         except Exception as e:
             logger.error(f"Failed to parse tool output into TopicAnalysisResult: {e}")
             # Return an error result
             return TopicAnalysisResult(
                 status="error",
                 processing_time=0.0,
                 core_topics=["error"],
                 domain_classification="unknown",
                 complexity_level=1,
                 key_entities=[],
                 timestamp=datetime.now(),
                 message=f"Failed to parse tool output: {e}"
             )


