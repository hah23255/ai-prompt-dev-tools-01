import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestWebSocket(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_websocket_enhance_prompt_success(self):
        with self.client.websocket_connect("/ws/enhance-prompt") as websocket:
            websocket.send_json({"prompt": "Explain how transformer models work in NLP and their applications."})
            
            # Receive messages until the status is 'complete' or 'error'
            response = None
            max_messages = 20 # Prevent infinite loops in case of unexpected behavior
            received_messages = 0
            while received_messages < max_messages:
                response = websocket.receive_json()
                received_messages += 1
                if response.get("status") in ["complete", "error"]:
                    break
            
            self.assertIsNotNone(response, "Did not receive any response from the websocket.")
            self.assertEqual(response.get("status"), "complete", f"Expected status 'complete' but received '{response.get('status')}'. Full response: {response}")
            self.assertIn("enhanced_prompt", response)

    def test_websocket_enhance_prompt_invalid_data(self):
        with self.client.websocket_connect("/ws/enhance-prompt") as websocket:
            websocket.send_json({"prompt": ""})
            
            # Receive messages until the status is 'error'
            response = None
            max_messages = 10 # Prevent infinite loops
            received_messages = 0
            while received_messages < max_messages:
                response = websocket.receive_json()
                received_messages += 1
                if response.get("status") == "error":
                    break

            self.assertIsNotNone(response, "Did not receive any response from the websocket.")
            self.assertEqual(response.get("status"), "error", f"Expected status 'error' but received '{response.get('status')}'. Full response: {response}")
            self.assertIn("message", response)
            self.assertIn("Invalid request data", response.get("message", ""))