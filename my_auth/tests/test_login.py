from django.urls import reverse
from rest_framework.test import APIClient

from .factories import DEFAULT_PASSWORD, CustomUserFactory
from core.MyTestCase import MyTestCase


class Test_Login_View(MyTestCase):

    def test_correct_login_no_data(self):
        """Testing a legitimate login with no games, friends, or other users."""
        userModel = CustomUserFactory()
        data = {'email': userModel.email, 'password': DEFAULT_PASSWORD}

        client = APIClient()
        url = reverse('login')
        response = client.post(url, data, format='json')

        self.assertResponse201(response)
        responseData = self.loadJSONSafely(response)
        self.assertTrue('access_token' in responseData)

    def test_correct_login_one_other_user(self):
        """Testing a legitimate login with many other users in the database."""
        userModel = CustomUserFactory()
        for _ in range(100):
            CustomUserFactory()
        data = {'email': userModel.email, 'password': DEFAULT_PASSWORD}

        client = APIClient()
        url = reverse('login')
        response = client.post(url, data, format='json')

        self.assertResponse201(response)
        responseData = self.loadJSONSafely(response)
        self.assertTrue('access_token' in responseData)

    def test_login_bad_email(self):
        """Testing a bad login with bad email param."""
        data = {'email': 'test', 'password': DEFAULT_PASSWORD}

        client = APIClient()
        url = reverse('login')
        response = client.post(url, data, format='json')

        self.assertResponse400(response)
        check_against_data = {'email': ['Enter a valid email address.']}
        responseData = self.loadJSONSafely(response)
        self.assertEqual(responseData, check_against_data)

    def test_login_no_email(self):
        """Testing a bad login with no email param."""
        data = {'password': DEFAULT_PASSWORD}

        client = APIClient()
        url = reverse('login')
        response = client.post(url, data, format='json')

        # Make sure things went wrong first
        self.assertResponse400(response)

        self.assertEqual(response.status_code, 400)
        check_against_data = {'email': ['This field is required.']}
        responseData = self.loadJSONSafely(response)
        self.assertEqual(responseData, check_against_data)

    def test_login_no_password(self):
        """Testing a bad login with no password param."""
        data = {'email': 'willFail@gmail.com'}

        client = APIClient()
        url = reverse('login')
        response = client.post(url, data, format='json')

        # Make sure things went wrong first
        self.assertResponse400(response)
        responseData = self.loadJSONSafely(response)
        check_against_data = {'password': ['This field is required.']}
        self.assertEqual(responseData, check_against_data)

    def test_login_no_email_or_password(self):
        """Testing a bad login with no email or password params."""
        data = {}

        client = APIClient()
        url = reverse('login')
        response = client.post(url, data, format='json')

        # Make sure things went wrong first
        self.assertResponse400(response)
        responseData = self.loadJSONSafely(response)
        check_against_data = {
            'password': ['This field is required.'],
            'email': ['This field is required.']}
        self.assertEqual(responseData, check_against_data)
