import logging
from crewai import Agent
from crewai.tools import BaseTool # Import BaseTool
# Assuming these models exist

from app.models.prompt import PromptRequest # Assuming PromptRequest might be needed for type hinting
from app.models.response import ResearchIntegrationResult # Import necessary result models
from app.services.lmstudio import LMStudioService # Import LMStudioService
# Assuming you have a ResearchTool service/class
# from app.services.research import ResearchService # Example import - Uncomment if you have this service
from typing import Dict, Any, List, Optional
from datetime import datetime
import json # Import json
from pydantic import BaseModel, Field # Import BaseModel and Field for Pydantic schema

logger = logging.getLogger(__name__)

# Define the Pydantic model for the actual input data fields for Research Integration
class ResearchIntegrationInputData(BaseModel):
    """Schema for the actual data fields within the Research Integration tool's input."""
    refined_prompt: str = Field(description="The refined prompt from the previous task.")
    original_prompt: str = Field(description="The original text prompt from the user.")
    additional_context: str = Field(description="Additional context or research findings as a JSON string.")

# Define the Pydantic model that CrewBase seems to expect for args_schema
# This model has a single field named 'tool_input'
class ResearchIntegrationToolInput(BaseModel):
    """Input schema for the ResearchIntegrationTool, structured to satisfy CrewBase validation."""
    # This 'tool_input' field is added to satisfy CrewBase's specific validation
    # The actual data the tool needs is nested within this field.
    tool_input: ResearchIntegrationInputData = Field(description="Container for the tool's input data.")


# Define the custom tool by subclassing BaseTool
class ResearchIntegrationTool(BaseTool):
    """Tool for integrating research findings and context into a refined prompt using LMStudio."""

    name: str = "Research Integration Tool"
    description: str = (
        "Integrates relevant research findings and additional context into a refined prompt. "
        "Returns the final enhanced prompt as a string."
        "Input should be a JSON object with a single key 'tool_input', whose value is a JSON object "
        "with 'refined_prompt', 'original_prompt', and 'additional_context' keys."
        "Example input JSON: {'tool_input': {'refined_prompt': 'Refined Prompt Here', 'original_prompt': 'Original Prompt Here', 'additional_context': '{...Context JSON...}'}"
    )
    # Define the input model for the tool, using the nested structure
    args_schema: type = ResearchIntegrationToolInput

    # Add service and llm as attributes that will be passed during instantiation
    lmstudio_service: LMStudioService
    llm: Any # Or a more specific type if available
    # research_service: Optional[Any] = None # Add research service if you have one

    # The _run method now receives the validated ResearchIntegrationToolInput instance
    def _run(self, tool_input: ResearchIntegrationToolInput) -> str:
        """
        Runs the research integration logic by prompting LMStudio.
        This method is called by the CrewAI agent when the tool is used.
        Receives input as a ResearchIntegrationToolInput instance with nested data.
        """
        logger.info(f"Executing Research Integration Tool...")
        # Access the actual input data from the nested 'tool_input' field
        input_data = tool_input.tool_input
        logger.info(f"  Refined Prompt: {input_data.refined_prompt[:100]}...")
        logger.info(f"  Original Prompt: {input_data.original_prompt[:100]}...")
        logger.info(f"  Additional Context: {input_data.additional_context[:100]}...")

        # The input is now validated and available via the input_data object
        refined_prompt = input_data.refined_prompt
        original_prompt = input_data.original_prompt
        additional_context = input_data.additional_context

        # --- Research Step (Placeholder) ---
        # Initialize research_results to an empty string or default value
        research_results = "[No research service available]"
        # If you have a research service, uncomment and use it here.
        # research_query = f"Find relevant information for: {original_prompt}" # Or refined_prompt
        # research_results = ""
        # if self.research_service:
        #     try:
        #         research_results = self.research_service.perform_search(research_query)
        #         logger.info(f"Research results obtained (first 50 chars): {research_results[:50]}...")
        #     except Exception as e:
        #         logger.error(f"Error during research service call: {e}")
        #         research_results = f"Error obtaining research results: {e}"
        # else:
        #      logger.warning("Research service not provided to ResearchIntegrationTool.")

        # Combine all information for the final LMStudio prompt
        integration_prompt = f"""
Integrate the following research findings and additional context into the refined prompt.
The goal is to create the final, most comprehensive and useful version of the prompt.

Refined Prompt: {refined_prompt}

Original Prompt: {original_prompt}

Additional Context: {additional_context if additional_context else "No additional context provided."}

Research Findings: {research_results} # Use the initialized variable

Provide the final, enhanced prompt as your output. Do not include any other text or formatting.
"""

        try:
            # Use the LMStudio service instance passed to the tool
            final_enhanced_prompt = self.lmstudio_service.generate_completion(integration_prompt)
            logger.info(f"Received final enhanced prompt from LMStudio (first 50 chars): {final_enhanced_prompt[:50]}...")

            # Return the final enhanced prompt string
            return final_enhanced_prompt.strip() # Return the cleaned response string

        except Exception as e:
            logger.error(f"Error calling LMStudio service from Research Integration tool: {e}")
            # Return an error message
            return f"Error during final integration: {e}" # Return error as a string


