import json
from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile, TermsAndConditions, ConnectedAccounts
from django.urls import reverse
from django.contrib.messages import get_messages
from .forms import MyUserCreationForm  # Assuming you have a custom form


class UserAuthTests(TestCase):

    def test_sign_in_success(self):
        """Test successful user login."""
        user = User.objects.create_user(username='testuser', password='testpassword')
        TermsAndConditions.objects.create(user=user, accepted=True)
        ConnectedAccounts.objects.create(user=user, connected=True) 
        UserProfile.objects.create(user=user)
        response = self.client.post(reverse('userauth:signIn'), {'username': 'testuser', 'password': 'testpassword'})
        self.assertRedirects(response, reverse('profile_management:profile', kwargs={'username': 'testuser'}))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_sign_in_invalid_credentials(self):
        """Test login with invalid credentials."""
        User.objects.create_user(username='testuser', password='testpassword')
        response = self.client.post(reverse('userauth:signIn'), {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)  # Should stay on the same page
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Invalid username or password")

    def test_sign_in_user_does_not_exist(self):
        """Test login with a non-existent user."""
        response = self.client.post(reverse('userauth:signIn'), {'username': 'nonexistentuser', 'password': 'somepassword'})
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "User does not exist")

    # def test_sign_up_success(self):
    #     """Test successful user registration."""
    #     response = self.client.post(reverse('userauth:signUp'), {'username': 'testuser', 'password': 'testpassword'})
    #     self.assertRedirects(response, reverse('userauth:termsAndconditions'))
    #     self.assertTrue(User.objects.filter(username='testuser').exists())
    #     user = User.objects.get(username='testuser')
    #     self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_sign_up_form_errors(self):
        """Test form validation errors during signup."""
        response = self.client.post(reverse('userauth:signUp'), {'username': 'testuser'})  # Missing password
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages) > 0)  # Should have at least one error message

    def test_sign_out(self):
        """Test user logout."""
        user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')  # Log in the user
        response = self.client.get(reverse('userauth:signOut'))
        self.assertRedirects(response, reverse('userauth:signIn'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_terms_and_conditions_acceptance(self):
        """Test accepting terms and conditions."""
        user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('userauth:termsAndconditions'))
        self.assertRedirects(response, reverse('userauth:completeProfile'))
        self.assertTrue(TermsAndConditions.objects.filter(user=user, accepted=True).exists())

    def test_complete_profile(self):
        """Test completing the user profile."""
        user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        # Ensure the required objects exist before accessing completeProfile
        TermsAndConditions.objects.create(user=user, accepted=True)
        ConnectedAccounts.objects.create(user=user, connected=True)
        UserProfile.objects.create(user=user)  # Create a UserProfile object
        response = self.client.post(reverse('userauth:completeProfile'))
        self.assertRedirects(response, reverse('profile_management:profile', kwargs={'username': 'testuser'}))
        connected_accounts = ConnectedAccounts.objects.get(user=user)
        self.assertTrue(connected_accounts.connected)

    def test_report_csp_violation(self):
        """Test CSP violation reporting."""
        report_data = {"csp-report": {"document-uri": "http://example.com"}}
        response = self.client.post(
            reverse('userauth:report_csp_violation'), 
            json.dumps(report_data), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 204)  # Expecting a 204 No Content
        
        
        
        
#     from unittest.mock import patch

# # ... (other imports and test class)

#     @patch('qrcode.make_image')  # Mock the qrcode.make_image function
#     def test_sign_up_qr_code(self, mock_make_image):
#         """Test QR code generation during signup."""
#         # ... (your sign up POST request)

#         # Assert that qrcode.make_image was called with the expected arguments
#         mock_make_image.assert_called_once_with(fill_color="#135D66", back_color="#FFF5E0")

#         # Add assertions to check that UserProfile.qr_code is set correctly 
#         # (you might need to adjust the path based on your mocking strategy)
#         user = User.objects.get(username='testuser')
#         user_profile = UserProfile.objects.get(user=user)
#         # Example assertion (adjust the path if needed):
#         expected_qr_code_path = os.path.join(settings.MEDIA_ROOT, 'qrcodes', 'testuser_qr.png')
#         self.assertEqual(user_profile.qr_code, expected_qr_code_path)