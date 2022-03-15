from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


class PublicUserApiTests(TestCase):
    """ Tests the users API (public) """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """ Test creating user with valid payload is successful """
        payload = {
            'email': 'test@gmail.com',
            'password': 'TestPass123',
            'name': 'Test name'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        # check status code
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)

        # check password
        self.assertTrue(user.check_password(payload['password']))
        # check password field is not in response
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """ Test creating a user that already exists """
        payload = {
            'email': 'test@outlook.com',
            'password': 'TestPass123',
            'name': 'Test name'
        }

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ Test that password must be more than 5 characters """
        payload = {
            'email': 'test@hotmail.com',
            'password': 'pw',
            'name': 'Test name'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects. \
            filter(email=payload['email']).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """ Test that a token is created for the user """
        payload = {
            'email': 'test@gmail.com',
            'password': 'TestPass'
        }

        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_creds(self):
        """ Test that token is not created if invalid creds are given """
        payload = {
            'email': 'test@gmail.com',
            'password': 'TestPass'
        }
        create_user(**payload)

        payload['password'] = 'NotAValidPass'

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """ Test that token is not created if user doesn't exist """
        payload = {
            'email': 'test@gmail.co.uk',
            'password': 'TestPass'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """ Test that email and password are required """
        res = self.client.post(TOKEN_URL,
                               {'email': 'one', 'password': ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """ Test that authentication is required for users """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """ Test APi requests that requires authentication """

    def setUp(self):
        self.user = create_user(
            email='jdoe@gmail.com',
            password='SecretPass123',
            name='John Doe'
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_profile_success(self):
        """ Test retrieving profile of logged in user """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_method_not_allowed(self):
        """ Test that POST is not allowed on me url """
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """ Test updating the user profile for authenticated user """
        payload = {
            'name': 'John Cena',
            'password': 'MyNewSecretPass123'
        }

        # update user
        res = self.client.patch(ME_URL, payload)

        # refresh user
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)