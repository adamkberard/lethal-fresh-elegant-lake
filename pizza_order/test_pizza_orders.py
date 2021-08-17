import json

from django.urls import reverse
from httmock import HTTMock, urlmatch
from rest_framework.test import APIClient

from core.MyTestCase import MyTestCase
from my_auth.tests.factories import CustomUserFactory

from .models import PizzaOrder


class Test_Pizza_Ordering(MyTestCase):
    order = 1

    @urlmatch(netloc=r'order-pizza-api.herokuapp.com', path=r'/api/auth')
    def login_mock(self, caught_url, request):
        tempDict = {'access_token': 'access_token'}
        return {
            'status_code': 200,
            'content': tempDict
        }

    @urlmatch(netloc=r'order-pizza-api.herokuapp.com', path=r'/api/auth')
    def fail_login_mock(self, caught_url, request):
        return {'status_code': 400}

    @urlmatch(netloc=r'order-pizza-api.herokuapp.com', path=r'/api/orders')
    def pizza_order_mock(self, caught_url, request):
        caughtDict = json.loads(request.body)
        caughtDict['Order_ID'] = int(caughtDict['Table_No']) - 30000
        caughtDict['Timestamp'] = "2021-08-16T02:37:41.353941"
        return {
            'status_code': 201,
            'content': caughtDict
        }

    @urlmatch(netloc=r'order-pizza-api.herokuapp.com', path=r'/api/orders')
    def pizza_order_mock_bad_table_number(self, caught_url, request):
        return {'status_code': 409}

    def test_post_single_pizza(self):
        authUser = CustomUserFactory()
        data = {
            'flavor': 'Hawaii',
            'size': 'Large',
            'crust': 'Thin'
        }
        client = APIClient()
        client.force_authenticate(user=authUser)
        with HTTMock(self.login_mock, self.pizza_order_mock):
            response = client.post(reverse('pizza_create_list'), data=data, format='json')

        self.assertResponse201(response)
        responseData = self.loadJSONSafely(response)

        # Now we check the data
        self.assertEqual(responseData['flavor'], 'Hawaii')
        self.assertEqual(responseData['size'], 'Large')
        self.assertEqual(responseData['crust'], 'Thin')

        self.assertIn('Order_ID', responseData)
        self.assertGreaterEqual(responseData['Table_No'], 30000)

    def test_post_single_pizza_bad_login(self):
        authUser = CustomUserFactory()
        data = {
            'flavor': 'Hawaii',
            'size': 'Large',
            'crust': 'Thin'
        }
        client = APIClient()
        client.force_authenticate(user=authUser)
        with HTTMock(self.fail_login_mock):
            response = client.post(reverse('pizza_create_list'), data=data, format='json')

        self.assertResponse400(response)
        responseData = self.loadJSONSafely(response)

        # Now we check the data
        self.assertEqual(responseData['error'], "Couldn't log in to pizzeria.")

    def test_post_single_pizza_bad_table_number(self):
        authUser = CustomUserFactory()
        data = {
            'flavor': 'Hawaii',
            'size': 'Large',
            'crust': 'Thin'
        }
        client = APIClient()
        client.force_authenticate(user=authUser)
        with HTTMock(self.login_mock, self.pizza_order_mock_bad_table_number):
            response = client.post(reverse('pizza_create_list'), data=data, format='json')

        self.assertResponse400(response)
        responseData = self.loadJSONSafely(response)

        # Now we check the data
        self.assertEqual(responseData['error'], "Error sending order to pizzaria.")

    def test_post_every_pizza(self):
        authUser = CustomUserFactory()
        table_numbers = []
        for flavor in [x[0] for x in PizzaOrder.FLAVOR_CHOICES]:
            for size in [x[0] for x in PizzaOrder.SIZE_CHOICES]:
                for crust in [x[0] for x in PizzaOrder.CRUST_CHOICES]:
                    data = {
                        'flavor': flavor,
                        'size': size,
                        'crust': crust
                    }
                    client = APIClient()
                    client.force_authenticate(user=authUser)
                    with HTTMock(self.login_mock, self.pizza_order_mock):
                        url = reverse('pizza_create_list')
                        response = client.post(url, data=data, format='json')

                    self.assertResponse201(response)
                    responseData = self.loadJSONSafely(response)

                    # Now we check the data
                    self.assertEqual(responseData['flavor'], flavor)
                    self.assertEqual(responseData['size'], size)
                    self.assertEqual(responseData['crust'], crust)

                    self.assertIn('Order_ID', responseData)
                    self.assertGreaterEqual(responseData['Table_No'], 30000)
                    self.assertNotIn(responseData['Table_No'], table_numbers)
                    table_numbers.append(responseData['Table_No'])
