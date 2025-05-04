<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# how about testing what do we do? with the above

Absolutely! **Testing** is essential for ensuring your system is robust, reliable, and maintainable-especially when multiple agents and services interact. Here’s a breakdown of how to approach testing for the above architecture, tailored for junior developers or AI agents working in small, manageable units.

---

## Testing Plan for the Prompt Enhancer System

### 1. **Unit Testing**

**Goal:**
Test each component (models, agents, services) in isolation to ensure correctness of logic and data handling.

#### a. **Models**

- Test Pydantic models for correct validation and serialization/deserialization.
- Example: Given valid/invalid input data, does the model accept/reject as expected?


#### b. **Agents**

- Mock dependencies (e.g., LMStudioService, ResearchService).
- Test each agent’s `process()` method:
    - Given a sample input, does it produce the expected output?
    - Does it handle malformed input or service errors gracefully?


#### c. **Services**

- Test LMStudioService and ResearchService methods with mocked responses.
- Ensure correct error handling for connection failures or unexpected data.

---

### 2. **Integration Testing**

**Goal:**
Test how components work together in the orchestration layer.

- Simulate a full prompt enhancement flow:
    - Feed a sample prompt through the orchestration layer.
    - Mock agent/service responses as needed.
    - Assert that the final output contains all expected intermediate and final results.
- Test error propagation and recovery (e.g., what happens if an agent fails?).

---

### 3. **API Testing**

**Goal:**
Ensure the FastAPI endpoints work as intended.

- Use `TestClient` from FastAPI to send requests to `/api/enhance-prompt`.
- Test:
    - Valid prompt submission (expect 200 and correct structure).
    - Invalid prompt submission (expect 400 and error message).
    - Edge cases (empty prompt, extremely long prompt, etc.).

---

### 4. **Frontend Testing (Optional for MVP)**

**Goal:**
Check that the web UI interacts correctly with the backend.

- Manual testing: Enter prompts, observe status updates and results.
- Automated (optional): Use Selenium or Playwright for end-to-end tests.

---

## Example: Unit Test for Topic Analysis Agent

```python
import unittest
from unittest.mock import MagicMock
from app.agents.topic_analysis import TopicAnalysisAgent
from app.models.prompt import PromptRequest

class TestTopicAnalysisAgent(unittest.TestCase):
    def setUp(self):
        # Mock LMStudioService
        self.mock_lmstudio = MagicMock()
        self.mock_lmstudio.generate_completion.return_value = '''
        {
            "core_topics": ["AI", "Prompt Engineering"],
            "domain_classification": "technology",
            "complexity_level": 5,
            "key_entities": ["GPT-4"]
        }
        '''
        self.agent = TopicAnalysisAgent(
            config={
                "role": "Topic Analysis Specialist",
                "goal": "Analyze topics",
                "backstory": "Expert",
                "verbose": True,
                "allow_delegation": False
            },
            lmstudio_service=self.mock_lmstudio
        )

    def test_process_valid_prompt(self):
        req = PromptRequest(request_id="1", content="Explain how transformers work.")
        result = self.agent.process(req)
        self.assertEqual(result.core_topics, ["AI", "Prompt Engineering"])
        self.assertEqual(result.domain_classification, "technology")
        self.assertEqual(result.complexity_level, 5)
        self.assertEqual(result.key_entities, ["GPT-4"])

    def test_process_invalid_json(self):
        self.mock_lmstudio.generate_completion.return_value = "not a json"
        req = PromptRequest(request_id="2", content="Test")
        result = self.agent.process(req)
        self.assertEqual(result.status, "error")
```


---

## Example: API Test with FastAPI

```python
from fastapi.testclient import TestClient
from app.main import app

def test_enhance_prompt_api():
    client = TestClient(app)
    response = client.post("/api/enhance-prompt", json={"prompt": "Summarize quantum computing."})
    assert response.status_code == 200
    data = response.json()
    assert "enhanced_prompt" in data
    assert "processing_details" in data
```


---

## How to Organize Tests

- Place all test files in the `tests/` directory.
- Use `test_*.py` naming convention.
- Run all tests with:

```
python -m unittest discover tests
```

or, if using `pytest`:

```
pytest tests/
```


---

## Task Breakdown for Testing

1. **Write unit tests for each agent** (`tests/test_agents.py`)
2. **Write unit tests for each service** (`tests/test_services.py`)
3. **Write integration tests for orchestration** (`tests/test_orchestrator.py`)
4. **Write API endpoint tests** (`tests/test_api.py`)
5. (Optional) **Write frontend end-to-end tests** (`tests/test_frontend.py`)

---

## Acceptance Criteria

- All unit and integration tests pass.
- API returns correct status codes and data.
- Error cases are handled gracefully.
- (Optional) Manual UI testing confirms end-to-end functionality.

---

**Summary:**
Testing should be incremental and parallel to development. Each agent/service gets its own test file, and integration/API tests ensure the whole system works together.
If you want, I can generate example test stubs for any specific agent or service-just let me know!

