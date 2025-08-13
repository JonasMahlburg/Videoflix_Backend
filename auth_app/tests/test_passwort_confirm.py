from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class PasswordResetConfirmAPITest(APITestCase):
    """
    Test suite for the password reset confirmation functionality.

    This class tests the `PasswordResetConfirmView` to ensure that a user can
    successfully confirm a password reset and set a new password, while also
    handling various failure scenarios like invalid tokens or mismatched passwords.
    """

    def setUp(self):
        """
        Set up a test user, UID, and token for password reset confirmation.
        """
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="oldpassword123"
        )
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.url = f'/api/password_confirm/{self.uidb64}/{self.token}/'

    def test_password_confirm_success(self):
        """
        Test that a valid password reset token and matching passwords
        successfully reset the user's password.
        """
        data = {
            "new_password": "newsecurepassword",
            "confirm_password": "newsecurepassword"
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Your Password has been successfully reset.")
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newsecurepassword"))

    def test_password_confirm_mismatch(self):
        """
        Test that the password reset fails if the new passwords do not match.
        """
        data = {
            "new_password": "newsecurepassword",
            "confirm_password": "differentpassword"
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Passwords do not match.", response.data["detail"])
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("oldpassword123"))

    def test_password_confirm_invalid_token(self):
        """
        Test that the password reset fails with an invalid or expired token.
        """
        invalid_token_url = f'/api/password_confirm/{self.uidb64}/invalid-token/'
        
        data = {
            "new_password": "newsecurepassword",
            "confirm_password": "newsecurepassword"
        }
        response = self.client.post(invalid_token_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid or expired token.", response.data["detail"])
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("oldpassword123"))

    def test_password_confirm_invalid_uid(self):
        """
        Test that the password reset fails if the user ID (uidb64) is invalid.
        """
        invalid_uid_url = f'/api/password_confirm/invalid-uid/{self.token}/'
        
        data = {
            "new_password": "newsecurepassword",
            "confirm_password": "newsecurepassword"
        }
        response = self.client.post(invalid_uid_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid user.", response.data["detail"])
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("oldpassword123"))

    def test_password_confirm_missing_fields(self):
        """
        Test that the password reset fails if one of the password fields is missing.
        """
        data = {
            "new_password": "newsecurepassword"
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Both password fields are required.", response.data["detail"])
