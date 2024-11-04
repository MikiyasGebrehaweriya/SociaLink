# Import necessary modules and classes
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile, TermsAndConditions, ConnectedAccounts
from selenium import webdriver
from django.test import LiveServerTestCase
from .models import (
    UserProfile, Connection, TermsAndConditions, Facebook, Instagram,
    Youtube, Linkedin, Google, X, Tiktok, ConnectedAccounts, Post
)




# ------------------------------- UserAuth Views Tests ----------------------------------------------------------
# Unit Tests
# These tests focus on individual components of the application, such as views.
class UserAuthViewTests(TestCase):
    def setUp(self):
        # Set up a test client and create a test user and related objects
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.userprofile = UserProfile.objects.create(user=self.user, user_code='1234567890123456')
        self.terms = TermsAndConditions.objects.create(user=self.user, accepted=True)
        self.connected_accounts = ConnectedAccounts.objects.create(user=self.user, connected=False)

    def test_sign_in_view(self):
        # Test the sign-in view to ensure it redirects correctly after a successful login
        response = self.client.post(reverse('userauth:signIn'), {'username': 'testuser', 'password': 'password'})
        self.assertEqual(response.status_code, 302)  # Check for a redirect status code
        self.assertRedirects(response, reverse('userauth:completeProfile'))  # Ensure it redirects to the correct URL

    def test_sign_up_view(self):
        # Test the sign-up view for creating a new user
        response = self.client.post(reverse('userauth:signUp'), {'username': 'newuser', 'password1': 'password', 'password2': 'password'})
        self.assertEqual(response.status_code, 200)  # Check for a successful response, assuming the form might have errors

    def test_sign_out_view(self):
        # Test the sign-out functionality
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('userauth:signOut'))
        self.assertEqual(response.status_code, 302)  # Check for a redirect status code
        self.assertRedirects(response, reverse('userauth:signIn'))  # Ensure it redirects to the sign-in page

    def test_terms_and_conditions_view(self):
        # Test the terms and conditions acceptance process
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('userauth:termsAndconditions'))
        self.assertEqual(response.status_code, 302)  # Check for a redirect status code
        self.assertRedirects(response, reverse('userauth:completeProfile'))  # Ensure it redirects correctly

    def test_complete_profile_view(self):
        # Test the profile completion process
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('userauth:completeProfile'))
        self.assertEqual(response.status_code, 302)  # Check for a redirect status code
        self.assertRedirects(response, reverse('profile_management:profile', args=[self.user.username]))  # Ensure it redirects correctly

    def test_report_csp_violation_view(self):
        # Test the CSP violation reporting
        response = self.client.post(reverse('userauth:report_csp_violation'), content_type='application/json', data='{}')
        self.assertEqual(response.status_code, 204)  # Check for a no content status code indicating success


# Integration Tests
# These tests check how different components of the application work together.
class UserAuthIntegrationTests(TestCase):
    def test_full_signup_process(self):
        # Test the entire user sign-up process, including user profile creation and terms acceptance
        client = Client()
        response = client.post(reverse('userauth:signUp'), {
            'username': 'integrationuser',
            'password1': 'password',
            'password2': 'password'
        })
        self.assertEqual(response.status_code, 302)  # Check for a redirect status code

        user = User.objects.get(username='integrationuser')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())  # Ensure user profile is created
        self.assertFalse(TermsAndConditions.objects.filter(user=user, accepted=True).exists())  # Ensure terms are not yet accepted

        # Simulate terms acceptance
        client.login(username='integrationuser', password='password')
        response = client.post(reverse('userauth:termsAndconditions'))
        self.assertEqual(response.status_code, 302)  # Check for a redirect status code
        self.assertTrue(TermsAndConditions.objects.filter(user=user, accepted=True).exists())  # Ensure terms are accepted


