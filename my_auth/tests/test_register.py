from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from ..models import CustomUser
from ..serializers import BasicCustomUserSerializer
from .checkers import AuthTesting
from .factories import DEFAULT_PASSWORD, CustomUserFactory


class Test_Register_View(AuthTesting):

    def test_correct_register(self):
        """Testing a legitimate registration."""
        data = {'email': 'testEmail@gmail.com', 'password': 'password'}

        client = APIClient()
        url = reverse('register')
        self.response = client.post(url, data, format='json')
        userModel = CustomUser.objects.get(email='testEmail@gmail.com')

        # The response we want
        check_against_user = {
            'username': userModel.username,
            'email': userModel.email,
            'uuid': str(userModel.uuid),
            'token': str(Token.objects.get(user=userModel))
        }
        self.check_against_data = {
            'user': check_against_user,
            'games': [],
            'friends': [],
            'all_users': [BasicCustomUserSerializer(userModel).data]
        }

        # Check return
        self.assertResponse201()
        self.loadJSONSafely()
        self.assertLoginDataEqual()

    def test_correct_register_one_other_user(self):
        """Testing a legitimate registration with one other user."""
        otherUser = CustomUserFactory()

        data = {'email': 'testEmail@gmail.com', 'password': DEFAULT_PASSWORD}

        client = APIClient()
        url = reverse('register')
        self.response = client.post(url, data, format='json')
        userModel = CustomUser.objects.get(email='testEmail@gmail.com')

        # The response we want
        check_against_user = {
            'username': userModel.username,
            'email': userModel.email,
            'uuid': str(userModel.uuid),
            'token': str(Token.objects.get(user=userModel))
        }
        check_against_all_usernames = [
            BasicCustomUserSerializer(userModel).data,
            BasicCustomUserSerializer(otherUser).data,
        ]
        self.check_against_data = {
            'user': check_against_user,
            'games': [],
            'friends': [],
            'all_users': check_against_all_usernames
        }

        # Check return
        self.assertResponse201()
        self.loadJSONSafely()
        self.assertLoginDataEqual()

    def test_correct_register_four_other_users(self):
        """Testing a legitimate registration with four other users."""
        otherUserOne = CustomUserFactory()
        otherUserTwo = CustomUserFactory()
        otherUserThree = CustomUserFactory()
        otherUserFour = CustomUserFactory()

        data = {'email': 'testEmail@gmail.com', 'password': DEFAULT_PASSWORD}

        client = APIClient()
        url = reverse('register')
        self.response = client.post(url, data, format='json')
        userModel = CustomUser.objects.get(email='testEmail@gmail.com')

        # The response we want
        check_against_user = {
            'username': userModel.username,
            'email': userModel.email,
            'uuid': str(userModel.uuid),
            'token': str(Token.objects.get(user=userModel))
        }
        check_against_all_usernames = [
            BasicCustomUserSerializer(userModel).data,
            BasicCustomUserSerializer(otherUserOne).data,
            BasicCustomUserSerializer(otherUserTwo).data,
            BasicCustomUserSerializer(otherUserThree).data,
            BasicCustomUserSerializer(otherUserFour).data,
        ]
        self.check_against_data = {
            'user': check_against_user,
            'games': [],
            'friends': [],
            'all_users': check_against_all_usernames
        }

        # Check return
        self.assertResponse201()
        self.loadJSONSafely()
        self.assertLoginDataEqual()

    def test_register_bad_email(self):
        """Testing a bad register with bad email param."""
        data = {'email': 'test', 'password': DEFAULT_PASSWORD}

        client = APIClient()
        url = reverse('register')
        self.response = client.post(url, data, format='json')

        # Make sure things went wrong first
        self.assertResponse400()

        self.check_against_data = {'email': ['Enter a valid email address.']}
        self.fields = ['email']
        self.assertResponseEqual()

    def test_register_no_email(self):
        """Testing a bad register with no email param."""
        data = {'password': DEFAULT_PASSWORD}

        client = APIClient()
        url = reverse('register')
        self.response = client.post(url, data, format='json')

        # Make sure things went wrong first
        self.assertResponse400()
        self.assertFieldsMissing(['email'])

    def test_register_bad_password_length(self):
        """Testing a bad register with bad password length."""
        data = {'email': 'willFail@gmail.com', 'password': 't'}

        client = APIClient()
        url = reverse('register')
        self.response = client.post(url, data, format='json')

        # Make sure things went wrong first
        self.assertResponse400()

        self.check_against_data = {
            'password': ['This password is too short. It must contain at least 8 characters.',
                         'This password is too common.']}
        self.fields = ['password']
        self.assertResponseEqual()

    def test_register_bad_password_common(self):
        """Testing a bad register with bad password too common."""
        data = {'email': 'willFail@gmail.com', 'password': 'password'}

        client = APIClient()
        url = reverse('register')
        self.response = client.post(url, data, format='json')

        # Make sure things went wrong first
        self.assertResponse400()

        self.check_against_data = {
            'password': ['This password is too common.']}
        self.fields = ['password']
        self.assertResponseEqual()

    def test_register_bad_password_numeric(self):
        """Testing a bad register with bad password that's only numbers."""
        data = {'email': 'willFail@gmail.com', 'password': '234238483'}

        client = APIClient()
        url = reverse('register')
        self.response = client.post(url, data, format='json')

        # Make sure things went wrong first
        self.assertResponse400()

        self.check_against_data = {
            'password': ['This password is entirely numeric.']
        }
        self.fields = ['password']
        self.assertResponseEqual()

    def test_register_no_password(self):
        """Testing a bad register with no password param."""
        data = {'email': 'willFail@gmail.com'}

        client = APIClient()
        url = reverse('register')
        self.response = client.post(url, data, format='json')

        # Make sure things went wrong first
        self.assertResponse400()
        self.assertFieldsMissing(['password'])

    def test_register_no_email_or_password(self):
        """Testing a bad register with no email or password params."""
        data = {}

        client = APIClient()
        url = reverse('register')
        response = client.post(url, data, format='json')

        # Make sure things went wrong first
        self.assertEqual(response.status_code, 400)
        self.response = client.post(url, data, format='json')

        # Make sure things went wrong first
        self.assertResponse400()
        self.assertFieldsMissing(['password', 'email'])
