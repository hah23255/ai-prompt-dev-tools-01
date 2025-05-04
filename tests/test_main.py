import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestMain(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_enhance_prompt_success(self):
        response = self.client.post(
            "/api/enhance-prompt",
            json={"prompt": "Explain how transformer models work in NLP and their applications."}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("enhanced_prompt", response.json())

    def test_enhance_prompt_invalid_data(self):
        response = self.client.post(
            "/api/enhance-prompt",
            json={"prompt": ""}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid request data", response.json()["message"])