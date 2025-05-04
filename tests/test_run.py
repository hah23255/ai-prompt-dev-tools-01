import unittest
from unittest.mock import patch
from app.run import check_lmstudio_running, main

class TestRun(unittest.TestCase):
    @patch('app.run.requests.get')
    def test_check_lmstudio_running_success(self, mock_get):
        mock_get.return_value.status_code = 200
        self.assertTrue(check_lmstudio_running())

    @patch('app.run.requests.get')
    def test_check_lmstudio_running_failure(self, mock_get):
        mock_get.return_value.status_code = 404
        self.assertFalse(check_lmstudio_running())

    @patch('app.run.subprocess.Popen')
    @patch('app.run.check_lmstudio_running', return_value=False)
    def test_main_starts_lms(self, mock_check, mock_popen):
        main()
        mock_popen.assert_called_once_with(["lms", "server", "start"])