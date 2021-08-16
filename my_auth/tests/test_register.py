from django.urls import reverse
from rest_framework.test import APIClient

from core.MyTestCase import MyTestCase

from .factories import DEFAULT_PASSWORD, CustomUserFactory


class Test_Register_View(MyTestCase):

    def test_correct_login_no_data(self):
        """Testing a legitimate register."""
        data = {'email': 'test@email.com', 'password': 'pass4test'}

        client = APIClient()
        url = reverse('register')
        response = client.post(url, data, format='json')

        self.assertResponse201(response)
        responseData = self.loadJSONSafely(response)
        self.assertTrue('access_token' in responseData)

    def test_correct_register_many_other_users(self):
        """Testing a legitimate registration with one other user."""
        for i in range(100):
            CustomUserFactory()

        data = {'email': 'testEmail@gmail.com', 'password': DEFAULT_PASSWORD}

        client = APIClient()
        url = reverse('register')
        response = client.post(url, data, format='json')

        self.assertResponse201(response)
        responseData = self.loadJSONSafely(response)
        self.assertTrue('access_token' in responseData)

    def test_register_bad_email(self):
        """Testing a bad register with bad email param."""
        data = {'email': 'test', 'password': DEFAULT_PASSWORD}

        client = APIClient()
        url = reverse('register')
        response = client.post(url, data, format='json')

        # Make sure things went wrong first
        self.assertResponse400(response)
        responseData = self.loadJSONSafely(response)
        check_against_data = {'email': ['Enter a valid email address.']}
        self.assertEqual(responseData, check_against_data)

    def test_register_no_email(self):
        """Testing a bad register with no email param."""
        data = {'password': DEFAULT_PASSWORD}

        client = APIClient()
        url = reverse('register')
        response = client.post(url, data, format='json')

        # Make sure things went wrong first
        self.assertResponse400(response)
        responseData = self.loadJSONSafely(response)
        check_against_data = {'email': ['This field is required.']}
        self.assertEqual(responseData, check_against_data)

    def test_register_bad_password_length(self):
        """Testing a bad register with bad password length."""
        data = {'email': 'willFail@gmail.com', 'password': 't'}

        client = APIClient()
        url = reverse('register')
        response = client.post(url, data, format='json')

        # Make sure things went wrong first
        self.assertResponse400(response)
        responseData = self.loadJSONSafely(response)
        check_against_data = {
            'password': ['This password is too short. It must contain at least 8 characters.',
                         'This password is too common.']}
        self.assertEqual(responseData, check_against_data)

    def test_register_bad_password_common(self):
        """Testing a bad register with bad password too common."""
        data = {'email': 'willFail@gmail.com', 'password': 'password'}

        client = APIClient()
        url = reverse('register')
        response = client.post(url, data, format='json')

        # Make sure things went wrong first
        self.assertResponse400(response)
        responseData = self.loadJSONSafely(response)
        check_against_data = {'password': ['This password is too common.']}
        self.assertEqual(responseData, check_against_data)

    def test_register_bad_password_numeric(self):
        """Testing a bad register with bad password that's only numbers."""
        data = {'email': 'willFail@gmail.com', 'password': '234238483'}

        client = APIClient()
        url = reverse('register')
        response = client.post(url, data, format='json')

        # Make sure things went wrong first
        self.assertResponse400(response)
        responseData = self.loadJSONSafely(response)
        check_against_data = {'password': ['This password is entirely numeric.']}
        self.assertEqual(responseData, check_against_data)

    def test_register_no_password(self):
        """Testing a bad register with no password param."""
        data = {'email': 'willFail@gmail.com'}

        client = APIClient()
        url = reverse('register')
        response = client.post(url, data, format='json')

        # Make sure things went wrong first
        self.assertResponse400(response)
        responseData = self.loadJSONSafely(response)
        check_against_data = {'password': ['This field is required.']}
        self.assertEqual(responseData, check_against_data)

    def test_register_no_email_or_password(self):
        """Testing a bad register with no email or password params."""
        data = {}

        client = APIClient()
        url = reverse('register')
        response = client.post(url, data, format='json')

        # Make sure things went wrong first
        self.assertResponse400(response)
        responseData = self.loadJSONSafely(response)
        check_against_data = {
            'email': ['This field is required.'],
            'password': ['This field is required.']}
        self.assertEqual(responseData, check_against_data)
