from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from userauth.models import UserProfile, Instagram, Facebook, Connection
from unittest.mock import patch
from django.contrib.messages import get_messages



class UserProfileTests(TestCase):

    def setUp(self):
        # Create a test user and user profile
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user_profile = UserProfile.objects.create(user=self.user)
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

    def test_profile_view(self):
        # Test profile view for the logged-in user
        response = self.client.get(reverse('profile_management:profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userauth/members-page.html')
        self.assertContains(response, self.user.username)

    @patch('requests.get')
    def test_ai_view(self, mock_get):
        # Mock the external API call
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'output': 'Sample AI response'}

        # Test AI view with a POST request
        response = self.client.post(reverse('profile_management:ai'), {'data': 'Sample query'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Sample AI response'})

    def test_members_view(self):
        # Test members view for the logged-in user
        response = self.client.get(reverse('profile_management:members'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userauth/members2.html')




























# from django.test import TestCase
# from unittest.mock import patch
# from .views import fetch_instagram_data, fetch_facebook_data

# class FetchDataTests(TestCase):
    
#     @patch('requests.get')
#     def test_fetch_instagram_data_success(self, mock_get):
#         mock_get.return_value.status_code = 200
#         mock_get.return_value.json.return_value = {'data': 'Instagram data'}

#         result = fetch_instagram_data('mock_token')
#         self.assertEqual(result, {'data': 'Instagram data'})

#     @patch('requests.get')
#     def test_fetch_instagram_data_failure(self, mock_get):
#         mock_get.return_value.status_code = 400

#         result = fetch_instagram_data('mock_token')
#         self.assertIsNone(result)

#     @patch('requests.get')
#     def test_fetch_facebook_data_success(self, mock_get):
#         mock_get.return_value.status_code = 200
#         mock_get.return_value.json.return_value = {'data': 'Facebook data'}

#         result = fetch_facebook_data('mock_token')
#         self.assertEqual(result, {'data': 'Facebook data'})

#     @patch('requests.get')
#     def test_fetch_facebook_data_failure(self, mock_get):
#         mock_get.return_value.status_code = 400

#         result = fetch_facebook_data('mock_token')
#         self.assertIsNone(result)
