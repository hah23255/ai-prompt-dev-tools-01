import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestWebSocket(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_websocket_enhance_prompt_success(self):
        with self.client.websocket_connect("/ws/enhance-prompt") as websocket:
            websocket.send_json({"prompt": "Explain how transformer models work in NLP and their applications."})
            response = websocket.receive_json()
            self.assertEqual(response["status"], "complete")
            self.assertIn("enhanced_prompt", response)

    def test_websocket_enhance_prompt_invalid_data(self):
        with self.client.websocket_connect("/ws/enhance-prompt") as websocket:
            websocket.send_json({"prompt": ""})
            response = websocket.receive_json()
            self.assertEqual(response["status"], "error")
            self.assertIn("Invalid request data", response["message"])