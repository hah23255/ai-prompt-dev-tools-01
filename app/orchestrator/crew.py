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
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"

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

    @agent
    def topic_analysis_agent(self) -> Agent:
        """Creates and returns the Topic Analysis Agent."""
        agents_config = self._load_config("agents")
        agent_config = agents_config.get("topic_analysis", {})
        custom_agent_wrapper = TopicAnalysisAgent(
            agent_config,
            self.lmstudio_service, # Pass the LMStudio service instance
            self.litellm_llm # Pass the configured LiteLLM instance (the wrapper)
        )
        return custom_agent_wrapper.agent

    @agent
    def category_breakdown_agent(self) -> Agent:
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
    def iterative_refinement_agent(self) -> Agent:
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
    def research_integration_agent(self) -> Agent:
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
        return Task(
            description=task_config.get("description", "Default topic analysis description."), # <-- Pass description directly
            expected_output=task_config.get("expected_output", "A JSON object containing core topics, domain, complexity, and key entities."), # <-- Pass expected_output directly
            agent=self.topic_analysis_agent(), # Reference the agent method
            # Pass other config items if needed, e.g., context, tools
            # context=[...],
            # tools=[...],
            # async_execution=task_config.get("async_execution", False)
        )

    @task
    def category_breakdown_task(self) -> Task:
        """Creates and returns the Category Breakdown Task"""
        tasks_config = self._load_config("tasks")
        task_config = tasks_config.get("category_breakdown_task", {})
        return Task(
            description=task_config.get("description", "Default category breakdown description."), # <-- Pass description directly
            expected_output=task_config.get("expected_output", "A list of categories or sub-topics identified in the prompt."), # <-- Pass expected_output directly
            agent=self.category_breakdown_agent(), # Reference the agent method
            # Pass other config items if needed
        )

    @task
    def iterative_refinement_task(self) -> Task:
        """Creates and returns the Iterative Refinement Task"""
        tasks_config = self._load_config("tasks")
        task_config = tasks_config.get("iterative_refinement_task", {})
        return Task(
            description=task_config.get("description", "Default iterative refinement description."), # <-- Pass description directly
            expected_output=task_config.get("expected_output", "A refined version of the original prompt."), # <-- Pass expected_output directly
            agent=self.iterative_refinement_agent(), # Reference the agent method
            # Pass other config items if needed
            # context=[self.topic_analysis_task(), self.category_breakdown_task()] # Example: Pass previous tasks as context
            # tools=[...],
            # async_execution=task_config.get("async_execution", False)
        )

    @task
    def research_integration_task(self) -> Task:
        """Creates and returns the Research Integration Agent"""
        tasks_config = self._load_config("tasks")
        task_config = tasks_config.get("research_integration_task", {})
        return Task(
            description=task_config.get("description", "Default research integration description."), # <-- Pass description directly
            expected_output=task_config.get("expected_output", "The refined prompt with relevant research findings integrated."), # <-- Pass expected_output directly
            agent=self.research_integration_agent(), # Reference the agent method
            # Pass other config items if needed
            # context=[self.iterative_refinement_task()] # Example: Pass previous task as context
            # tools=[self.research_tool()] # Example: If you have a research tool method
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
                self.topic_analysis_agent(), # Call the agent methods to get agent instances
                self.category_breakdown_agent(),
                self.iterative_refinement_agent(),
                self.research_integration_agent()
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

            # Execute the crew with the prompt
            logger.info(f"Kicking off crew with prompt: {prompt_request.content[:50]}...") # Log snippet
            # CrewAI's kickoff returns the final result of the last task by default.
            # If you need results from intermediate tasks, you might need to modify
            # your tasks to store results or use a different CrewAI process.
            crew_output = crew.kickoff(inputs={"prompt": prompt_request.content})
            logger.info("Crew execution finished successfully.")

            # Extract the final result string from the CrewOutput object
            # Assuming the final result is available as a string attribute, e.g., .result or similar
            # You might need to inspect the actual CrewOutput object structure if this is incorrect
            enhanced_prompt_result = str(crew_output) # Convert to string for serialization

            # Accessing intermediate results requires agents/tasks to store them
            # and expose them in a way that can be retrieved after kickoff.
            # Placeholder details are used for demonstration.
            # In a real scenario, you would collect results from your agent wrapper instances
            # after the crew has run, assuming they store their results.
            processing_details = {
                 "topic_analysis": "Details not available directly from this structure.",
                 "category_breakdown": "Details not available directly from this structure.",
                 "iterative_refinement": "Details not available directly from this structure.",
                 "research_integration": "Details not available directly from this structure."
            }

            # Return the successful result
            return {
                "status": "complete", # Change status to 'complete' on successful execution
                "enhanced_prompt": enhanced_prompt_result,
                "processing_details": processing_details # Placeholder details
            }
        except ValidationError as e:
            # Catch Pydantic Validation errors specifically and return 400
            logger.error(f"Validation Error during prompt enhancement: {e}", exc_info=True)
            # Re-raise as HTTPException for FastAPI to handle with 400 status
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"Validation error during crew setup or execution: {e}")
        except Exception as e:
            logger.error(f"Error during prompt enhancement: {e}", exc_info=True) # Log the exception details
            # Re-raise the exception so it's caught by the FastAPI endpoint's general handler
            raise e
