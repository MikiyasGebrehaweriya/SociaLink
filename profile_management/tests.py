from django.test import TestCase
from unittest.mock import patch
from .views import fetch_instagram_data, fetch_facebook_data

class FetchDataTests(TestCase):
    
    @patch('requests.get')
    def test_fetch_instagram_data_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'data': 'Instagram data'}

        result = fetch_instagram_data('mock_token')
        self.assertEqual(result, {'data': 'Instagram data'})

    @patch('requests.get')
    def test_fetch_instagram_data_failure(self, mock_get):
        mock_get.return_value.status_code = 400

        result = fetch_instagram_data('mock_token')
        self.assertIsNone(result)

    @patch('requests.get')
    def test_fetch_facebook_data_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'data': 'Facebook data'}

        result = fetch_facebook_data('mock_token')
        self.assertEqual(result, {'data': 'Facebook data'})

    @patch('requests.get')
    def test_fetch_facebook_data_failure(self, mock_get):
        mock_get.return_value.status_code = 400

        result = fetch_facebook_data('mock_token')
        self.assertIsNone(result)
