import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_websocket_enhance_prompt_valid_data():
    with client.websocket_connect("/ws/enhance-prompt") as websocket:
        websocket.send_json({
            "prompt": "Explain how transformer models work in NLP and their applications.",
            "context": {}
        })
        
        response = websocket.receive_json()
        assert response["status"] == "processing"
        assert response["stage"] == "topic_analysis"
        assert response["message"] == "Analyzing prompt topics..."
        
        final_response = websocket.receive_json()
        assert final_response["status"] == "complete"
        assert isinstance(final_response["processing_time"], float)
        assert "enhanced_prompt" in final_response
        assert "processing_details" in final_response

def test_websocket_enhance_prompt_invalid_data():
    with client.websocket_connect("/ws/enhance-prompt") as websocket:
        websocket.send_json({
            "prompt": "",
            "context": {}
        })
        
        response = websocket.receive_json()
        assert response["status"] == "error"
        assert response["message"] == "Invalid request data"

def test_websocket_enhance_prompt_internal_error():
    # Mock an internal error in the enhance_prompt method
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/enhance-prompt") as websocket:
            websocket.send_json({
                "prompt": "Explain how transformer models work in NLP and their applications.",
                "context": {}
            })