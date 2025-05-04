import os
import yaml
import logging # Import logging
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from typing import Dict, Any, List
from pathlib import Path

# Assuming these custom agent classes exist and work correctly
from app.agents.topic_analysis import TopicAnalysisAgent
from app.agents.category_breakdown import CategoryBreakdownAgent
from app.agents.iterative_refinement import IterativeRefinementAgent
from app.agents.research_integration import ResearchIntegrationAgent

# Assuming your LMStudio service exists and works correctly
from app.services.lmstudio import LMStudioService

# Assuming your PromptRequest model exists
from app.models.prompt import PromptRequest

# Define the path to the configuration directory
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"

# Configure basic logging (you might have a more sophisticated setup)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@CrewBase
class PromptEnhancerCrew:
    """CrewAI orchestration for the Prompt Enhancer System"""

    def __init__(self):
        # Load configurations - can still be done here or in a helper
        # Note: We'll load configs in the methods that need them for clarity,
        # but loading them once in __init__ is also fine if preferred.
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

    # Define the LMStudio service instance
    # This can be initialized once and reused
    @property
    def lmstudio_service(self) -> LMStudioService:
        """Initializes and returns the LMStudio service"""
        # You might want to cache this if it's expensive to initialize
        return LMStudioService()

    @agent
    def topic_analysis_agent(self) -> Agent:
        """Creates and returns the Topic Analysis Agent"""
        agents_config = self._load_config("agents")
        # Instantiate your custom agent wrapper, then return its internal Agent
        custom_agent = TopicAnalysisAgent(
            agents_config.get("topic_analysis", {}), # Use .get for safer access
            self.lmstudio_service
        )
        return custom_agent.agent # Assuming your custom agent has a .agent attribute

    @agent
    def category_breakdown_agent(self) -> Agent:
        """Creates and returns the Category Breakdown Agent"""
        agents_config = self._load_config("agents")
        custom_agent = CategoryBreakdownAgent(
            agents_config.get("category_breakdown", {}), # Use .get for safer access
            self.lmstudio_service
        )
        return custom_agent.agent

    @agent
    def iterative_refinement_agent(self) -> Agent:
        """Creates and returns the Iterative Refinement Agent"""
        agents_config = self._load_config("agents")
        custom_agent = IterativeRefinementAgent(
            agents_config.get("iterative_refinement", {}), # Use .get for safer access
            self.lmstudio_service
        )
        return custom_agent.agent

    @agent
    def research_integration_agent(self) -> Agent:
        """Creates and returns the Research Integration Agent"""
        agents_config = self._load_config("agents")
        custom_agent = ResearchIntegrationAgent(
            agents_config.get("research_integration", {}), # Use .get for safer access
            self.lmstudio_service
        )
        return custom_agent.agent

    @task
    def topic_analysis_task(self) -> Task:
        """Creates and returns the Topic Analysis Task"""
        tasks_config = self._load_config("tasks")
        return Task(
            config=tasks_config.get("topic_analysis_task", {}), # Use .get for safer access
            # Reference the agent method using self.method_name()
            agent=self.topic_analysis_agent()
        )

    @task
    def category_breakdown_task(self) -> Task:
        """Creates and returns the Category Breakdown Task"""
        tasks_config = self._load_config("tasks")
        return Task(
            config=tasks_config.get("category_breakdown_task", {}), # Use .get for safer access
            agent=self.category_breakdown_agent()
        )

    @task
    def iterative_refinement_task(self) -> Task:
        """Creates and returns the Iterative Refinement Task"""
        tasks_config = self._load_config("tasks")
        return Task(
            config=tasks_config.get("iterative_refinement_task", {}), # Use .get for safer access
            agent=self.iterative_refinement_agent()
        )

    @task
    def research_integration_task(self) -> Task:
        """Creates and returns the Research Integration Task"""
        tasks_config = self._load_config("tasks")
        return Task(
            config=tasks_config.get("research_integration_task", {}), # Use .get for safer access
            agent=self.research_integration_agent()
        )

    @crew
    def get_crew(self) -> Crew:
        """Creates and returns the Prompt Enhancer crew"""
        return Crew(
            agents=[
                self.topic_analysis_agent(), # Call the agent methods
                self.category_breakdown_agent(),
                self.iterative_refinement_agent(),
                self.research_integration_agent()
            ],
            tasks=[
                self.topic_analysis_task(), # Call the task methods
                self.category_breakdown_task(),
                self.iterative_refinement_task(),
                self.research_integration_task()
            ],
            process=Process.sequential,
            verbose=True
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
            result = crew.kickoff(inputs={"prompt": prompt_request.content})
            logger.info("Crew execution finished successfully.")

            # Accessing last_result from agents initialized in __init__ won't work here
            # because the agents used by the crew are created within the decorated methods.
            # You would need to modify your custom agent classes or tasks to expose
            # intermediate results in a way that can be collected after crew.kickoff().
            # For demonstration, placeholder details are used.
            processing_details = {
                 "topic_analysis": "Details not available directly from this structure.",
                 "category_breakdown": "Details not available directly from this structure.",
                 "iterative_refinement": "Details not available directly from this structure.",
                 "research_integration": "Details not available directly from this structure."
            }

            # Return the successful result
            return {
                "status": "success",
                "enhanced_prompt": result, # Assuming 'result' is the final enhanced prompt string
                "processing_details": processing_details # Placeholder details
            }

        except Exception as e:
            logger.error(f"Error during prompt enhancement: {e}", exc_info=True) # Log the exception details
            # Re-raise the exception so it's caught by the FastAPI endpoint
            raise e

