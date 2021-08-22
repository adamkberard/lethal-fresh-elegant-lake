from django.urls import reverse
from httmock import HTTMock
from rest_framework.test import APIClient

from my_auth.tests.factories import CustomUserFactory

from ..models import PizzaOrder
from .MyPizzaTester import MyPizzaTester


class Test_Post_Single_Pizza(MyPizzaTester):
    def test_post_single_pizza(self):
        authUser = CustomUserFactory()
        testFlavor = 'Hawaii'
        testSize = 'Large'
        testCrust = 'Thin'
        data = {
            'Flavor': testFlavor,
            'Size': testSize,
            'Crust': testCrust
        }

        client = APIClient()
        client.force_authenticate(user=authUser)
        with HTTMock(self.login_mock, self.pizza_order_mock):
            response = client.post(reverse('pizza_create_list'), data=data, format='json')

        self.assertResponse201(response)
        responseData = self.loadJSONSafely(response)

        self.assertIn('Order_ID', responseData)
        pizza = PizzaOrder.objects.get(Order_ID=responseData['Order_ID'])
        self.assertEqual(pizza.Flavor, testFlavor)
        self.assertEqual(pizza.Size, testSize)
        self.assertEqual(pizza.Crust, testCrust)

        # Now we check the data
        self.assertEqual(responseData['Flavor'], pizza.Flavor)
        self.assertEqual(responseData['Size'], pizza.Size)
        self.assertEqual(responseData['Crust'], pizza.Crust)
        self.assertEqual(responseData['Table_No'], pizza.Table_No)
        self.assertEqual(responseData['Table_No'], pizza.Table_No)
        self.assertEqual(responseData['Order_ID'], pizza.Order_ID)
        self.assertEqual(responseData['Timestamp'], pizza.timeAsString())

    def test_post_every_pizza(self):
        authUser = CustomUserFactory()
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

                    self.assertIn('Order_ID', responseData)
                    pizza = PizzaOrder.objects.get(Order_ID=responseData['Order_ID'])
                    self.assertEqual(pizza.Flavor, flavor)
                    self.assertEqual(pizza.Size, size)
                    self.assertEqual(pizza.Crust, crust)

                    # Now we check the data
                    self.assertEqual(responseData['Flavor'], pizza.Flavor)
                    self.assertEqual(responseData['Size'], pizza.Size)
                    self.assertEqual(responseData['Crust'], pizza.Crust)
                    self.assertEqual(responseData['Table_No'], pizza.Table_No)
                    self.assertEqual(responseData['Table_No'], pizza.Table_No)
                    self.assertEqual(responseData['Order_ID'], pizza.Order_ID)
                    self.assertEqual(responseData['Timestamp'], pizza.timeAsString())


class Test_Post_Single_Pizza_Fail(MyPizzaTester):
    # This test makes sure if the first table_no is rejected, we still
    # can make a successfull order on one of the subsequent attempts
    def test_post_single_pizza_bad_table_no_once(self):
        authUser = CustomUserFactory()
        testFlavor = 'Hawaii'
        testSize = 'Large'
        testCrust = 'Thin'
        data = {
            'Flavor': testFlavor,
            'Size': testSize,
            'Crust': testCrust
        }
        client = APIClient()
        client.force_authenticate(user=authUser)
        with HTTMock(self.login_mock, self.pizza_order_mock_bad_table_number_once):
            response = client.post(reverse('pizza_create_list'), data=data, format='json')

        self.assertResponse201(response)
        responseData = self.loadJSONSafely(response)

        self.assertIn('Order_ID', responseData)
        pizza = PizzaOrder.objects.get(Order_ID=responseData['Order_ID'])
        self.assertEqual(pizza.Flavor, testFlavor)
        self.assertEqual(pizza.Size, testSize)
        self.assertEqual(pizza.Crust, testCrust)

        # Now we check the data
        self.assertEqual(responseData['Flavor'], pizza.Flavor)
        self.assertEqual(responseData['Size'], pizza.Size)
        self.assertEqual(responseData['Crust'], pizza.Crust)
        self.assertEqual(responseData['Table_No'], pizza.Table_No)
        self.assertEqual(responseData['Order_ID'], pizza.Order_ID)
        self.assertEqual(responseData['Timestamp'], pizza.timeAsString())

        # One extra check to ensure the table_no is above 31000 to show it is the second attempt
        self.assertGreater(pizza.Table_No, 31000)

    # This test makes sure we can handle a bad pizza login gracefully
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

        # Make sure we didn't save the pizza order since the pizzeria didn't get it
        self.assertEqual(PizzaOrder.objects.all().count(), 0)

    # This test makes sure we can handle a pizza login with no return token gracefully
    def test_post_single_pizza_no_token(self):
        authUser = CustomUserFactory()
        data = {
            'Flavor': 'Hawaii',
            'Size': 'Large',
            'Crust': 'Thin'
        }
        client = APIClient()
        client.force_authenticate(user=authUser)
        with HTTMock(self.login_mock_bad_token_return):
            response = client.post(reverse('pizza_create_list'), data=data, format='json')

        self.assertResponse400(response)
        responseData = self.loadJSONSafely(response)

        # Now we check the data
        self.assertEqual(responseData['error'], "Did not receive a token from pizzeria.")

        # Make sure we didn't save the pizza order since the pizzeria didn't get it
        self.assertEqual(PizzaOrder.objects.all().count(), 0)

    # This test makes sure we can handle a bad json response from the pizzaria
    def test_post_single_pizza_bad_json_response(self):
        authUser = CustomUserFactory()
        data = {
            'Flavor': 'Hawaii',
            'Size': 'Large',
            'Crust': 'Thin'
        }
        client = APIClient()
        client.force_authenticate(user=authUser)
        with HTTMock(self.login_mock_bad_json_return):
            response = client.post(reverse('pizza_create_list'), data=data, format='json')

        self.assertResponse400(response)
        responseData = self.loadJSONSafely(response)

        # Now we check the data
        self.assertEqual(responseData['error'], "Did not receive valid json from pizzeria.")

        # Make sure we didn't save the pizza order since the pizzeria didn't get it
        self.assertEqual(PizzaOrder.objects.all().count(), 0)


class Test_Post_Many_Pizzas(MyPizzaTester):
    def test_post_same_pizza_many_times(self):
        authUser = CustomUserFactory()
        numPizzas = 5
        testFlavor = 'Hawaii'
        testSize = 'Large'
        testCrust = 'Thin'
        data = []
        for i in range(numPizzas):
            data.append({
                'Flavor': testFlavor,
                'Size': testSize,
                'Crust': testCrust
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
            self.assertIn('Order_ID', responseData[i])
            pizza = PizzaOrder.objects.get(Order_ID=responseData[i]['Order_ID'])
            self.assertEqual(pizza.Flavor, testFlavor)
            self.assertEqual(pizza.Size, testSize)
            self.assertEqual(pizza.Crust, testCrust)

            # Now we check the data
            self.assertEqual(responseData[i]['Flavor'], pizza.Flavor)
            self.assertEqual(responseData[i]['Size'], pizza.Size)
            self.assertEqual(responseData[i]['Crust'], pizza.Crust)
            self.assertEqual(responseData[i]['Table_No'], pizza.Table_No)
            self.assertEqual(responseData[i]['Table_No'], pizza.Table_No)
            self.assertEqual(responseData[i]['Order_ID'], pizza.Order_ID)
            self.assertEqual(responseData[i]['Timestamp'], pizza.timeAsString())
