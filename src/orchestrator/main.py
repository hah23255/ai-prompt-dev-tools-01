import logging
from datetime import datetime

from src.orchestrator.agents.category_breakdown import break_down_category
from src.orchestrator.agents.iterative_refinement import refine_iteratively
from src.orchestrator.agents.research_integration import integrate_research


# Configure logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Log start of the application
logging.info(f"Application started at {datetime.now()}")

# Define Pydantic models for input validation
from pydantic import BaseModel, Field

class PromptRequest(BaseModel):
    content: str = Field(..., description="The user's input prompt")
    metadata: dict = Field({}, description="Additional metadata for processing")

class ProcessingStep(BaseModel):
    step_name: str
    input_data: dict
    output_data: dict
    status: str = "completed"
    error_message: str = ""


def orchestrate(prompt_request: PromptRequest) -> dict:
    """
    Orchestrate the workflow through all agents with validation and logging.

    Args:
        prompt_request: A validated request containing the user's prompt and metadata

    Returns:
        Dictionary containing final result and processing history

    Raises:
        ValidationError: If input validation fails
        RuntimeError: For orchestration errors
    """
    try:
        # Validate input using Pydantic
        prompt_request.model_validate()

        # Initialize processing history
        processing_history = []

        # Step 1: Topic Analysis

        try:
            from src.orchestrator.agents.topic_analysis import analyze_topic
            
            topic_result = analyze_topic(prompt_request.content)
            step_data.output_data = {"topic": topic_result}
            logging.info(f"Topic analysis completed: {topic_result}")
        except Exception as e:
            step_data.status = "failed"
            step_data.error_message = str(e)

        processing_history.append(step_data)

        # Step 2: Category Breakdown
        if step_data.status == "completed":

            try:
                from src.orchestrator.agents.category_breakdown import break_down_category
                
                category_result = break_down_category(topic_result)
                step_data.output_data = {"categories": category_result}
                logging.info(f"Category breakdown completed: {category_result}")
            except Exception as e:
                step_data.status = "failed"
                step_data.error_message = str(e)

            processing_history.append(step_data)

        # Step 3: Iterative Refinement
        if all(s.status == "completed" for s in processing_history):
            logging.info("Starting iterative refinement...")
            step_data = ProcessingStep(
                step_name="iterative_refinement",
                input_data={"categories": category_result},
                output_data={}
            )


            processing_history.append(step_data)

        # Step 4: Research Integration
        if all(s.status == "completed" for s in processing_history):
            logging.info("Starting research integration...")
            step_data = ProcessingStep(
                step_name="research_integration",
                input_data={"refined_prompt": refined_result},
                output_data={}
            )

            try:
                from src.orchestrator.agents.research_integration import integrate_research
                
                refined_result = "Refined result placeholder"  # Define refined_result before using it
                final_result = integrate_research(refined_result)
                step_data.output_data = {"final_output": final_result}
                logging.info("Research integration completed successfully")
            except Exception as e:
                step_data.status = "failed"
                step_data.error_message = str(e)

            processing_history.append(step_data)

        # Return result with processing history
        return {
            "final_output": final_result,
            "processing_history": processing_history
        }

    except ValidationError as ve:
        logging.error(f"Input validation failed: {ve}", exc_info=True)
        raise RuntimeError(f"Invalid input format: {ve}") from ve
    except Exception as e:
        logging.critical(f"Critical orchestration error: {e}", exc_info=True)
        raise RuntimeError(f"Orchestration failed: {e}") from e

class Orchestrator:
    def __init__(self):
        self.processing_history = []

    def initiate_orchestration(self, prompt: str) -> dict:
        prompt_request = PromptRequest(content=prompt)
        return orchestrate(prompt_request)

    def get_processing_status(self) -> dict:
        return {
            "status": "completed" if all(s.status == "completed" for s in self.processing_history) else "in_progress",
            "processing_history": [step.dict() for step in self.processing_history]
        }

if __name__ == "__main__":
    # Example usage with validation
    prompt = PromptRequest(
        content="Your prompt here",
        metadata={"priority": "high", "user_id": "12345"}
    )

    try:
        result = orchestrate(prompt)
        print("Final output:", result["final_output"])
        print("\nProcessing history:")
        for step in result["processing_history"]:
            print(f"- {step.step_name}: {step.status}")
    except Exception as e:
        print(f"Error: {e}")