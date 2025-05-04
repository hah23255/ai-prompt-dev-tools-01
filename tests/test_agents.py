import unittest
import os
from unittest.mock import MagicMock, patch
from app.agents.topic_analysis import TopicAnalysisAgent
from app.models.prompt import PromptRequest, TopicAnalysisResult
from app.services.lmstudio import LMStudioService

class TestTopicAnalysisAgent(unittest.TestCase):
    
    def setUp(self):
        # Mock LMStudio service
        self.mock_lmstudio = MagicMock(spec=LMStudioService)
        self.mock_lmstudio.generate_completion.return_value = '''
        {
            "core_topics": ["AI", "Prompt Engineering", "NLP"],
            "domain_classification": "technology",
            "complexity_level": 7,
            "key_entities": ["GPT", "BERT", "Transformers"]
        }
        '''
        
        # Create agent config
        self.agent_config = {
            "role": "Topic Analysis Specialist",
            "goal": "Analyze topics",
            "backstory": "Expert in topic analysis",
            "verbose": True,
            "allow_delegation": False
        }
        
        # Create agent
        self.agent = TopicAnalysisAgent(
            config=self.agent_config,
            lmstudio_service=self.mock_lmstudio
        )
        
    def test_process_valid_prompt(self):
        # Create test prompt
        prompt_request = PromptRequest(
            request_id="test-123",
            content="Explain how transformer models work in NLP and their applications."
        )
        
        # Process prompt
        result = self.agent.process(prompt_request)
        
        # Check result
        self.assertIsInstance(result, TopicAnalysisResult)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.core_topics, ["AI", "Prompt Engineering", "NLP"])
        self.assertEqual(result.domain_classification, "technology")
        self.assertEqual(result.complexity_level, 7)
        self.assertEqual(result.key_entities, ["GPT", "BERT", "Transformers"])
        
    def test_process_invalid_response(self):
        # Mock invalid JSON response
        self.mock_lmstudio.generate_completion.return_value = "Invalid JSON"
        
        # Create test prompt
        prompt_request = PromptRequest(
            request_id="test-123",
            content="Test prompt"
        )
        
        # Process prompt
        result = self.agent.process(prompt_request)
        
        # Check error handling
        self.assertIsInstance(result, TopicAnalysisResult)
        self.assertEqual(result.status, "error")
        self.assertEqual(result.core_topics, ["error"])
        self.assertEqual(result.domain_classification, "unknown")

# Add similar tests for other agents