import os
import yaml
import logging
import json
from crewai import Agent
from crewai.tools import BaseTool # Import BaseTool
from crewai.project import CrewBase, agent, task, crew # Keep if needed for CrewBase context, but likely not in agent file
from typing import Dict, Any, List
from pathlib import Path
from pydantic import ValidationError, BaseModel, Field # Import BaseModel and Field
from app.services.lmstudio import LMStudioService, LMStudioLiteLLMWrapper

# Configure logger for this module
logger = logging.getLogger(__name__)

# Define the Pydantic model for the actual input data fields for the tool
class TopicAnalysisInputData(BaseModel):
    """Schema for the actual data fields within the tool's input."""
    text_to_analyze: str = Field(description="The text content to analyze for topics, domain, complexity, and key entities.")

# Define the Pydantic model that CrewBase seems to expect for args_schema
class TopicAnalysisToolInput(BaseModel):
    """Input schema for the TopicAnalysisTool, structured to satisfy CrewBase validation."""
    tool_input: TopicAnalysisInputData = Field(description="Container for the tool's input data.")

# Define the custom tool by subclassing BaseTool
class TopicAnalysisTool(BaseTool):
    """Tool for analyzing text to identify topics, domain, complexity, and key entities using LMStudio."""

    name: str = "Topic Analysis Tool"
    description: str = (
        "Analyzes input text to extract core topics, domain, complexity, and key entities. "
        "Input should be a JSON object with a single key 'tool_input', whose value is a JSON object "
        "with a 'text_to_analyze' key."
        "Example input JSON: {'tool_input': {'text_to_analyze': 'Text content here'}}"
    )
    # Define the input model for the tool, using the nested structure
    args_schema: type = TopicAnalysisToolInput

    # Add service and llm as attributes that will be passed during instantiation
    lmstudio_service: LMStudioService
    llm: Any # Or a more specific type if available

    def _run(self, tool_input: TopicAnalysisToolInput) -> str:
        """
        Runs the topic analysis logic by prompting LMStudio.
        This method is called by the CrewAI agent when the tool is used.
        Receives input as a TopicAnalysisToolInput instance with nested data.
        """
        logger.info(f"Executing Topic Analysis Tool...")
        # Access the actual input data from the nested 'tool_input' field
        input_data = tool_input.tool_input
        text_to_analyze = input_data.text_to_analyze
        logger.info(f"  Text to Analyze: {text_to_analyze[:100]}...")

        # Construct prompt for LMStudio
        analysis_prompt = f"""
Analyze the following text to identify its core topics, domain, complexity, and key entities.

Text to Analyze: {text_to_analyze}

Provide the output as a JSON object with the following keys:
- core_topics: A list of strings representing the main topics.
- domain: A string representing the subject area (e.g., 'technology', 'science', 'business').
- complexity: A string indicating the complexity ('low', 'medium', 'high').
- key_entities: A list of strings representing important names, places, or concepts.

Ensure the output is valid JSON and contains only the JSON object.
Example output: {{"core_topics": ["topic1", "topic2"], "domain": "example", "complexity": "medium", "key_entities": ["entityA", "entityB"]}}
"""

        try:
            # Use the LMStudio service instance passed to the tool
            # Assuming generate_completion exists and takes a prompt string
            response = self.lmstudio_service.generate_completion(analysis_prompt)
            logger.info(f"Received response from LMStudio (first 50 chars): {response[:50]}...")

            # Attempt to parse the response to ensure it's valid JSON before returning
            try:
                # Clean up potential extra text before/after JSON object from LLM
                # Find the first '{' and last '}' to extract the JSON string
                json_start = response.find('{')
                json_end = response.rfind('}')
                if json_start != -1 and json_end != -1 and json_end > json_start:
                    json_string = response[json_start : json_end + 1]
                    # Validate JSON is an object
                    parsed_json = json.loads(json_string)
                    if isinstance(parsed_json, dict):
                        # Optional: Validate keys in parsed_json if necessary
                        return json_string # Return the cleaned JSON object string
                    else:
                        logger.error(f"LMStudio returned valid JSON but not an object: {response}")
                        return json.dumps({"status": "error", "message": "Tool received valid JSON but not an object", "raw_response": response})
                else:
                     logger.error(f"LMStudio response does not contain a valid JSON object structure: {response}")
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
    """Agent responsible for analyzing the prompt topic."""

    def __init__(self, config: Dict[str, Any], lmstudio_service: LMStudioService, llm: Any):
        self.config = config
        self.lmstudio_service = lmstudio_service # Store the service instance
        self.llm = llm # Store llm

        # Instantiate the custom tool, passing necessary dependencies
        self.topic_analysis_tool = TopicAnalysisTool(
            lmstudio_service=self.lmstudio_service,
            llm=self.llm # Pass the llm to the tool if needed within _run
        )

        # Initialize the CrewAI Agent here using the config
        self.agent = Agent(
            role=config.get("role", "Topic Analysis Specialist"),
            goal=config.get("goal", "Analyze the user's prompt to identify core topics, domain, complexity, and key entities."),
            backstory=config.get("backstory", "An expert in dissecting complex queries into fundamental components."),
            verbose=config.get("verbose", False),
            allow_delegation=config.get("allow_delegation", False),
            max_iter=config.get("max_iter", 15),
            max_rpm=config.get("max_rpm", 100),
            llm=self.llm, # Pass the llm instance to the CrewAI Agent
            tools=[self.topic_analysis_tool] # Assign the instantiated tool to the agent
        )
        # self.last_result: Optional[Any] = None # Add a placeholder for result if needed

    # The process method is likely not needed if the task uses the tool directly.
    # Keeping it as a placeholder or for direct calls outside CrewAI flow if necessary.
    # Note: If you call this process method directly, you would need to construct
    # a TopicAnalysisToolInput object with the nested structure.
    # def process(self, inputs: TopicAnalysisToolInput) -> str:
    #     """Process the input using the agent's tool."""
    #     logger.warning("TopicAnalysisAgent.process called directly. CrewAI task uses the TopicAnalysisTool.")
    #     # Example: Call the tool's _run method if needed for direct processing
    #     tool_output_json_string = self.topic_analysis_tool._run(inputs) # Pass the inputs object
    #     return tool_output_json_string
