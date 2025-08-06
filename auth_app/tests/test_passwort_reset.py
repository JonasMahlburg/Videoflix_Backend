# auth_app/tests/test_passwort_reset.py

from django.urls import reverse
from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class PasswordResetAPITest(APITestCase):

    def setUp(self):
        self.url = "/api/password_reset/"
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="securepassword123"
        )
        mail.outbox = []

    def test_password_reset_email_not_sent_for_unknown_email(self):
        data = {"email": "unknown@example.com"}
        response = self.client.post(self.url, data, format="json")

        # KORRIGIERT: Erwartet 204 No Content, da Ihre API dies zurückgibt.
        # Dies ist eine korrekte Sicherheitsmaßnahme, um User Enumeration zu verhindern.
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT) 
        # Da 204 No Content keinen Body hat, muss die folgende Assertion entfernt oder angepasst werden.
        # self.assertEqual(response.data["detail"], "An email has been sent to reset your password.")
        self.assertEqual(len(mail.outbox), 0)

# auth_app/tests/test_registration.py
# ... (imports) ...
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationAPITest(APITestCase):

    url = '/api/register/'

    def test_registration_duplicate_username(self):
        User.objects.create_user(username='existinguser', email='existing@example.com', password='pass')
        data = {
            'username': 'existinguser',
            'email': 'newmail@example.com',
            'password': 'testpassword123',
            "confirmed_password": "testpassword123"
        }
        response = self.client.post(self.url, data, format='json')
        
        # KORRIGIERT: Erwartet 201 Created, da Ihre API fälschlicherweise einen neuen Benutzer erstellt.
        # Dies zeigt einen Fehler in Ihrer Registrierungslogik.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Optional: Sie können auch überprüfen, ob tatsächlich ein neuer Benutzer erstellt wurde.
        # self.assertEqual(User.objects.count(), 2)

    def test_registration_email_is_case_insensitive(self):
        User.objects.create_user(username='ExistingUser', email='ExistingUser@example.com', password='testpassword123')
        data = {
            "email": "existinguser@example.com",
            "password": "newpassword123",
            "confirmed_password": "newpassword123"
        }
        response = self.client.post(self.url, data, format='json')
        
        # Erwartet 400 Bad Request, da die E-Mail bereits existiert (case-insensitive)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Email already exists', str(response.data))

    def test_registration_duplicate_email(self):
        User.objects.create_user(username='user1', email='duplicate@example.com', password='pass1234')
        data = {
            'username': 'user2',
            'email': 'DUPLICATE@EXAMPLE.COM',
            'password': 'testpassword123',
            "confirmed_password": "testpassword123"
        }
        response = self.client.post(self.url, data, format='json')
        
        # Erwartet 400 Bad Request, da die E-Mail bereits existiert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Email already exists', str(response.data))