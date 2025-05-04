import os
import yaml
import logging # Import logging
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from typing import Dict, Any, List
from pathlib import Path
from pydantic import ValidationError # Import ValidationError to potentially catch it here if needed
from app.services.lmstudio import LMStudioService, LMStudioLiteLLMWrapper # Import LMStudioService and the new wrapper

# Assuming these custom agent wrapper classes exist and work correctly
# They should contain the logic for interacting with services and returning results
from app.agents.topic_analysis import TopicAnalysisAgent
from app.agents.category_breakdown import CategoryBreakdownAgent
from app.agents.iterative_refinement import IterativeRefinementAgent
from app.agents.research_integration import ResearchIntegrationAgent

# Assuming your LMStudio service exists and works correctly
# from app.services.lmstudio import LMStudioService # Already imported above

# Assuming your PromptRequest model exists
from app.models.prompt import PromptRequest

# Define the path to the configuration directory
# This path should now be relative to the crew.py file itself
# and point to the config directory *within* app/orchestrator/
CONFIG_DIR = Path(__file__).parent / "config"
print(f"CONFIG_DIR: {CONFIG_DIR}") # Print the actual path being used

# Configure logger for this module
logger = logging.getLogger(__name__)
# You might want to set a specific level for this logger if needed,
# or rely on the basicConfig level set in run.py or main.py
# logger.setLevel(logging.INFO)


