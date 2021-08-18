import json

from django.urls import reverse
from httmock import HTTMock, urlmatch
from rest_framework.test import APIClient

from core.MyTestCase import MyTestCase
from my_auth.tests.factories import CustomUserFactory

from .models import PizzaOrder


class Test_Pizza_Getting_Single_Pizzas(MyTestCase):
    def test_get_single_pizza(self):
        authUser = CustomUserFactory()
        pizza = PizzaOrder.objects.create(
            flavor=PizzaOrder.FLAVOR_HAWAII,
            crust=PizzaOrder.CRUST_THIN,
            size=PizzaOrder.SIZE_LARGE,
            table_number=30000,
            ordered_by=authUser
        )

        client = APIClient()
        client.force_authenticate(user=authUser)
        response = client.get(reverse('pizza_get_list'))

        self.assertResponse200(response)
        responseData = self.loadJSONSafely(response)

        # Now we check the data, make sure it is accurate
        self.assertEqual(len(responseData), 1)
        self.assertEqual(responseData[0]['flavor'], PizzaOrder.FLAVOR_HAWAII)
        self.assertEqual(responseData[0]['size'], PizzaOrder.SIZE_LARGE)
        self.assertEqual(responseData[0]['crust'], PizzaOrder.CRUST_THIN)
        self.assertEqual(responseData[0]['Order_ID'], PizzaOrder.CRUST_THIN)
        self.assertEqual(responseData[0]['Table_No'], PizzaOrder.CRUST_THIN)


        self.assertIn('Order_ID', responseData)
        self.assertGreaterEqual(responseData['Table_No'], 30000)

    def test_post_single_pizza_bad_table_no_once(self):
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
        self.assertEqual(responseData['error'], "Error logging in to pizzeria.")

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
        self.assertEqual(responseData['error'], "Error sending order to pizzeria.")

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
