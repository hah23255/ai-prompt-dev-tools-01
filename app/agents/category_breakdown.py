import logging
from crewai import Agent
from crewai.tools import BaseTool # Import BaseTool
# Assuming these models exist

from app.models.prompt import PromptRequest # Assuming PromptRequest might be needed for type hinting
from app.models.response import CategoryAnalysisResult # Assuming this model exists
from app.services.lmstudio import LMStudioService # Import LMStudioService
from typing import Dict, Any, Optional
from datetime import datetime
import json # Import json
from pydantic import BaseModel, Field # Import BaseModel and Field for Pydantic schema

logger = logging.getLogger(__name__)

# Define the Pydantic model for the actual input data fields
class CategoryBreakdownInputData(BaseModel):
    """Schema for the actual data fields within the tool's input."""
    prompt: str = Field(description="The original text prompt from the user.")
    topic_analysis: str = Field(description="The JSON string output from the Topic Analysis Tool.")

# Define the Pydantic model that CrewBase seems to expect for args_schema
# This model has a single field named 'tool_input'
class CategoryBreakdownToolInput(BaseModel):
    """Input schema for the CategoryBreakdownTool, structured to satisfy CrewBase validation."""
    # This 'tool_input' field is added to satisfy CrewBase's specific validation
    # The actual data the tool needs is nested within this field.
    tool_input: CategoryBreakdownInputData = Field(description="Container for the tool's input data.")


# Define the custom tool by subclassing BaseTool
class CategoryBreakdownTool(BaseTool):
    """Tool for breaking down a prompt into categories using LMStudio."""

    name: str = "Category Breakdown Tool"
    description: str = (
        "Analyzes a given text prompt and a topic analysis result to break down the prompt "
        "into distinct categories or sub-topics. Returns a JSON array of strings."
        "Input should be a JSON object with a single key 'tool_input', whose value is a JSON object "
        "with 'prompt' (original prompt string) and 'topic_analysis' (Topic Analysis JSON string) keys."
        "Example input JSON: {'tool_input': {'prompt': 'Original Prompt Here', 'topic_analysis': '{...Topic Analysis JSON...}'}"
    )
    # Define the input model for the tool, using the nested structure
    args_schema: type = CategoryBreakdownToolInput

    # Add service and llm as attributes that will be passed during instantiation
    lmstudio_service: LMStudioService
    llm: Any # Or a more specific type if available

    # The _run method now receives the validated CategoryBreakdownToolInput instance
    # Access the actual data from the nested 'tool_input' attribute
    def _run(self, tool_input: CategoryBreakdownToolInput) -> str:
        """
        Runs the category breakdown logic by prompting LMStudio.
        This method is called by the CrewAI agent when the tool is used.
        Receives input as a CategoryBreakdownToolInput instance with nested data.
        """
        logger.info(f"Executing Category Breakdown Tool...")
        # Access the actual input data from the nested 'tool_input' field
        input_data = tool_input.tool_input
        logger.info(f"  Prompt: {input_data.prompt[:100]}...")
        logger.info(f"  Topic Analysis: {input_data.topic_analysis[:100]}...")

        # The input is now validated and available via the input_data object
        prompt_content = input_data.prompt
        topic_analysis_result_str = input_data.topic_analysis

        # Construct prompt for LMStudio
        breakdown_prompt = f"""
Break down the following original prompt into distinct categories or sub-topics.
Consider the topic analysis provided.

Original Prompt: {prompt_content}

Topic Analysis: {topic_analysis_result_str}

List the categories as a JSON array of strings.
Example output: ["Category 1", "Category 2", "Sub-topic A"]
Ensure the output is valid JSON and contains only the JSON array.
"""

        try:
            # Use the LMStudio service instance passed to the tool
            response = self.lmstudio_service.generate_completion(breakdown_prompt)
            logger.info(f"Received response from LMStudio (first 50 chars): {response[:50]}...")

            # Attempt to parse the response to ensure it's valid JSON array before returning
            try:
                # Clean up potential extra text before/after JSON array from LLM
                # Find the first '[' and last ']' to extract the JSON string
                json_start = response.find('[')
                json_end = response.rfind(']')
                if json_start != -1 and json_end != -1 and json_end > json_start:
                    json_string = response[json_start : json_end + 1]
                    # Validate JSON is an array
                    parsed_json = json.loads(json_string)
                    if isinstance(parsed_json, list):
                        return json_string # Return the cleaned JSON array string
                    else:
                        logger.error(f"LMStudio returned valid JSON but not an array: {response}")
                        return json.dumps({"status": "error", "message": "Tool received valid JSON but not an array", "raw_response": response})
                else:
                     logger.error(f"LMStudio response does not contain a valid JSON array structure: {response}")
                     return json.dumps({"status": "error", "message": "Tool received response without valid JSON array structure", "raw_response": response})

            except json.JSONDecodeError:
                logger.error(f"LMStudio returned invalid JSON from tool: {response}")
                # Return an error indicator or formatted message if JSON is invalid
                return json.dumps({"status": "error", "message": "Tool received invalid JSON from LLM", "raw_response": response})

        except Exception as e:
            logger.error(f"Error calling LMStudio service from tool: {e}")
            # Return an error message in a consistent format
            return json.dumps({"status": "error", "message": f"Tool execution failed: {e}"})


