

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_registration_success():
    client = APIClient()
    url = reverse('register')
    data = {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "confirmed_password": "testpassword123"
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(username='testuser').exists()

@pytest.mark.django_db
def test_registration_missing_field():
    client = APIClient()
    url = reverse('register')
    data = {
        'username': 'testuser2',
        # 'email' missing
        'password': 'testpassword123'
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_registration_duplicate_username():
    User.objects.create_user(username='existinguser', email='existing@example.com', password='pass')
    client = APIClient()
    url = reverse('register')
    data = {
        'username': 'existinguser',
        'email': 'newmail@example.com',
        'password': 'testpassword123'
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST