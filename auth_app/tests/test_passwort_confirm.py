from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class PasswordResetConfirmAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="oldpassword123"
        )
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        # Feste URL mit den dynamischen Werten
        self.url = f'/api/password_confirm/{self.uidb64}/{self.token}/'

    def test_password_confirm_success(self):
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
        data = {
            "new_password": "newsecurepassword"
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Both password fields are required.", response.data["detail"])