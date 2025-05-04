import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime # <-- Add this import
import json

# Assuming these models and agent classes exist
from app.models.prompt import PromptRequest
from app.models.response import TopicAnalysisResult # Assuming you have a result model for Topic Analysis
from app.agents.topic_analysis import TopicAnalysisAgent
# Import other agent test classes if they are in this file

class TestTopicAnalysisAgent(unittest.TestCase):
    def setUp(self):
        # Mock the LMStudioService
        self.mock_lmstudio = MagicMock()
        # Mock the LLM object
        self.mock_llm = MagicMock()
        # Provide a dummy config dictionary
        agent_config = {
            "role": "Topic Analyzer",
            "goal": "Identify core topics, domain, complexity, and key entities from a user prompt.",
            "backstory": "An expert in natural language processing...",
            "verbose": False,
            "allow_delegation": False,
            "max_iter": 15,
            "max_rpm": 100
        }
        # Initialize the TopicAnalysisAgent with the mock service, config, and mock llm
        self.agent = TopicAnalysisAgent(agent_config, self.mock_lmstudio, self.mock_llm)

    def test_process_valid_prompt(self):
        # Mock a valid JSON response from LMStudio
        mock_response_data = {
            "core_topics": ["transformer models", "NLP", "applications"],
            "domain_classification": "Technology",
            "complexity_level": 7,
            "key_entities": ["transformer models", "NLP"]
        }
        self.mock_lmstudio.generate_completion.return_value = json.dumps(mock_response_data)

        # Create test prompt
        prompt_request = PromptRequest(
            request_id="test-123",
            content="Explain how transformer models work in NLP and their applications."
        )

        # Process prompt
        result = self.agent.process(prompt_request)

        # Assertions
        self.assertIsInstance(result, TopicAnalysisResult)
        self.assertEqual(result.status, "success")
        # Note: processing_time and timestamp are set in the agent's process method
        self.assertEqual(result.core_topics, ["transformer models", "NLP", "applications"])
        self.assertEqual(result.domain_classification, "Technology")
        self.assertEqual(result.complexity_level, 7)
        self.assertEqual(result.key_entities, ["transformer models", "NLP"])
        self.assertIsInstance(result.timestamp, datetime) # Check timestamp type

        # Verify LMStudio service was called correctly
        self.mock_lmstudio.generate_completion.assert_called_once()
        # You might want to add assertions about the prompt passed to generate_completion

    def test_process_invalid_response(self):
        # Mock an invalid JSON response
        self.mock_lmstudio.generate_completion.return_value = "Invalid JSON"

        # Create test prompt
        prompt_request = PromptRequest(
            request_id="test-123",
            content="Test prompt"
        )

        # Process prompt - This should now be handled gracefully by the agent's try/except
        result = self.agent.process(prompt_request)

        # Assertions for error handling
        self.assertIsInstance(result, TopicAnalysisResult)
        self.assertEqual(result.status, "error")
        self.assertIn("error", result.core_topics) # Assuming error handling sets default values
        self.assertEqual(result.domain_classification, "unknown")
        self.assertEqual(result.complexity_level, 1)
        self.assertEqual(result.key_entities, [])
        self.assertIsInstance(result.timestamp, datetime)

        # Verify LMStudio service was called correctly
        self.mock_lmstudio.generate_completion.assert_called_once()

# Add other agent test classes here if they are in the same file
# class TestCategoryBreakdownAgent(unittest.TestCase):
#     ...