class CategoryBreakdownAgent:
    """Agent responsible for breaking down a prompt into categories"""

    def __init__(self, config: Dict[str, Any], lmstudio_service: LMStudioService, llm: Any):
        self.config = config
        self.lmstudio_service = lmstudio_service # Store the service instance
        self.llm = llm # Store llm

        # Instantiate the custom tool, passing necessary dependencies
        self.category_breakdown_tool = CategoryBreakdownTool(
            lmstudio_service=self.lmstudio_service,
            llm=self.llm # Pass the llm to the tool if needed within _run
        )

        # Initialize the CrewAI Agent here using the config
        self.agent = Agent(
            role=config.get("role", "Category Breakdown Specialist"),
            goal=config.get("goal", "Break down the user prompt into distinct categories or sub-topics."),
            backstory=config.get("backstory", "An expert in information architecture..."),
            verbose=config.get("verbose", False),
            allow_delegation=config.get("allow_delegation", False),
            max_iter=config.get("max_iter", 15),
            max_rpm=config.get("max_rpm", 100),
            llm=self.llm, # Pass the llm instance to the CrewAI Agent
            tools=[self.category_breakdown_tool] # Assign the instantiated tool to the agent
        )
        self.last_result: Optional[CategoryAnalysisResult] = None

    # The process method is likely not needed if the task uses the tool directly.
    # Keeping it as a placeholder or for direct calls outside CrewAI flow if necessary.
    # Note: If you call this process method directly, you would need to construct
    # a CategoryBreakdownToolInput object with the nested structure.
    def process(self, inputs: CategoryBreakdownToolInput) -> CategoryAnalysisResult:
        """Process the input and break it down into categories (now handled by the tool)."""
        logger.warning("CategoryBreakdownAgent.process called directly. CrewAI task uses the CategoryBreakdownTool.")
        # Example: Call the tool's _run method if needed for direct processing
        tool_output_json_string = self.category_breakdown_tool._run(inputs) # Pass the inputs object
        try:
            # Assuming the tool output is a JSON string representing the categories list
            categories_list = json.loads(tool_output_json_string)
            if isinstance(categories_list, list):
                 result = CategoryAnalysisResult(
                     status="success",
                     processing_time=0.0, # Placeholder
                     categories=categories_list,
                     analysis_details="Processed via direct tool call."
                 )
                 self.last_result = result
                 return result
            else:
                 logger.error(f"Tool output was not a list: {tool_output_json_string}")
                 return CategoryAnalysisResult(
                     status="error",
                     processing_time=0.0,
                     categories=[],
                     analysis_details=f"Tool output was not a list: {tool_output_json_string}"
                 )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse tool output into CategoryAnalysisResult (JSON Error): {e}")
            return CategoryAnalysisResult(
                status="error",
                processing_time=0.0,
                categories=[],
                analysis_details=f"Failed to parse tool output as JSON: {e}"
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred during direct process call: {e}")
            return CategoryAnalysisResult(
                status="error",
                processing_time=0.0,
                categories=[],
                analysis_details=f"An unexpected error occurred: {e}"
            )
