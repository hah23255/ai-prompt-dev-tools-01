import logging
from crewai import Agent
from crewai.tools import BaseTool # Import BaseTool
# Assuming these models exist
from app.models.prompt import PromptRequest # Assuming PromptRequest might be needed for type hinting
from app.models.response import ResearchIntegrationResult, IterativeRefinementResult # Import necessary result models
from app.services.lmstudio import LMStudioService # Import LMStudioService
# Assuming you have a ResearchTool service/class
# from app.services.research import ResearchService # Example import - Uncomment if you have this service
from typing import Dict, Any, List, Optional
from datetime import datetime
import json # Import json

logger = logging.getLogger(__name__)

# Define the custom tool by subclassing BaseTool
class ResearchIntegrationTool(BaseTool):
    """Tool for integrating research findings and context into a refined prompt using LMStudio."""

    name: str = "Research Integration Tool"
    description: str = (
        "Integrates relevant research findings and additional context into a refined prompt. "
        "Returns the final enhanced prompt as a string."
        "Input should be a string containing the refined prompt, original prompt, and optional additional context."
        "Example input format: 'Refined Prompt: [Refined Prompt Here]\nOriginal Prompt: [Original Prompt Here]\nAdditional Context: [Optional Context Here]'"
    )
    # Add service and llm as attributes that will be passed during instantiation
    lmstudio_service: LMStudioService
    llm: Any # Or a more specific type if available
    # research_service: Optional[Any] = None # Add research service if you have one

    def _run(self, tool_input: str) -> str:
        """
        Runs the research integration logic by prompting LMStudio and potentially using a research service.
        This method is called by the CrewAI agent when the tool is used.
        Expects input in the format 'Refined Prompt: ...\nOriginal Prompt: ...\nAdditional Context: ...'.
        """
        logger.info(f"Executing Research Integration Tool with input: {tool_input[:150]}...")

        # Parse the input string to extract refined prompt, original prompt, and context
        refined_prompt = ""
        original_prompt = ""
        additional_context = ""
        lines = tool_input.split('\n')

        current_section = None
        for line in lines:
            if line.startswith("Refined Prompt: "):
                refined_prompt = line[len("Refined Prompt: "):].strip()
                current_section = "Refined Prompt"
            elif line.startswith("Original Prompt: "):
                original_prompt = line[len("Original Prompt: "):].strip()
                current_section = "Original Prompt"
            elif line.startswith("Additional Context: "):
                additional_context = line[len("Additional Context: "):].strip()
                current_section = "Additional Context"
            elif current_section == "Refined Prompt":
                 refined_prompt += "\n" + line.strip() # Append subsequent lines
            elif current_section == "Original Prompt":
                 original_prompt += "\n" + line.strip() # Append subsequent lines
            elif current_section == "Additional Context":
                 additional_context += "\n" + line.strip() # Append subsequent lines


        if not refined_prompt:
             logger.error("Research Integration Tool received input without 'Refined Prompt:' prefix.")
             return "Error during integration: Tool input missing refined prompt."

        # --- Research Step (Placeholder) ---
        # If you have a research service, use it here.
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

Research Findings: {"[No research service available]" } # Replace with {research_results} if using a research service

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
    def process(self, tool_input: str) -> ResearchIntegrationResult:
        """Process the input and integrate research (now handled by the tool)."""
        logger.warning("ResearchIntegrationAgent.process called directly. CrewAI task uses the ResearchIntegrationTool.")
        # Example: Call the tool's _run method if needed for direct processing
        # The tool expects a string input like "Refined Prompt: ...\nOriginal Prompt: ...\nAdditional Context: ..."
        integrated_output_string = self.research_integration_tool._run(tool_input)
        # Assuming the tool returns the final prompt string directly
        result = ResearchIntegrationResult(
            status="success" if not integrated_output_string.startswith("Error during final integration:") else "error",
            processing_time=0.0, # Placeholder
            integrated_output=integrated_output_string if not integrated_output_string.startswith("Error during final integration:") else "Error: " + integrated_output_string,
            integration_details="Processed via direct tool call." if not integrated_output_string.startswith("Error during final integration:") else integrated_output_string,
            timestamp=datetime.now()
        )
        self.last_result = result
        return result