class ResearchIntegrationAgent:
    """Agent responsible for integrating research findings into the prompt refinement"""

    # Corrected __init__ to accept necessary services
    def __init__(self, config: Dict[str, Any], lmstudio_service: LMStudioService, llm: Any): # , research_service: Optional[ResearchService] = None): # Example
        self.config = config
        self.lmstudio_service = lmstudio_service # Store the service instance
        self.llm = llm # Store llm
        # self.research_service = research_service # Store research service if needed

        # Instantiate the custom tool, passing necessary dependencies
        self.research_integration_tool = ResearchIntegrationTool(
            lmstudio_service=self.lmstudio_service,
            llm=self.llm, # Pass the llm to the tool if needed within _run
            # research_service=self.research_service # Pass research service if you have one
        )

        # Initialize the CrewAI Agent here using the config
        self.agent = Agent(
            role=config.get("role", "Research Integration Specialist"),
            goal=config.get("goal", "Integrate relevant research findings to enrich the prompt."),
            backstory=config.get("backstory", "A diligent researcher who finds and synthesizes information..."),
            verbose=config.get("verbose", False),
            allow_delegation=config.get("allow_delegation", False),
            max_iter=config.get("max_iter", 15),
            max_rpm=config.get("max_rpm", 100),
            llm=self.llm, # Pass the llm instance to the CrewAI Agent
            tools=[self.research_integration_tool] # Assign the instantiated tool to the agent
        )
        self.last_result: Optional[ResearchIntegrationResult] = None

    # The process method is likely not needed if the task uses the tool directly.
    # Keeping it as a placeholder or for direct calls outside CrewAI flow if necessary.
    # Note: If you call this process method directly, you would need to construct
    # a ResearchIntegrationToolInput object with the nested structure.
    def process(self, inputs: ResearchIntegrationToolInput) -> ResearchIntegrationResult:
        """Process the input and integrate research (now handled by the tool)."""
        logger.warning("ResearchIntegrationAgent.process called directly. CrewAI task uses the ResearchIntegrationTool.")
        # Example: Call the tool's _run method if needed for direct processing
        tool_output_string = self.research_integration_tool._run(inputs) # Pass the inputs object
        # Assuming the tool returns the final prompt string directly
        result = ResearchIntegrationResult(
            status="success" if not tool_output_string.startswith("Error during final integration:") else "error",
            processing_time=0.0, # Placeholder
            integrated_output=tool_output_string if not tool_output_string.startswith("Error during final integration:") else "Error: " + tool_output_string,
            integration_details="Processed via direct tool call." if not tool_output_string.startswith("Error during final integration:") else tool_output_string,
            timestamp=datetime.now()
        )
        self.last_result = result
        return result
