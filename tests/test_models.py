import pytest
# Change this import slightly for clarity, although the core issue is below
# from pydantic_core import ValidationError
from pydantic import ValidationError # <-- Import ValidationError directly from pydantic

from app.models.base import BaseResponse, BaseRequest

def test_base_response_valid_data():
    data = {
        "status": "success",
        "processing_time": 0.5,
        "timestamp": "2023-10-01T12:00:00"
    }
    response = BaseResponse(**data)
    assert response.status == "success"
    assert response.processing_time == 0.5
    assert response.timestamp.isoformat() == data["timestamp"]

# Note: For Pydantic V2, validation errors often raise ValidationError directly,
# not ValueError for type/format issues on field assignment.
# You might need to adjust these tests depending on expected Pydantic behavior.
# Let's assume ValidationError is expected for these too.
def test_base_response_invalid_data():
    with pytest.raises(ValidationError): # <-- Change from ValueError to ValidationError
        BaseResponse(status="error", processing_time=-1, timestamp="invalid")

def test_base_request_valid_data():
    data = {
        "request_id": "req123",
        "timestamp": "2023-10-01T12:00:00"
    }
    request = BaseRequest(**data)
    assert request.request_id == "req123"
    assert request.timestamp.isoformat() == data["timestamp"]

def test_base_request_invalid_data():
    with pytest.raises(ValidationError): # <-- Change from ValueError to ValidationError
        BaseRequest(request_id="", timestamp="invalid")

def test_base_response_required_fields():
    # Use the imported ValidationError class directly
    with pytest.raises(ValidationError):
        BaseResponse(processing_time=0.5)

def test_base_request_required_fields():
    # Use the imported ValidationError class directly
    with pytest.raises(ValidationError):
        BaseRequest(timestamp="2023-10-01T12:00:00")