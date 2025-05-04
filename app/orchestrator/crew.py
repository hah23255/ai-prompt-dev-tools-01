import os
import yaml
import logging # Import logging
import json # Import the json module
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
from app.agents.research_integration import ResearchIntegrationAgent, ResearchIntegrationInputData, ResearchIntegrationToolInput # Import necessary classes for manual input construction

# Assuming your LMStudio service exists and works correctly
# from app.services.lmstudio import LMStudioService # Already imported above

# Assuming your PromptRequest model exists
from app.models.prompt import PromptRequest

# Define the path to the configuration directory
# This path should now be relative to the crew.py file itself
# and point to the config directory *within* app/orchestrator/
# Updated CONFIG_DIR to be relative to the current file's directory
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
        # Initialize service and LLM instances
        self.lmstudio_service = LMStudioService()
        self.litellm_llm = LMStudioLiteLLMWrapper(self.lmstudio_service)

        # Initialize custom agent wrappers
        agents_config = self._load_config("agents")
        self.topic_analysis_wrapper = TopicAnalysisAgent(agents_config.get("topic_analysis", {}), self.lmstudio_service, self.litellm_llm)
        self.category_breakdown_wrapper = CategoryBreakdownAgent(agents_config.get("category_breakdown", {}), self.lmstudio_service, self.litellm_llm)
        self.iterative_refinement_wrapper = IterativeRefinementAgent(agents_config.get("iterative_refinement", {}), self.lmstudio_service, self.litellm_llm)
        self.research_integration_wrapper = ResearchIntegrationAgent(agents_config.get("research_integration", {}), self.lmstudio_service, self.litellm_llm)

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
            # Log a warning instead of raising an error here, as CrewBase
            # might handle missing files differently or you might want
            # to proceed with defaults if the files are optional.
            # Re-raising is probably correct if they are mandatory.
            logger.error(f"Configuration file not found: {config_path}")
            raise # Re-raise the exception
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file {config_path}: {e}")
            raise # Re-raise the exception


    # Modified agent methods to return the custom agent wrapper instance
    @agent
    def topic_analysis(self) -> Agent: # Return type hint is CrewAI Agent
        """Returns the CrewAI Topic Analysis Agent instance."""
        # The wrapper is initialized in __init__
        return self.topic_analysis_wrapper.agent


    @agent
    def category_breakdown(self) -> Agent: # Return type hint is CrewAI Agent
        """Returns the CrewAI Category Breakdown Agent instance."""
        # The wrapper is initialized in __init__
        return self.category_breakdown_wrapper.agent

    @agent
    def iterative_refinement(self) -> Agent: # Return type hint is CrewAI Agent
        """Returns the CrewAI Iterative Refinement Agent instance."""
        # The wrapper is initialized in __init__
        return self.iterative_refinement_wrapper.agent

    @agent
    def research_integration(self) -> Agent: # Return type hint is CrewAI Agent
        """Returns the CrewAI Research Integration Agent instance."""
        # The wrapper is initialized in __init__
        return self.research_integration_wrapper.agent


    @task
    def topic_analysis_task(self) -> Task:
        """Creates and returns the Topic Analysis Task"""
        tasks_config = self._load_config("tasks")
        task_config = tasks_config.get("topic_analysis_task", {})
        # Get the CrewAI Agent instance (returned by the @agent method)
        topic_analysis_crewai_agent = self.topic_analysis() # Call the agent method

        return Task(
            description=task_config.get("description", "Default topic analysis description."), # <-- Pass description directly
            expected_output=task_config.get("expected_output", "A JSON object containing core topics, domain, complexity, and key entities."), # <-- Pass expected_output directly
            agent=topic_analysis_crewai_agent, # Assign the CrewAI Agent instance
            tools=[self.topic_analysis_wrapper.topic_analysis_tool], # Access the tool from the wrapper attribute
            # The task description in tasks.yaml MUST now instruct the agent to use this tool
            # e.g., "Use the 'Topic Analysis Tool' to analyze the input prompt: {prompt}"
            # Ensure the description also includes {prompt} if it's used.
        )

    @task
    def category_breakdown_task(self) -> Task:
        """Creates and returns the Category Breakdown Task"""
        tasks_config = self._load_config("tasks")
        task_config = tasks_config.get("category_breakdown_task", {})
        # Get the CrewAI Agent instance
        category_breakdown_crewai_agent = self.category_breakdown() # Get the agent instance
        return Task(
            description=task_config.get("description", "Default category breakdown description."), # <-- Pass description directly
            expected_output=task_config.get("expected_output", "A list of strings, where each string is a identified category or sub-topic."), # <-- Pass expected_output directly
            agent=category_breakdown_crewai_agent, # Assign the CrewAI Agent instance
            # Add tool(s) for this task if the CategoryBreakdownAgent has one
            # tools=[self.category_breakdown_wrapper.category_breakdown_tool], # Example - Access tool from wrapper attribute
            # context=[self.topic_analysis_task()], # This task likely needs context from the previous one
            # Ensure the description in tasks.yaml uses {output of topic_analysis_task} and {prompt}
        )

    @task
    def iterative_refinement_task(self) -> Task:
        """Creates and returns the Iterative Refinement Task"""
        tasks_config = self._load_config("tasks")
        task_config = tasks_config.get("iterative_refinement_task", {})
        # Get the CrewAI Agent instance
        iterative_refinement_crewai_agent = self.iterative_refinement() # Get the agent instance
        return Task(
            description=task_config.get("description", "Default iterative refinement description."), # <-- Pass description directly
            expected_output=task_config.get("expected_output", "A significantly improved and more detailed version of the original prompt."), # <-- Pass expected_output directly
            agent=iterative_refinement_crewai_agent, # Assign the CrewAI Agent instance
            # Add tool(s) for this task if the IterativeRefinementAgent has one
            # tools=[self.iterative_refinement_wrapper.iterative_refinement_tool], # Example - Access tool from wrapper attribute
            # context=[self.topic_analysis_task(), self.category_breakdown_task()], # Needs context
            # Ensure the description in tasks.yaml uses {output of topic_analysis_task}, {output of category_breakdown_task}, and {prompt}
        )

    @task
    def research_integration_task(self) -> Task:
        """Creates and returns the Research Integration Agent"""
        tasks_config = self._load_config("tasks")
        task_config = tasks_config.get("research_integration_task", {})
        # Get the CrewAI Agent instance
        research_integration_crewai_agent = self.research_integration() # Get the agent instance
        return Task(
            description=task_config.get("description", "Default research integration description."), # <-- Pass description directly
            expected_output=task_config.get("expected_output", "The refined prompt with relevant research findings integrated."), # <-- Pass expected_output directly
            agent=research_integration_crewai_agent, # Assign the CrewAI Agent instance
            # Add tool(s) for this task if the ResearchIntegrationAgent has one
            # tools=[self.research_integration_wrapper.research_integration_tool], # Example - Access tool from wrapper attribute
            # context=[self.iterative_refinement_task()] # Needs context
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
            # self.research_integration_task() # Removed from here to be manually executed
        ]

        # Get the CrewAI Agent instances from the custom wrappers for the Crew initialization
        # ONLY include the first three agents in the main crew
        crew_agents = [
            self.topic_analysis(), # Call the agent methods to get agent instances
            self.category_breakdown(),
            self.iterative_refinement(),
            # self.research_integration().agent # Removed from the main crew
        ]


        return Crew(
            agents=crew_agents, # Use the list of CrewAI Agent instances (first three)
            tasks=tasks_list, # Use the ordered list of tasks (excluding the last one)
            process=Process.sequential, # Or Process.hierarchical, etc.
            verbose=True # Set to False in production or based on config
        )

    def enhance_prompt(self, prompt_request: PromptRequest) -> Dict[str, Any]:
        """Process a prompt through the enhancement pipeline"""
        logger.info(f"Starting prompt enhancement for request_id: {prompt_request.request_id}")
        try:
            # Initialize crew by calling the decorated method
            logger.info("Initializing crew...")
            # Get the crew instance. This instance contains the agent wrappers.
            # Note: get_crew now only includes the first three agents in its Crew instance
            crew_instance = self.get_crew()
            logger.info("Crew initialized.")

            # Separate the tasks for manual execution of the last one
            # Get the task instances directly from the crew_instance.tasks list
            tasks_for_intermediate_crew = crew_instance.tasks # This list already excludes the last task as per get_crew

            # Get the Research Integration Agent *wrapper* instance directly
            # Find the agent wrapper instance associated with the research integration agent
            research_integration_agent_wrapper = None
            # Access the research integration agent wrapper directly from the attribute
            research_integration_agent_wrapper = self.research_integration_wrapper

            if not research_integration_agent_wrapper:
                 # This should not happen if the @agent methods are defined, but good practice to check
                 raise Exception("Research Integration Agent wrapper instance not found.")


            # Execute the first three tasks sequentially using an intermediate crew
            logger.info("Executing Topic Analysis, Category Breakdown, and Iterative Refinement tasks...")
            # Create a new Crew instance for the intermediate tasks
            # This ensures the context and outputs are managed for these steps
            intermediate_crew_agents = [
                self.topic_analysis(),
                self.category_breakdown(),
                self.iterative_refinement()
            ]
            intermediate_crew = Crew(
                agents=intermediate_crew_agents, # Use the CrewAI Agent instances
                tasks=tasks_for_intermediate_crew, # Use the list of tasks excluding the last one
                process=Process.sequential,
                verbose=True
            )

            # Kickoff the intermediate crew. The output will be the result of the last task (iterative refinement).
            # Pass the original prompt and context to the intermediate crew
            intermediate_results = intermediate_crew.kickoff(inputs={"prompt": prompt_request.content, "context": prompt_request.context})
            # The output of the intermediate crew's kickoff is the output of the last task in its task list
            refined_prompt_output = str(intermediate_results) # Assuming the output is the refined prompt string
            logger.info(f"Iterative Refinement task completed. Output (first 50 chars): {refined_prompt_output[:50]}...")


            # Manually execute the Research Integration Task using the agent wrapper's process method
            logger.info("Executing Research Integration task manually...")

            # Ensure the additional_context is a JSON string as expected by the agent's process method
            # json.dumps handles converting the context dictionary to a JSON string
            additional_context_json_string = json.dumps(prompt_request.context)

            # Call the process method of the Research Integration Agent *wrapper* instance
            # Construct the input object expected by the process method
            research_integration_input = ResearchIntegrationToolInput(
                tool_input=ResearchIntegrationInputData(
                    refined_prompt=refined_prompt_output,
                    original_prompt=prompt_request.content,
                    additional_context=additional_context_json_string
                )
            )

            # Call the process method with the constructed input object
            final_enhanced_prompt = research_integration_agent_wrapper.process(research_integration_input)

            logger.info("Research Integration task completed manually.")

            # The final result is the output from the manual process call
            enhanced_prompt_result = str(final_enhanced_prompt)

            # Accessing intermediate results would require the agent wrappers to store them
            # and expose them. For now, these details are placeholders.
            # In a real application, you would collect results from agent wrapper instances
            # after the crew has run, assuming they store their results.
            processing_details = {
                 "topic_analysis": "Details not captured in this structure.", # Need to update if agents store results
                 "category_breakdown": "Details not captured in this structure.", # Need to update if agents store results
                 "iterative_refinement": "Details not captured in this structure.", # Need to update if agents store results
                 "research_integration": "Details captured via manual execution."
            }

            # Return the successful result
            return {
                "status": "complete",
                "enhanced_prompt": enhanced_prompt_result,
                "processing_details": processing_details
            }
        except ValidationError as e:
            logger.error(f"Validation Error during prompt enhancement: {e}", exc_info=True)
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"Validation error during crew setup or execution: {e}")
        except Exception as e:
            logger.error(f"Error during prompt enhancement: {e}", exc_info=True)
            raise e # Re-raise the exception for the FastAPI endpoint to handle