# System Tests
# These tests involve testing the application as a whole, often using tools like Selenium to test the user interface.
class UserAuthSystemTests(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_sign_in_page_title(self):
        self.browser.get(self.live_server_url + reverse('userauth:signIn'))
        print(self.browser.current_url)  # Print the current URL for debugging
        print(self.browser.title)  # Print the actual title for debugging
        self.assertIn('userauth:signIn', self.browser.title)  # Check that the page title contains 'Sign In'



# ------------------------------- UserProfile Model Tests ----------------------------------------------------------
class UserProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_user_profile_creation(self):
        profile = UserProfile.objects.create(user=self.user, fullName='Test User')
        self.assertEqual(profile.user.username, 'testuser')
        self.assertEqual(profile.fullName, 'Test User')

class ConnectionModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')

    def test_connection_creation(self):
        connection = Connection.objects.create(user=self.user1, connected_user=self.user2)
        self.assertEqual(connection.user.username, 'user1')
        self.assertEqual(connection.connected_user.username, 'user2')

    def test_unique_together_constraint(self):
        Connection.objects.create(user=self.user1, connected_user=self.user2)
        with self.assertRaises(Exception):
            # Trying to create the same connection should raise an exception due to unique_together constraint
            Connection.objects.create(user=self.user1, connected_user=self.user2)

class TermsAndConditionsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_terms_creation(self):
        terms = TermsAndConditions.objects.create(user=self.user, accepted=True)
        self.assertTrue(terms.accepted)

class SocialMediaModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_facebook_creation(self):
        fb = Facebook.objects.create(user=self.user, facebook_id='12345', facebook_name='Test FB')
        self.assertEqual(fb.facebook_id, '12345')

    def test_instagram_creation(self):
        ig = Instagram.objects.create(user=self.user, instagram_id='12345', instagram_name='Test IG')
        self.assertEqual(ig.instagram_id, '12345')

    # Add similar tests for Youtube, Linkedin, Google, X, Tiktok

class ConnectedAccountsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_connected_accounts_creation(self):
        accounts = ConnectedAccounts.objects.create(user=self.user, facebook=1, instagram=1)
        self.assertEqual(accounts.facebook, 1)
        self.assertEqual(accounts.instagram, 1)

class PostModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_post_creation(self):
        post = Post.objects.create(user=self.user, content_type='text', content='Hello World')
        self.assertTrue(post.is_text_post())
        self.assertEqual(post.content, 'Hello World')

    def test_post_type_methods(self):
        image_post = Post.objects.create(user=self.user, content_type='image')
        video_post = Post.objects.create(user=self.user, content_type='video')

        self.assertTrue(image_post.is_image_post())
        self.assertFalse(image_post.is_video_post())

        self.assertTrue(video_post.is_video_post())
        self.assertFalse(video_post.is_text_post())





















# from django.test import TestCase, Client
# from django.urls import reverse
# from django.contrib.auth.models import User
# from .models import UserProfile, TermsAndConditions, ConnectedAccounts


# class UserAuthTests(TestCase):

#     def setUp(self):
#         # Create a test user
#         self.user = User.objects.create_user(username='testuser', password='testpass')
#         self.client = Client()

#     def test_sign_in_view(self):
#         # Test GET request
#         response = self.client.get(reverse('userauth:signIn'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'userauth/signIn2.html')

#         # Test POST request with valid credentials
#         response = self.client.post(reverse('userauth:signIn'), {'username': 'testuser', 'password': 'testpass'})
#         self.assertRedirects(response, reverse('userauth:termsAndconditions'))

#         # Test POST request with invalid credentials
#         response = self.client.post(reverse('userauth:signIn'), {'username': 'wronguser', 'password': 'wrongpass'})
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "Invalid username or password")

#     def test_sign_up_view(self):
#         # Test GET request
#         response = self.client.get(reverse('userauth:signUp'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'userauth/signUp2.html')

#         # Test POST request with valid data
#         response = self.client.post(reverse('userauth:signUp'), {
#             'username': 'newuser',
#             'password1': 'newpass123',
#             'password2': 'newpass123',
#         })
#         self.assertRedirects(response, reverse('userauth:termsAndconditions'))
#         self.assertTrue(User.objects.filter(username='newuser').exists())
#         self.assertTrue(UserProfile.objects.filter(user__username='newuser').exists())

#     def test_sign_out_view(self):
#         # Log in the user first
#         self.client.login(username='testuser', password='testpass')

#         # Test sign out
#         response = self.client.get(reverse('userauth:signOut'))
#         self.assertRedirects(response, reverse('userauth:signIn'))











# import json
# from django.test import TestCase
# from django.contrib.auth.models import User
# from .models import UserProfile, TermsAndConditions, ConnectedAccounts
# from django.urls import reverse
# from django.contrib.messages import get_messages
# from .forms import MyUserCreationForm  # Assuming you have a custom form


# class UserAuthTests(TestCase):

