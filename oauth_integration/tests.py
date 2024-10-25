from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib import messages
from .models import Instagram, Facebook, ConnectedAccounts

class OAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = self.client.login(username='testuser', password='testpassword')
        self.client.force_login(self.user)

    def test_instagram_authorize(self):
        response = self.client.get(reverse('userauth:instagramAuthorize'))
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertIn('instagram_csrf_token', self.client.session)  # CSRF token is set

    @patch('requests.post')
    @patch('requests.get')
    def test_instagram_callback_success(self, mock_get, mock_post):
        # Mock responses
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'access_token': 'mock_access_token',
            'user_id': 'mock_user_id'
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'username': 'mock_username'
        }

        self.client.session['instagram_csrf_token'] = 'valid_csrf_token'
        response = self.client.get(reverse('userauth:instagramCallback'), {
            'code': 'mock_code',
            'state': 'valid_csrf_token'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Instagram.objects.filter(instagram_id='mock_user_id').exists())

    def test_instagram_callback_csrf_failure(self):
        self.client.session['instagram_csrf_token'] = 'valid_csrf_token'
        response = self.client.get(reverse('userauth:instagramCallback'), {
            'code': 'mock_code',
            'state': 'invalid_csrf_token'
        })

        self.assertEqual(response.status_code, 302)
        self.assertIn(messages.get_messages(self.client), "CSRF validation failed")

    @patch('requests.post')
    def test_facebook_authorize(self):
        response = self.client.get(reverse('userauth:facebookAuthorize'))
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertIn('facebook_csrf_token', self.client.session)  # CSRF token is set

    @patch('requests.post')
    @patch('requests.get')
    def test_facebook_callback_success(self, mock_get, mock_post):
        # Mock responses
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'access_token': 'mock_access_token',
            'expires_in': 3600
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'id': 'mock_user_id',
            'name': 'mock_user_name'
        }

        self.client.session['facebook_csrf_token'] = 'valid_csrf_token'
        response = self.client.get(reverse('userauth:facebookCallback'), {
            'code': 'mock_code',
            'state': 'valid_csrf_token'
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Facebook.objects.filter(facebook_id='mock_user_id').exists())

    def test_facebook_callback_csrf_failure(self):
        self.client.session['facebook_csrf_token'] = 'valid_csrf_token'
        response = self.client.get(reverse('userauth:facebookCallback'), {
            'code': 'mock_code',
            'state': 'invalid_csrf_token'
        })

        self.assertEqual(response.status_code, 302)
        self.assertIn(messages.get_messages(self.client), "CSRF validation failed")

    @patch('requests.post')
    def test_facebook_callback_token_exchange_failure(self, mock_post):
        # Mock a failed token exchange
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = 'Token exchange error'

        self.client.session['facebook_csrf_token'] = 'valid_csrf_token'
        response = self.client.get(reverse('userauth:facebookCallback'), {
            'code': 'mock_code',
            'state': 'valid_csrf_token'
        })

        self.assertEqual(response.status_code, 302)
        self.assertIn(messages.get_messages(self.client), "Error exchanging Facebook code for access token")


