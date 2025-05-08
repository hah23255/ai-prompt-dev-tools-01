<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# from the above plan. now break into separate task documents for a junior developer ai agent to be able to achieve in small chunks.

Absolutely! Here’s how you can break the implementation plan into **separate, focused task documents** suitable for a junior developer AI agent. Each task is self-contained, includes clear objectives, and can be completed in a short development sprint (1–3 hours). This format helps with parallelization, accountability, and easy review.

---

## Task 1: Project Initialization \& Environment Setup

**Objective:**
Set up the project structure and install all required dependencies.

**Steps:**

1. Create a new directory called `prompt-enhancer`.
2. Inside, create the following folders: `app/`, `app/models/`, `app/agents/`, `app/orchestrator/`, `app/services/`, `app/static/`, `tests/`, and `config/`.
3. Initialize a Python virtual environment and activate it.
4. Create a `requirements.txt` file and add:

```
crewai
openai
pydantic
fastapi
uvicorn
lmstudio
```

5. Install dependencies using `pip install -r requirements.txt`.
6. Create empty `__init__.py` files for each Python package directory.
7. Add a `.gitignore` file to exclude `venv/`, `__pycache__/`, and `.env`.

**Deliverables:**

- Complete folder structure
- Working virtual environment
- All dependencies installed

---

## Task 2: Define Core Pydantic Data Models

**Objective:**
Create Pydantic models for prompt requests and agent responses.

**Steps:**

1. In `app/models/base.py`, define `BaseRequest` and `BaseResponse` models.
2. In `app/models/prompt.py`, define:
    - `PromptRequest`
    - `TopicAnalysisResult`
    - (Stub out similar models for other agents)
3. Ensure all models have type annotations and docstrings.

**Deliverables:**

- `app/models/base.py` and `app/models/prompt.py` with all required models

---

## Task 3: Implement LMStudio Service Integration

**Objective:**
Create a Python service to interact with the LMStudio local LLM.

**Steps:**

1. In `app/services/lmstudio.py`, create a class `LMStudioService`.
2. Implement methods to:
    - Check if the model is loaded
    - Generate a completion given a prompt
3. Add error handling for connection issues.

**Deliverables:**

- `app/services/lmstudio.py` with a working service class

---

## Task 4: Implement Topic Analysis Agent

**Objective:**
Build the Topic Analysis Agent that uses LMStudio to analyze prompts.

**Steps:**

1. In `app/agents/topic_analysis.py`, create a class `TopicAnalysisAgent`.
2. The class should:
    - Accept config and LMStudioService in its constructor
    - Have a `process()` method that:
        - Takes a `PromptRequest`
        - Calls LMStudioService with a formatted analysis prompt
        - Parses the response into a `TopicAnalysisResult`
        - Handles JSON parsing errors gracefully
3. Add docstrings and comments.

**Deliverables:**

- `app/agents/topic_analysis.py` with a working agent

---

## Task 5: Implement Category Breakdown Agent

**Objective:**
Create the Category Breakdown Agent following the Topic Analysis Agent pattern.

**Steps:**

1. In `app/agents/category_breakdown.py`, create a class `CategoryBreakdownAgent`.
2. Implement a `process()` method that:
    - Accepts the output from Topic Analysis Agent
    - Calls LMStudioService to break down the prompt into categories
    - Returns a structured result (define a new Pydantic model if needed)
3. Handle errors and document the code.

**Deliverables:**

- `app/agents/category_breakdown.py` with a working agent

---

## Task 6: Implement Iterative Refinement Agent

**Objective:**
Build the Iterative Refinement Agent to enhance prompt sections.

**Steps:**

1. In `app/agents/iterative_refinement.py`, create a class `IterativeRefinementAgent`.
2. Implement a `process()` method that:
    - Accepts input from the Category Breakdown Agent
    - Enhances each section using LMStudioService
    - Returns a structured result
