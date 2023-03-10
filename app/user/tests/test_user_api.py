"""
Tests for User API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """Test public faetures of zUser APi"""

    def setUp(self):
        self.client = APIClient()
    def test_create_user_success(self):
        """Test creating creatin user is success"""
        payload = {
            'email': 'test@example.com',
            'password': 'test@123',
            'name': 'test name'
        }
        res = self.client.post(CREATE_USER_URL,payload)

        self.assertAlmostEqual(res.status_code,status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password',res.data)
    def test_user_with_email_exists_error(self):
        """test error returned if email already exists"""
        payload = {
            'email': 'test@example.com',
            'password': 'test@123',
            'name': 'test name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
    def test_password_too_short_error(self):
        payload = {
            'email': 'test12345@example.com',
            'password': 'tes',
            'name': 'test name'
        }
        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        user_details = {
            'name': 'testing',
            'email': 'test@example.com',
            'password': 'test-api-pass',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL,payload)
        print(res.data)
        self.assertIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
    def test_create_token_bad_credentials(self):
        create_user(email='test@example.com', password='goodpass')

        payload = {'email':'test@example.com', 'password':'badpass'}

        res = self.client.post(TOKEN_URL,payload)
        print(res.data)
        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
    def test_create_token_blank_password(self):
        payload = {'email':'test@example.com', 'password':''}

        res = self.client.post(TOKEN_URL,payload)

        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password = 'test21234',
            name='test user api'

        )
        self.client =APIClient()
        self.client.force_authenticate(user=self.user)
    def test_retrieve_profile_success(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,{
            'email':self.user.email,
            'name': self.user.name,
        })
    def test_post_me_not_allowed(self):
        res = self.client.post(ME_URL,{})

        self.assertEqual(res.status_code,status.HTTP_405_METHOD_NOT_ALLOWED)
    def test_update_user_profile(self):
        payload = { 'name':'updated name', 'password':'updated_password'}

        res = self.client.patch(ME_URL,payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name,payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code,status.HTTP_200_OK)
