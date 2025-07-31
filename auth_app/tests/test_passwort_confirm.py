import pytest
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.test import APIClient
from rest_framework import status


@pytest.mark.django_db
def test_password_confirm_success():
    user = User.objects.create_user(username="testuser", email="test@example.com", password="oldpassword123")
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    client = APIClient()
    response = client.post(f"/api/password_confirm/{uidb64}/{token}/", {
        "new_password": "newsecurepassword",
        "confirm_password": "newsecurepassword"
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data["detail"] == "Your Password has been successfully reset."
    user.refresh_from_db()
    assert user.check_password("newsecurepassword")


@pytest.mark.django_db
def test_password_confirm_mismatch():
    user = User.objects.create_user(username="testuser", email="test@example.com", password="oldpassword123")
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    client = APIClient()
    response = client.post(f"/api/password_confirm/{uidb64}/{token}/", {
        "new_password": "newsecurepassword",
        "confirm_password": "differentpassword"
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Passwords do not match." in response.data["detail"]


@pytest.mark.django_db
def test_password_confirm_invalid_token():
    user = User.objects.create_user(username="testuser", email="test@example.com", password="oldpassword123")
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    invalid_token = "invalid-token"

    client = APIClient()
    response = client.post(f"/api/password_confirm/{uidb64}/{invalid_token}/", {
        "new_password": "newsecurepassword",
        "confirm_password": "newsecurepassword"
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid or expired token." in response.data["detail"]