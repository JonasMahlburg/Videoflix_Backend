from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class LogoutAPITest(APITestCase):
    """
    Test suite for the user logout functionality.

    This class tests the `LogoutView` to ensure that a user can successfully
    log out, which involves blacklisting their refresh token and clearing
    the associated cookies.
    """

    def setUp(self):
        """
        Set up a test user and JWT tokens for the test cases.
        """
        self.url = "/api/logout/"
        self.user = User.objects.create_user(
            email="test@example.com", 
            password="test1234", 
            username="testuser"
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.refresh_token = str(self.refresh)

    def test_logout_success(self):
        """
        Test that a logout request with a valid refresh token successfully
        blacklists the token and clears the cookies.
        """
        self.client.cookies["refresh_token"] = self.refresh_token
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)
        self.assertIn("refresh_token", response.cookies)
        self.assertEqual(response.cookies["refresh_token"].value, "")
        self.assertIn("access_token", response.cookies)
        self.assertEqual(response.cookies["access_token"].value, "")

    def test_logout_missing_refresh_token(self):
        """
        Test that a logout request fails when no refresh token is provided in the cookies.
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Refresh token not found in cookies.", response.data["detail"])

    def test_logout_invalid_refresh_token(self):
        """
        Test that a logout request fails when the refresh token is invalid.
        """
        self.client.cookies["refresh_token"] = "invalid.token.value"
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid or already blacklisted token.", response.data["detail"])

    def test_logout_reuse_blacklisted_token(self):
        """
        Test that attempting to use a blacklisted token for logout fails.
        """
        self.client.cookies["refresh_token"] = self.refresh_token

        first_response = self.client.post(self.url)
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)

        new_client = APIClient()
        new_client.cookies["refresh_token"] = self.refresh_token

        second_response = new_client.post(self.url)

        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid or already blacklisted token.", str(second_response.data))
        