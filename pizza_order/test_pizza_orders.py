from django.urls import reverse
from rest_framework.test import APIClient

from .factories import DEFAULT_PASSWORD, CustomUserFactory
from core.MyTestCase import MyTestCase

from httmock import HTTMock, all_requests


class Test_Login_View(MyTestCase):

    @all_requests
    def google_mock(url, caught_url, request):
        return 'Feeling lucky, punk?'

    def test_httmock(self):
        userModel = CustomUserFactory()
        data = {'email': userModel.email, 'password': DEFAULT_PASSWORD}
        client = APIClient()
        url = reverse('login')

        with HTTMock(self.google_mock):
            response = client.post(url, data, format='json')
        print(response.content)  # 'Feeling lucky, punk?'