3. Add error handling and docstrings.

**Deliverables:**

- `app/agents/iterative_refinement.py` with a working agent

---

## Task 7: Implement Research Integration Agent

**Objective:**
Build an agent that incorporates external research data.

**Steps:**

1. In `app/agents/research_integration.py`, create a class `ResearchIntegrationAgent`.
2. Implement a `process()` method that:
    - Accepts input from the Iterative Refinement Agent
    - Calls a (stubbed) research service to fetch web and academic data
    - Integrates this data into the prompt
    - Returns a structured result
3. Document the code.

**Deliverables:**

- `app/agents/research_integration.py` with a working agent

---

## Task 8: Implement CrewAI Orchestration Layer

**Objective:**
Wire up all agents in a CrewAI workflow.

**Steps:**

1. In `app/orchestrator/crew.py`, create a class `PromptEnhancerCrew`.
2. Load agent/task configs from YAML files in `config/`.
3. Instantiate all agents and define CrewAI tasks for each.
4. Implement a method `enhance_prompt()` that:
    - Accepts a `PromptRequest`
    - Runs the agents sequentially
    - Collects and returns all intermediate and final results

**Deliverables:**

- `app/orchestrator/crew.py` with a working orchestration class

---

## Task 9: Implement FastAPI Web API

**Objective:**
Create a REST API for prompt enhancement.

**Steps:**

1. In `app/main.py`, set up a FastAPI app.
2. Implement the `/api/enhance-prompt` POST endpoint.
    - Accepts a JSON prompt
    - Calls the orchestration layer
    - Returns results and logs
3. Mount static files for the frontend.

**Deliverables:**

- `app/main.py` with a working API

---

## Task 10: Build Basic Web User Interface

**Objective:**
Create a simple HTML/JS frontend for prompt submission and result display.

**Steps:**

1. In `app/static/index.html`, create a form for prompt entry.
2. Add a button to submit the prompt via AJAX to the API.
3. Display processing status and results.
4. Add minimal CSS for usability.

**Deliverables:**

- `app/static/index.html` and related assets

---

## Task 11: Add Research Tools Integration

**Objective:**
Stub out a research service for web and academic queries.

**Steps:**

1. In `app/services/research.py`, create a class `ResearchService`.
2. Implement stub methods for:
    - Web search (returns dummy data)
    - Academic search (returns dummy data)
3. Integrate this service into the Research Integration Agent.

**Deliverables:**

- `app/services/research.py` with stubbed methods

---

## Task 12: Write Unit Tests for Agents

**Objective:**
Ensure agent logic is correct and robust.

**Steps:**

1. In `tests/test_agents.py`, write unit tests for:
    - Topic Analysis Agent
    - Category Breakdown Agent
    - Iterative Refinement Agent
    - Research Integration Agent
2. Use mock objects for LMStudioService and ResearchService.

**Deliverables:**

- `tests/test_agents.py` with passing tests

---

## Task 13: Dockerize the Application

**Objective:**
Create a Dockerfile for easy deployment.

**Steps:**

1. Write a `Dockerfile` that:
    - Uses a Python base image
    - Installs dependencies
    - Copies the app code
    - Exposes port 8000
    - Runs the app with Uvicorn
2. Add a `.dockerignore` file.

**Deliverables:**

- `Dockerfile` and `.dockerignore`

---

## Task 14: Write Developer Documentation

**Objective:**
Document setup, usage, and development practices.

**Steps:**

1. Write a `README.md` covering:
    - Setup instructions
    - How to run the app
    - API usage
    - How to add new agents
2. Add comments and docstrings throughout the codebase.

**Deliverables:**

- `README.md` and in-code documentation

---

**Tip:**
Each task can be assigned as a separate ticket or PR.
If you use an AI agent to implement, give it one task at a time, review the output, then proceed to the next.

---

Would you like these tasks as individual markdown files, or is this format sufficient?

