import logging
# Corrected import: Import BaseTool from crewai_tools.tools.base
from crewai import Agent
from crewai.tools import BaseTool # Import BaseTool

from app.models.prompt import PromptRequest # Assuming PromptRequest might be needed for type hinting, though tool input is string
from app.models.response import CategoryAnalysisResult # Assuming this model exists
from app.services.lmstudio import LMStudioService # Import LMStudioService
from typing import Dict, Any, Optional
from datetime import datetime
import json # Import json

logger = logging.getLogger(__name__)

# Define the custom tool by subclassing BaseTool
class CategoryBreakdownTool(BaseTool):
    """Tool for breaking down a prompt into categories using LMStudio."""

    name: str = "Category Breakdown Tool"
    description: str = (
        "Analyzes a given text prompt and a topic analysis result to break down the prompt "
        "into distinct categories or sub-topics. Returns a JSON array of strings."
        "Input should be a string containing the original prompt and the topic analysis result."
        "Example input format: 'Prompt: [Original Prompt Here]\nTopic Analysis: [Topic Analysis JSON Here]'"
    )
    # Add service and llm as attributes that will be passed during instantiation
    lmstudio_service: LMStudioService
    llm: Any # Or a more specific type if available

    def _run(self, tool_input: str) -> str:
        """
        Runs the category breakdown logic by prompting LMStudio.
        This method is called by the CrewAI agent when the tool is used.
        Expects input in the format 'Prompt: [Original Prompt Here]\nTopic Analysis: [Topic Analysis JSON Here]'.
        """
        logger.info(f"Executing Category Breakdown Tool with input: {tool_input[:100]}...")

        # Parse the input string to extract prompt and topic analysis
        # This is a simple parsing based on the expected input format
        prompt_content = ""
        topic_analysis_result_str = ""
        lines = tool_input.split('\n')
        if lines:
            if lines[0].startswith("Prompt: "):
                prompt_content = lines[0][len("Prompt: "):].strip()
            # Find the line that starts with "Topic Analysis:"
            topic_analysis_line_index = -1
            for i, line in enumerate(lines):
                if line.startswith("Topic Analysis: "):
                    topic_analysis_line_index = i
                    topic_analysis_result_str = line[len("Topic Analysis: "):].strip()
                    break

        if not prompt_content:
             logger.error("Category Breakdown Tool received input without 'Prompt:' prefix.")
             return json.dumps({"status": "error", "message": "Tool input missing original prompt."})

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
    def process(self, tool_input: str) -> CategoryAnalysisResult:
        """Process the input prompt and break it down into categories (now handled by the tool)."""
        logger.warning("CategoryBreakdownAgent.process called directly. CrewAI task uses the CategoryBreakdownTool.")
        # Example: Call the tool's _run method if needed for direct processing
        # The tool expects a string input like "Prompt: ...\nTopic Analysis: ..."
        tool_output_json_string = self.category_breakdown_tool._run(tool_input)
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

