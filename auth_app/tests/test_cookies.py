import datetime
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class CookieAuthenticationAPITest(APITestCase):
    """
    Test suite for JWT authentication using HTTP-only cookies.

    This class tests the functionality of logging in, refreshing tokens,
    and the security attributes of the cookies.
    """

    def setUp(self):
        """
        Set up a user and URLs for testing.
        """
        self.login_url = "/api/login/"
        self.refresh_url = "/api/token/refresh/"
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            is_active=True
        )

    def test_login_sets_cookies(self):
        """
        Test that a successful login request sets the access and refresh tokens
        as cookies in the response.
        """
        data = {
            "email": self.user.email,
            "password": "testpassword123"
        }
        response = self.client.post(self.login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertNotEqual(response.cookies["access_token"].value, "")
        self.assertNotEqual(response.cookies["refresh_token"].value, "")

    def test_refresh_with_valid_cookie(self):
        """
        Test that a valid refresh token cookie can successfully generate a new
        access token.
        """
        login_data = {
            "email": self.user.email,
            "password": "testpassword123"
        }
        login_response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        refresh_token_cookie = login_response.cookies.get("refresh_token")
        self.assertIsNotNone(refresh_token_cookie)
        refresh_token = refresh_token_cookie.value

        self.client.cookies["refresh_token"] = refresh_token
        response = self.client.post(self.refresh_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)
        self.assertNotEqual(response.cookies["access_token"].value, "")

    def test_refresh_without_cookie(self):
        """
        Test that a token refresh request fails when no refresh token cookie is provided.
        """
        response = self.client.post(self.refresh_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Refresh token not found!")

    def test_refresh_with_invalid_cookie(self):
        """
        Test that a token refresh request fails with an invalid refresh token.
        """
        self.client.cookies["refresh_token"] = "invalid.token.value"
        response = self.client.post(self.refresh_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Refresh token invalid!")
    
    def test_refresh_with_expired_token(self):
        """
        Test that a token refresh request fails with an expired refresh token.
        """
        refresh = RefreshToken.for_user(self.user)
        refresh.set_exp(lifetime=datetime.timedelta(seconds=-1))

        self.client.cookies["refresh_token"] = str(refresh)
        response = self.client.post(self.refresh_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Refresh token invalid!")

    def test_login_cookie_attributes(self):
        """
        Test that the cookies set upon login have the correct security attributes
        (httponly, secure, samesite).
        """
        data = {
            "email": self.user.email,
            "password": "testpassword123"
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        
        access_cookie = response.cookies["access_token"]
        refresh_cookie = response.cookies["refresh_token"]

        self.assertTrue(access_cookie["httponly"])
        self.assertTrue(access_cookie["secure"])
        self.assertEqual(access_cookie["samesite"], "Lax")

        self.assertTrue(refresh_cookie["httponly"])
        self.assertTrue(refresh_cookie["secure"])
        self.assertEqual(refresh_cookie["samesite"], "Lax")
