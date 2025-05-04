import json
import logging
from pydantic import BaseModel, Field, ValidationError
from src.orchestrator.agents.topic_analysis import analyze_topic
from src.orchestrator.agents.category_breakdown import break_down_category
from src.orchestrator.agents.iterative_refinement import refine_iteratively
from src.orchestrator.agents.research_integration import integrate_research

# Define Pydantic models for input validation
class PromptRequest(BaseModel):
    content: str = Field(..., description="The user's input prompt")
    metadata: dict = Field({}, description="Additional metadata for processing")

class ProcessingStep(BaseModel):
    step_name: str
    input_data: dict
    output_data: dict
    status: str = "completed"
    error_message: str = ""

# Configure logging
logging.basicConfig(
    filename='orchestrator.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [Orchestrator] %(message)s'
)

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
        PromptRequest.model_validate(prompt_request)
        
        # Initialize processing history
        processing_history = []
        
        # Step 1: Topic Analysis
        logging.info(f"Starting topic analysis for prompt: {prompt_request.content[:50]}...")
        step_data = ProcessingStep(
            step_name="topic_analysis",
            input_data={"prompt": prompt_request.content},
            output_data={}
        )
        
        try:
            topic_result = analyze_topic(prompt_request.content)
            step_data.output_data = {"topic": topic_result}
            logging.info(f"Topic analysis completed: {topic_result}")
        except Exception as e:
            step_data.status = "failed"
            step_data.error_message = str(e)
            logging.error(f"Topic analysis failed: {e}", exc_info=True)
            
        processing_history.append(step_data)
        
        # Step 2: Category Breakdown
        if step_data.status == "completed":
            logging.info("Starting category breakdown...")
            step_data = ProcessingStep(
                step_name="category_breakdown",
                input_data={"topic": topic_result},
                output_data={}
            )
            
            try:
                category_result = break_down_category(topic_result)
                step_data.output_data = {"categories": category_result}
                logging.info(f"Category breakdown completed: {category_result}")
            except Exception as e:
                step_data.status = "failed"
                step_data.error_message = str(e)
                logging.error(f"Category breakdown failed: {e}", exc_info=True)
                
            processing_history.append(step_data)
        
        # Step 3: Iterative Refinement
        if all(s.status == "completed" for s in processing_history):
            logging.info("Starting iterative refinement...")
            step_data = ProcessingStep(
                step_name="iterative_refinement",
                input_data={"categories": category_result},
                output_data={}
            )
            
            try:
                refined_result = refine_iteratively(category_result)
                step_data.output_data = {"refined_prompt": refined_result}
                logging.info(f"Refinement completed: {refined_result[:50]}...")
            except Exception as e:
                step_data.status = "failed"
                step_data.error错误信息 = str(e)
                logging.error(f"Refinement failed: {e}", exc_info=True)
                
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
                final_result = integrate_research(refined_result)
                step_data.output_data = {"final_output": final_result}
                logging.info("Research integration completed successfully")
            except Exception as e:
                step_data.status = "failed"
                step_data.error_message = str(e)
                logging.error(f"Research integration failed: {e}", exc_info=True)
                
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