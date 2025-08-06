# auth_app/tests/test_registration.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationAPITest(APITestCase):

    url = '/api/register/'

    def test_registration_success(self):
        data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
            "confirmed_password": "testpassword123"
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='testuser@example.com').exists())

    def test_registration_missing_field(self):
        # Korrigiert: Stellt sicher, dass das E-Mail-Feld fehlt
        data = {
            "password": "testpassword123",
            "confirmed_password": "testpassword123"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data) # Stellt sicher, dass das Feld als fehlend gemeldet wird

    def test_registration_duplicate_username(self):
        # Korrigiert: Die URL ist der korrekte Login-Endpunkt
        login_url = '/api/login/'
        data = {
            'email': 'existinguser@example.com',
            'password': 'testpassword123',
            'confirmed_password': 'testpassword123'
        }
        self.client.post(self.url, data, format='json')

        # Testet die Registrierung eines neuen Benutzers mit demselben Benutzernamen (generiert aus der E-Mail)
        data = {
            'email': 'existinguser@newdomain.com',
            'password': 'testpassword123',
            'confirmed_password': 'testpassword123'
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # KORRIGIERT: Überprüft, ob der Fehler im 'non_field_errors'-Feld enthalten ist
        self.assertIn('non_field_errors', response.data)
        self.assertIn('A user with this username already exists.', response.data['non_field_errors'])

    def test_registration_password_mismatch(self):
        data = {
            "email": "mismatch@example.com",
            "password": "password123",
            "confirmed_password": "password456"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Passwords do not match', str(response.data))

    def test_registration_email_is_case_insensitive(self):
        # Erstellt einen Benutzer mit einer bestimmten E-Mail
        User.objects.create_user(username='existinguser', email='ExistingUser@example.com', password='testpassword123')
        
        # Versucht, einen neuen Benutzer mit derselben E-Mail (andere Groß-/Kleinschreibung) zu registrieren
        data = {
            "email": "existinguser@example.com",
            "password": "newpassword123",
            "confirmed_password": "newpassword123"
        }
        response = self.client.post(self.url, data, format='json')
        
        # KORREKTUR: Die Assertion wird auf 400 Bad Request geändert, 
        # weil die API die Registrierung korrekt ablehnt.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Email already exists', str(response.data))
