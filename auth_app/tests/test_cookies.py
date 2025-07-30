

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestCookieAuth:

    def setup_method(self):
        self.client = APIClient()
        self.login_url = "/api/login/"
        self.refresh_url = "/api/token/refresh/"
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            is_active=True
        )

    def test_login_sets_cookies(self):
        data = {
            "email": self.user.email,
            "password": "testpassword123"
        }
        response = self.client.post(self.login_url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies
        assert response.cookies["access_token"].value != ""
        assert response.cookies["refresh_token"].value != ""

    def test_refresh_with_valid_cookie(self):
        # Erst Login, um Cookies zu erhalten
        login_data = {
            "email": self.user.email,
            "password": "testpassword123"
        }
        login_response = self.client.post(self.login_url, login_data, format="json")
        refresh_token = login_response.cookies.get("refresh_token").value

        self.client.cookies["refresh_token"] = refresh_token
        response = self.client.post(self.refresh_url)

        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.cookies
        assert response.cookies["access_token"].value != ""

    def test_refresh_without_cookie(self):
        response = self.client.post(self.refresh_url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Refresh token not found!"

    def test_refresh_with_invalid_cookie(self):
        self.client.cookies["refresh_token"] = "invalid.token.value"
        response = self.client.post(self.refresh_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == "Refresh token invalid!"