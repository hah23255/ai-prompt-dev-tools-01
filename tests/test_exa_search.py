import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crewai_tools import EXASearchTool
from app.models.base import BaseRequest

class TestEXASearchTool(unittest.TestCase):
    def setUp(self):
        import os
        from unittest.mock import patch
        
        # Mock environment variable loading to simulate EXA_API_KEY availability
        with patch.dict('os.environ', {'EXA_API_KEY': 'test_api_key_from_env'}):
            api_key = os.environ.get('EXA_API_KEY')
            self.tool = EXASearchTool(api_key=api_key)


    def tearDown(self):
        pass
        
    def test_search_valid_query(self):
        """Test EXASearchTool with a valid query"""
        query = "AI advancements in 2025"
        # Mock the _run method to return a successful result
        with patch.object(self.tool, '_run') as mock_run:
            mock_run.return_value = {"content": "Mock content", "source": "Mock source"}
            result = self.tool.run(query)

        self.assertIsInstance(result, dict)
        self.assertIn("content", result)
        self.assertTrue(len(result["content"]) > 0)
        self.assertIn("source", result)
        self.assertTrue(len(result["source"]) > 0)
        mock_run.assert_called_once_with(query)
        
    def test_search_invalid_query(self):
        """Test EXASearchTool with an invalid query"""
        query = ""
        # Mock the _run method to raise a ValueError
        with patch.object(self.tool, '_run') as mock_run:
            mock_run.side_effect = ValueError("Invalid query")
            with self.assertRaises(ValueError):
                self.tool.run(query)
        mock_run.assert_called_once_with(query)
            
    def test_search_api_error_handling(self):
        """Test EXASearchTool error handling when API fails"""
        # Mock the _run method to raise an Exception
        with patch.object(self.tool, '_run') as mock_run:
            mock_run.side_effect = Exception("API Error")
            with self.assertRaises(Exception) as context:
                self.tool.run("test query")

            self.assertEqual(str(context.exception), "API Error")
        mock_run.assert_called_once_with("test query")

if __name__ == '__main__':
    unittest.main()