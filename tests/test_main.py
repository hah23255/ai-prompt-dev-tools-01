import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_enhance_prompt_valid_data():
    response = client.post(
        "/api/enhance-prompt",
        json={
            "prompt": "Explain how transformer models work in NLP and their applications.",
            "context": {}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert isinstance(data["processing_time"], float)
    assert "enhanced_prompt" in data
    assert "processing_details" in data

def test_enhance_prompt_invalid_data():
    response = client.post(
        "/api/enhance-prompt",
        json={
            "prompt": "",
            "context": {}
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "Invalid request data"

def test_enhance_prompt_internal_error():
    # Mock an internal error in the enhance_prompt method
    with pytest.raises(Exception):
        client.post(
            "/api/enhance-prompt",
            json={
                "prompt": "Explain how transformer models work in NLP and their applications.",
                "context": {}
            }
        )