

import pytest
from django.urls import reverse
from django.core import mail
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestPasswordReset:

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/password_reset/"
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="securepassword123"
        )

    def test_password_reset_email_sent(self):
        data = {"email": "testuser@example.com"}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "An email has been sent to reset your password."
        assert len(mail.outbox) == 1
        assert "Passwort zurücksetzen" in mail.outbox[0].subject
        assert self.user.email in mail.outbox[0].to

    def test_password_reset_email_not_sent_for_unknown_email(self):
        data = {"email": "unknown@example.com"}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "An email has been sent to your password."
        assert len(mail.outbox) == 0
    
    #----------------------------------reset password without enumeration catch test ----------------------------------

    # def test_password_reset_email_not_sent_for_unknown_email(self):
    #     data = {"email": "unknown@example.com"}
    #     response = self.client.post(self.url, data, format="json")

    #     assert response.status_code == status.HTTP_400_BAD_REQUEST
    #     assert response.data["detail"] == "Your Email is not in our Database"
    #     assert len(mail.outbox) == 0

    #-------------------------------------------------------------------------------------------------------------

    def test_password_reset_missing_email_field(self):
        data = {}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.data
        assert response.data["detail"] == "Email field is required."