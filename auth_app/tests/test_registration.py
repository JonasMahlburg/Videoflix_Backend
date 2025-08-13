from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()


class RegistrationAPITest(APITestCase):
    """
    Test suite for user registration and activation.

    This class tests the `RegistrationView` and related serializer logic,
    covering both successful and unsuccessful registration attempts,
    as well as the account activation process via email link.
    """

    url = '/api/register/'

    def test_registration_success(self):
        """
        Test that a valid registration request creates a new user and
        returns a 201 Created status code.
        """
        data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
            "confirmed_password": "testpassword123"
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='testuser@example.com').exists())

    def test_registration_missing_field(self):
        """
        Test that a registration request fails if a required field is missing.
        """
        data = {
            "password": "testpassword123",
            "confirmed_password": "testpassword123"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_registration_duplicate_username(self):
        """
        Test that registration fails if the derived username from the email
        already exists in the database.
        """
        data = {
            'email': 'existinguser@example.com',
            'password': 'testpassword123',
            'confirmed_password': 'testpassword123'
        }
        self.client.post(self.url, data, format='json')

        data = {
            'email': 'existinguser@newdomain.com',
            'password': 'testpassword123',
            'confirmed_password': 'testpassword123'
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertIn('A user with this username already exists.', response.data['non_field_errors'])

    def test_registration_password_mismatch(self):
        """
        Test that registration fails if the 'password' and 'confirmed_password'
        fields do not match.
        """
        data = {
            "email": "mismatch@example.com",
            "password": "password123",
            "confirmed_password": "password456"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Passwords do not match', str(response.data))

    def test_registration_email_is_case_insensitive(self):
        """
        Test that registration fails if the email address, regardless of case,
        already exists in the database.
        """
        User.objects.create_user(username='existinguser', email='ExistingUser@example.com', password='testpassword123')

        data = {
            "email": "existinguser@example.com",
            "password": "newpassword123",
            "confirmed_password": "newpassword123"
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Email already exists', str(response.data))

    def test_registration_sends_activation_email(self):
        """
        Test that a successful registration triggers the sending of an
        activation email.
        """
        data = {
            "email": "newuser@example.com",
            "password": "testpassword123",
            "confirmed_password": "testpassword123"
        }
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            response = self.client.post(self.url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn('Welcome to Videoflix', mail.outbox[0].subject)
            self.assertIn('newuser', mail.outbox[0].body)
            self.assertIn('activate', mail.outbox[0].body)
    
    def test_password_mismatch_fails_registration(self):
        """
        A duplicate test to confirm password mismatch validation logic.
        This test is redundant but serves as an explicit check for the
        'confirmed_password' field.
        """
        data = {
            "email": "mismatch@example.com",
            "password": "password123",
            "confirmed_password": "differentpassword"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Passwords do not match', str(response.data))

    def test_user_activation_success(self):
        """
        Test that a user account is successfully activated with a valid UID and token.
        """
        user = User.objects.create_user(username="inactiveuser", email="inactive@example.com", password="pass", is_active=False)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_url = f'/api/activate/{uidb64}/{token}/'
        response = self.client.get(activation_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)
    
    def test_user_activation_with_invalid_token(self):
        """
        Test that account activation fails if an invalid token is provided.
        """
        user = User.objects.create_user(username="inactiveuser", email="inactive@example.com", password="pass", is_active=False)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        invalid_token_url = f'/api/activate/{uidb64}/invalid-token/'
        response = self.client.get(invalid_token_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertFalse(user.is_active)