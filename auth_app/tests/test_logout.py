

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

@pytest.mark.django_db
class TestLogoutView:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@example.com", password="test1234", username="testuser")
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.refresh_token = str(self.refresh)

    def test_logout_success(self):
        self.client.cookies["refresh_token"] = self.refresh_token
        response = self.client.post("/api/logout/")
        assert response.status_code == status.HTTP_200_OK
        assert "detail" in response.data
        assert "refresh_token" in response.cookies
        assert response.cookies["refresh_token"].value == ""
        assert "access_token" in response.cookies
        assert response.cookies["access_token"].value == ""

    def test_logout_missing_refresh_token(self):
        response = self.client.post("/api/logout/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Refresh token not found in cookies."

    def test_logout_invalid_refresh_token(self):
        self.client.cookies["refresh_token"] = "invalid.token.value"
        response = self.client.post("/api/logout/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Invalid or already blacklisted token."

    def test_logout_reuse_blacklisted_token(self):
        self.client.cookies["refresh_token"] = self.refresh_token
        self.client.post("/api/logout/")
        response = self.client.post("/api/logout/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST