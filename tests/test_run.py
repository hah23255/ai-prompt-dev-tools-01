import pytest
from unittest.mock import patch
from app.run import main

def test_check_lmstudio_running():
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        assert main.check_lmstudio_running() is True

def test_check_lmstudio_not_running():
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("Connection error")
        assert main.check_lmstudio_running() is False

def test_start_lmstudio_success():
    with patch("subprocess.Popen") as mock_popen, \
         patch("app.run.logger.info") as mock_info:
        main.start_lmstudio()
        mock_popen.assert_called_once_with(["lms", "server", "start"])
        mock_info.assert_called_once_with("LMStudio server started")

def test_start_lmstudio_failure():
    with patch("subprocess.Popen") as mock_popen, \
         patch("app.run.logger.error") as mock_error:
        mock_popen.side_effect = Exception("Failed to start")
        main.start_lmstudio()
        mock_error.assert_called_once_with("Failed to start LMStudio automatically. Please start it manually.")