@CrewBase
class PromptEnhancerCrew:
    """CrewAI orchestration for the Prompt Enhancer System"""

    def __init__(self):
        # __init__ can be used for general setup, but agent/task/crew creation
        # is handled by the decorated methods below.
        pass

    def _load_config(self, config_name: str) -> Dict[str, Any]:
        """Helper to load a specific configuration file"""
        config_path = CONFIG_DIR / f"{config_name}.yaml"
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            raise # Re-raise the exception
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file {config_path}: {e}")
            raise # Re-raise the exception


    # Define the LMStudio service instance
    # This is initialized once per CrewBase instance and reused by agent methods
    @property
    def lmstudio_service(self) -> LMStudioService:
        """Initializes and returns the LMStudio service"""
        # You might want to cache this if it's expensive to initialize
        # This implementation creates a new instance each time the property is accessed,
        # which is fine if LMStudioService is lightweight. If not, implement caching here.
        return LMStudioService()

    @property
    def litellm_llm(self) -> LMStudioLiteLLMWrapper: # Change return type hint
        """Initializes and returns a LiteLLM instance configured for LMStudio"""
        # Get the LMStudio service instance to access its configuration
        lmstudio_service = self.lmstudio_service
        # Return an instance of the new wrapper class
        return LMStudioLiteLLMWrapper(lmstudio_service=lmstudio_service)

    # Renamed agent methods to match expected names in tasks.yaml
    @agent
    def topic_analysis(self) -> Agent: # Renamed from topic_analysis_agent
        """Creates and returns the Topic Analysis Agent."""
        agents_config = self._load_config("agents")
        agent_config = agents_config.get("topic_analysis", {})
        custom_agent_wrapper = TopicAnalysisAgent(
            agent_config,
            self.lmstudio_service, # Pass the LMStudio service instance
            self.litellm_llm # Pass the configured LiteLLM instance (the wrapper)
        )
        # The custom_agent_wrapper instance holds the CrewAI Agent AND the tool
        return custom_agent_wrapper.agent # Return the CrewAI Agent instance


    @agent
    def category_breakdown(self) -> Agent: # Renamed from category_breakdown_agent
        """Creates and returns the Category Breakdown Agent."""
        agents_config = self._load_config("agents")
        agent_config = agents_config.get("category_breakdown", {})
        custom_agent_wrapper = CategoryBreakdownAgent(
            agent_config,
            self.lmstudio_service, # Pass the LMStudio service instance
            self.litellm_llm # Pass the configured LiteLLM instance (now the wrapper)
        )
        return custom_agent_wrapper.agent

    @agent
    def iterative_refinement(self) -> Agent: # Renamed from iterative_refinement_agent
        """Creates and returns the Iterative Refinement Agent."""
        agents_config = self._load_config("agents")
        agent_config = agents_config.get("iterative_refinement", {})
        custom_agent_wrapper = IterativeRefinementAgent(
            agent_config,
            self.lmstudio_service, # Pass the LMStudio service instance
            self.litellm_llm # Pass the configured LiteLLM instance (the wrapper)
        )
        return custom_agent_wrapper.agent

    @agent
    def research_integration(self) -> Agent: # Renamed from research_integration_agent
        """Creates and returns the Research Integration Agent."""
        agents_config = self._load_config("agents")
        agent_config = agents_config.get("research_integration", {})
        custom_agent_wrapper = ResearchIntegrationAgent(
            agent_config,
            self.lmstudio_service, # Pass the LMStudio service instance
            self.litellm_llm # Pass the configured LiteLLM instance (the wrapper)
        )
        return custom_agent_wrapper.agent


    @task
    def topic_analysis_task(self) -> Task:
        """Creates and returns the Topic Analysis Task"""
        tasks_config = self._load_config("tasks")
        task_config = tasks_config.get("topic_analysis_task", {})
        # Get the agent instance to access its tools
        topic_analysis_agent_instance = self.topic_analysis() # Call the agent method

        return Task(
            description=task_config.get("description", "Default topic analysis description."),
            expected_output=task_config.get("expected_output", "A JSON object containing core topics, domain, complexity, and key entities."),
            agent=topic_analysis_agent_instance, # Assign the agent instance
            tools=[topic_analysis_agent_instance.tools[0]], # Add the tool to the task's tools list
            # The task description in tasks.yaml MUST now instruct the agent to use this tool
            # e.g., "Use the 'Topic Analysis Tool' to analyze the input prompt: {prompt}"
            # Ensure the description also includes {prompt} if it's used.
        )

    @task
    def category_breakdown_task(self) -> Task:
        """Creates and returns the Category Breakdown Task"""
        tasks_config = self._load_config("tasks")
        task_config = tasks_config.get("category_breakdown_task", {})
        category_breakdown_agent_instance = self.category_breakdown()
        return Task(
            description=task_config.get("description", "Default category breakdown description."),
            expected_output=task_config.get("expected_output", "A list of categories or sub-topics identified in the prompt."),
            agent=category_breakdown_agent_instance,
            # Add tool(s) for this task if the CategoryBreakdownAgent has one
            # tools=[category_breakdown_agent_instance.tools[0]], # Example
            context=[self.topic_analysis_task()], # This task likely needs context from the previous one
            # Ensure the description in tasks.yaml uses {output of topic_analysis_task} and {prompt}
        )

    @task
    def iterative_refinement_task(self) -> Task:
        """Creates and returns the Iterative Refinement Task"""
        tasks_config = self._load_config("tasks")
        task_config = tasks_config.get("iterative_refinement_task", {})
        iterative_refinement_agent_instance = self.iterative_refinement()
        return Task(
            description=task_config.get("description", "Default iterative refinement description."),
            expected_output=task_config.get("expected_output", "A refined version of the original prompt."),
            agent=iterative_refinement_agent_instance,
            # Add tool(s) for this task if the IterativeRefinementAgent has one
            # tools=[iterative_refinement_agent_instance.tools[0]], # Example
            context=[self.topic_analysis_task(), self.category_breakdown_task()], # Needs context
            # Ensure the description in tasks.yaml uses {output of topic_analysis_task}, {output of category_breakdown_task}, and {prompt}
        )

    @task
    def research_integration_task(self) -> Task:
        """Creates and returns the Research Integration Agent"""
        tasks_config = self._load_config("tasks")
        task_config = tasks_config.get("research_integration_task", {})
        research_integration_agent_instance = self.research_integration()
        return Task(
            description=task_config.get("description", "Default research integration description."),
            expected_output=task_config.get("expected_output", "The refined prompt with relevant research findings integrated."),
            agent=research_integration_agent_instance,
            # Add tool(s) for this task if the ResearchIntegrationAgent has one
            # tools=[self.research_tool()], # Example: If you have a research tool method
            context=[self.iterative_refinement_task()], # Needs context
            # Ensure the description in tasks.yaml uses {output of iterative_refinement_task}, {prompt}, and {context}
        )


    @crew
    def get_crew(self) -> Crew:
        """Creates and returns the Prompt Enhancer crew"""
        # Define the tasks in the desired execution order
        tasks_list = [
            self.topic_analysis_task(),
            self.category_breakdown_task(),
            self.iterative_refinement_task(),
            self.research_integration_task()
        ]

        return Crew(
            agents=[
                self.topic_analysis(), # Call the agent methods to get agent instances
                self.category_breakdown(),
                self.iterative_refinement(),
                self.research_integration()
            ],
            tasks=tasks_list, # Use the ordered list of tasks
            process=Process.sequential, # Or Process.hierarchical, etc.
            verbose=True # Set to False in production or based on config
        )

    def enhance_prompt(self, prompt_request: PromptRequest) -> Dict[str, Any]:
        """Process a prompt through the enhancement pipeline"""
        logger.info(f"Starting prompt enhancement for request_id: {prompt_request.request_id}")
        try:
            # Initialize crew by calling the decorated method
            logger.info("Initializing crew...")
            crew = self.get_crew()
            logger.info("Crew initialized.")

            # Execute the crew with the prompt and context
            logger.info(f"Kicking off crew with prompt: {prompt_request.content[:50]}... and context: {prompt_request.context}") # Log snippet
            # Include the context from the prompt_request in the inputs dictionary
            crew_output = crew.kickoff(inputs={"prompt": prompt_request.content, "context": prompt_request.context})
            logger.info("Crew execution finished successfully.")

            # The kickoff result is typically the output of the last task.
            # Assuming the last task (research_integration_task) produces the final enhanced prompt string.
            enhanced_prompt_result = str(crew_output) # Convert to string for serialization

            # Accessing intermediate results requires agents/tasks to store them
            # and expose them in a way that can be retrieved after kickoff.
            # For now, these details are placeholders.
            processing_details = {
                 "topic_analysis": "Details not captured in this structure.",
                 "category_breakdown": "Details not captured in this structure.",
                 "iterative_refinement": "Details not captured in this structure.",
                 "research_integration": "Details not captured in this structure."
            }

            # Return the successful result
            return {
                "status": "complete",
                "enhanced_prompt": enhanced_prompt_result,
                "processing_details": processing_details # Placeholder details
            }
        except ValidationError as e:
            logger.error(f"Validation Error during prompt enhancement: {e}", exc_info=True)
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"Validation error during crew setup or execution: {e}")
        except Exception as e:
            logger.error(f"Error during prompt enhancement: {e}", exc_info=True)
            raise e # Re-raise the exception for the FastAPI endpoint to handle

