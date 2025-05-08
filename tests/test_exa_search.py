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
        self.tool = EXASearchTool()
        
    def test_search_valid_query(self):
        """Test EXASearchTool with a valid query"""
        query = "AI advancements in 2025"
        result = self.tool.search(query)
        
        self.assertIsInstance(result, dict)
        self.assertIn("content", result)
        self.assertTrue(len(result["content"]) > 0)
        self.assertIn("source", result)
        self.assertTrue(len(result["source"]) > 0)
        
    def test_search_invalid_query(self):
        """Test EXASearchTool with an invalid query"""
        query = ""
        with self.assertRaises(ValueError):
            self.tool.search(query)
            
    def test_search_api_error_handling(self):
        """Test EXASearchTool error handling when API fails"""
        with patch.object(self.tool, '_search_api') as mock_search:
            mock_search.side_effect = Exception("API Error")
            
            with self.assertRaises(Exception) as context:
                self.tool.search("test query")
                
            self.assertEqual(str(context.exception), "API Error")

if __name__ == '__main__':
    unittest.main()