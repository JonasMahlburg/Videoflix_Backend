from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.test import APITestCase
from rest_framework import status
from django.core import mail

User = get_user_model()


class PasswordResetAPITest(APITestCase):
    """
    Test suite for the password reset functionality.

    This class tests the `PasswordResetView` and its related logic,
    including sending a reset email and handling different scenarios
    for password reset confirmation.
    """

    def setUp(self):
        """
        Set up a user and necessary data for testing the password reset process.
        """
        self.url = "/api/password_reset/"
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="securepassword123"
        )
        mail.outbox = []
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.confirm_url = f'/api/password_confirm/{self.uidb64}/{self.token}/'

    def test_password_reset_email_not_sent_for_unknown_email(self):
        """
        Test that no email is sent for an unknown email address,
        which is a security measure to prevent user enumeration.
        """
        data = {"email": "unknown@example.com"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_password_reset_sends_email_for_existing_user(self):
        """
        Test that an email is successfully sent to an existing user
        when they request a password reset.
        """
        User.objects.create_user(
            username="resetuser", 
            email="reset@example.com", 
            password="old_password"
        )
        data = {"email": "testuser@example.com"}
        
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            response = self.client.post(self.url, data, format="json")
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn('Password Reset', mail.outbox[0].subject)
            self.assertEqual(mail.outbox[0].to[0], 'testuser@example.com')
            self.assertEqual(len(mail.outbox), 1)

    def test_password_reset_confirm_with_expired_token(self):
        """
        Test that a password reset request fails with an invalid or expired token.
        """
        expired_token_url = f'/api/password_confirm/{self.uidb64}/expired-token/'
        data = {"new_password": "new_password", "confirm_password": "new_password"}
        response = self.client.post(expired_token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

