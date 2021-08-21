from django.urls import reverse
from httmock import HTTMock
from rest_framework.test import APIClient

from my_auth.tests.factories import CustomUserFactory

from ..models import PizzaOrder
from .MyPizzaTester import MyPizzaTester


class Test_Post_Single_Pizza(MyPizzaTester):
    def test_post_single_pizza(self):
        authUser = CustomUserFactory()
        data = {
            'Flavor': 'Hawaii',
            'Size': 'Large',
            'Crust': 'Thin'
        }
        client = APIClient()
        client.force_authenticate(user=authUser)
        with HTTMock(self.login_mock, self.pizza_order_mock):
            response = client.post(reverse('pizza_create_list'), data=data, format='json')

        self.assertResponse201(response)
        responseData = self.loadJSONSafely(response)

        # Now we check the data
        self.assertEqual(responseData['Flavor'], 'Hawaii')
        self.assertEqual(responseData['Size'], 'Large')
        self.assertEqual(responseData['Crust'], 'Thin')

        self.assertIn('Order_ID', responseData)
        self.assertGreaterEqual(responseData['Table_No'], 30000)
        self.assertIn('Timestamp', responseData)

    def test_post_every_pizza(self):
        authUser = CustomUserFactory()
        table_numbers = []
        for flavor in [x[0] for x in PizzaOrder.FLAVOR_CHOICES]:
            for size in [x[0] for x in PizzaOrder.SIZE_CHOICES]:
                for crust in [x[0] for x in PizzaOrder.CRUST_CHOICES]:
                    data = {
                        'Flavor': flavor,
                        'Size': size,
                        'Crust': crust
                    }
                    client = APIClient()
                    client.force_authenticate(user=authUser)
                    with HTTMock(self.login_mock, self.pizza_order_mock):
                        url = reverse('pizza_create_list')
                        response = client.post(url, data=data, format='json')

                    self.assertResponse201(response)
                    responseData = self.loadJSONSafely(response)

                    # Now we check the data
                    self.assertEqual(responseData['Flavor'], flavor)
                    self.assertEqual(responseData['Size'], size)
                    self.assertEqual(responseData['Crust'], crust)

                    self.assertIn('Order_ID', responseData)
                    self.assertGreaterEqual(responseData['Table_No'], 30000)
                    self.assertNotIn(responseData['Table_No'], table_numbers)
                    self.assertIn('Timestamp', responseData)
                    table_numbers.append(responseData['Table_No'])


class Test_Post_Single_Pizza_Fail(MyPizzaTester):

    def test_post_single_pizza_bad_table_no_once(self):
        authUser = CustomUserFactory()
        data = {
            'Flavor': 'Hawaii',
            'Size': 'Large',
            'Crust': 'Thin'
        }
        client = APIClient()
        client.force_authenticate(user=authUser)
        with HTTMock(self.login_mock, self.pizza_order_mock):
            response = client.post(reverse('pizza_create_list'), data=data, format='json')

        self.assertResponse201(response)
        responseData = self.loadJSONSafely(response)

        # Now we check the data
        self.assertEqual(responseData['Flavor'], 'Hawaii')
        self.assertEqual(responseData['Size'], 'Large')
        self.assertEqual(responseData['Crust'], 'Thin')

        self.assertIn('Order_ID', responseData)
        self.assertGreaterEqual(responseData['Table_No'], 30000)

    def test_post_single_pizza_bad_login(self):
        authUser = CustomUserFactory()
        data = {
            'Flavor': 'Hawaii',
            'Size': 'Large',
            'Crust': 'Thin'
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
            'Flavor': 'Hawaii',
            'Size': 'Large',
            'Crust': 'Thin'
        }
        client = APIClient()
        client.force_authenticate(user=authUser)
        with HTTMock(self.login_mock, self.pizza_order_mock_bad_table_number):
            response = client.post(reverse('pizza_create_list'), data=data, format='json')

        self.assertResponse400(response)
        responseData = self.loadJSONSafely(response)

        # Now we check the data
        self.assertEqual(responseData['error'], "Error sending order to pizzeria.")


class Test_Post_Many_Pizzas(MyPizzaTester):
    def test_post_same_pizza_many_times(self):
        authUser = CustomUserFactory()
        numPizzas = 5
        data = []
        for i in range(numPizzas):
            data.append({
                'Flavor': 'Hawaii',
                'Size': 'Large',
                'Crust': 'Thin'
            })
        client = APIClient()
        client.force_authenticate(user=authUser)
        with HTTMock(self.login_mock, self.pizza_order_mock):
            response = client.post(reverse('pizza_create_list'), data=data, format='json')

        self.assertResponse201(response)
        responseData = self.loadJSONSafely(response)

        # Now we check the data
        self.assertEqual(len(responseData), numPizzas)
        for i in range(numPizzas):
            self.assertEqual(responseData[i]['Flavor'], 'Hawaii')
            self.assertEqual(responseData[i]['Size'], 'Large')
            self.assertEqual(responseData[i]['Crust'], 'Thin')

            self.assertIn('Order_ID', responseData[i])
            self.assertGreaterEqual(responseData[i]['Table_No'], 30000)
            self.assertIn('Timestamp', responseData[i])