#     def test_sign_in_success(self):
#         """Test successful user login."""
#         user = User.objects.create_user(username='testuser', password='testpassword')
#         TermsAndConditions.objects.create(user=user, accepted=True)
#         ConnectedAccounts.objects.create(user=user, connected=True) 
#         UserProfile.objects.create(user=user)
#         response = self.client.post(reverse('userauth:signIn'), {'username': 'testuser', 'password': 'testpassword'})
#         self.assertRedirects(response, reverse('profile_management:profile', kwargs={'username': 'testuser'}))
#         self.assertTrue(response.wsgi_request.user.is_authenticated)

#     def test_sign_in_invalid_credentials(self):
#         """Test login with invalid credentials."""
#         User.objects.create_user(username='testuser', password='testpassword')
#         response = self.client.post(reverse('userauth:signIn'), {'username': 'testuser', 'password': 'wrongpassword'})
#         self.assertEqual(response.status_code, 200)  # Should stay on the same page
#         messages = list(get_messages(response.wsgi_request))
#         self.assertEqual(len(messages), 1)
#         self.assertEqual(str(messages[0]), "Invalid username or password")

#     def test_sign_in_user_does_not_exist(self):
#         """Test login with a non-existent user."""
#         response = self.client.post(reverse('userauth:signIn'), {'username': 'nonexistentuser', 'password': 'somepassword'})
#         self.assertEqual(response.status_code, 200)
#         messages = list(get_messages(response.wsgi_request))
#         self.assertEqual(len(messages), 1)
#         self.assertEqual(str(messages[0]), "User does not exist")

#     # def test_sign_up_success(self):
#     #     """Test successful user registration."""
#     #     response = self.client.post(reverse('userauth:signUp'), {'username': 'testuser', 'password': 'testpassword'})
#     #     self.assertRedirects(response, reverse('userauth:termsAndconditions'))
#     #     self.assertTrue(User.objects.filter(username='testuser').exists())
#     #     user = User.objects.get(username='testuser')
#     #     self.assertTrue(UserProfile.objects.filter(user=user).exists())

#     def test_sign_up_form_errors(self):
#         """Test form validation errors during signup."""
#         response = self.client.post(reverse('userauth:signUp'), {'username': 'testuser'})  # Missing password
#         self.assertEqual(response.status_code, 200)
#         messages = list(get_messages(response.wsgi_request))
#         self.assertTrue(len(messages) > 0)  # Should have at least one error message

#     def test_sign_out(self):
#         """Test user logout."""
#         user = User.objects.create_user(username='testuser', password='testpassword')
#         self.client.login(username='testuser', password='testpassword')  # Log in the user
#         response = self.client.get(reverse('userauth:signOut'))
#         self.assertRedirects(response, reverse('userauth:signIn'))
#         self.assertFalse(response.wsgi_request.user.is_authenticated)

#     def test_terms_and_conditions_acceptance(self):
#         """Test accepting terms and conditions."""
#         user = User.objects.create_user(username='testuser', password='testpassword')
#         self.client.login(username='testuser', password='testpassword')
#         response = self.client.post(reverse('userauth:termsAndconditions'))
#         self.assertRedirects(response, reverse('userauth:completeProfile'))
#         self.assertTrue(TermsAndConditions.objects.filter(user=user, accepted=True).exists())

#     def test_complete_profile(self):
#         """Test completing the user profile."""
#         user = User.objects.create_user(username='testuser', password='testpassword')
#         self.client.login(username='testuser', password='testpassword')
#         # Ensure the required objects exist before accessing completeProfile
#         TermsAndConditions.objects.create(user=user, accepted=True)
#         ConnectedAccounts.objects.create(user=user, connected=True)
#         UserProfile.objects.create(user=user)  # Create a UserProfile object
#         response = self.client.post(reverse('userauth:completeProfile'))
#         self.assertRedirects(response, reverse('profile_management:profile', kwargs={'username': 'testuser'}))
#         connected_accounts = ConnectedAccounts.objects.get(user=user)
#         self.assertTrue(connected_accounts.connected)

#     def test_report_csp_violation(self):
#         """Test CSP violation reporting."""
#         report_data = {"csp-report": {"document-uri": "http://example.com"}}
#         response = self.client.post(
#             reverse('userauth:report_csp_violation'), 
#             json.dumps(report_data), 
#             content_type='application/json'
#         )
#         self.assertEqual(response.status_code, 204)  # Expecting a 204 No Content
        
        
        
        
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