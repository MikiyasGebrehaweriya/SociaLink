from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class SignUpViewTests(TestCase):
    def test_signup_view_get(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userauth/signUp2.html')

    def test_signup_view_post_valid(self):
        User = get_user_model()
        data = {
            'username': 'testuser',
            'password1': 'password123',
            'password2': 'password123',
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_signup_view_post_invalid(self):
        data = {
            'username': 'testuser',
            'password1': 'password123',
            'password2': 'password321',  # Mismatched passwords
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'user_form', 'password2', "The two password fields didn’t match.")
