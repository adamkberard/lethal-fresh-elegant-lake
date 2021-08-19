from django.urls import reverse
from rest_framework.test import APIClient

from core.MyTestCase import MyTestCase
from my_auth.tests.factories import CustomUserFactory

from ..models import PizzaOrder

from datetime import datetime

timeFormatStr = "%Y-%m-%dT%H:%M:%S.%f"

# Maybe only create auth user once...
class Test_Get_Single_Pizza(MyTestCase):
    def test_get_one_pizza(self):
        authUser = CustomUserFactory()
        # I make up an order id that would normall be sent by the pizzeria
        pizza = PizzaOrder.objects.create(
            flavor=PizzaOrder.FLAVOR_HAWAII,
            crust=PizzaOrder.CRUST_THIN,
            size=PizzaOrder.SIZE_LARGE,
            table_number=30000,
            ordered_by=authUser,
            timestamp=datetime.now()
        )
        pizza.order_id = pizza.id
        pizza.save()

        client = APIClient()
        client.force_authenticate(user=authUser)
        url = reverse('pizza_detail', args=(pizza.order_id,))
        response = client.get(url)

        self.assertResponse200(response)
        responseData = self.loadJSONSafely(response)

        # Now we check the data, make sure it is accurate
        self.assertEqual(responseData['flavor'], pizza.flavor)
        self.assertEqual(responseData['size'], pizza.size)
        self.assertEqual(responseData['crust'], pizza.crust)
        self.assertEqual(responseData['Order_ID'], pizza.order_id)
        self.assertEqual(responseData['Table_No'], pizza.table_number)
        self.assertEqual(responseData['Timestamp'], pizza.timestamp.strftime(timeFormatStr))

    def test_get_one_pizza_every_pizza(self):
        authUser = CustomUserFactory()
        order_ids = []
        for flavor in [x[0] for x in PizzaOrder.FLAVOR_CHOICES]:
            for size in [x[0] for x in PizzaOrder.SIZE_CHOICES]:
                for crust in [x[0] for x in PizzaOrder.CRUST_CHOICES]:
                    pizza = PizzaOrder.objects.create(
                        flavor=flavor,
                        crust=crust,
                        size=size,
                        table_number=30000,
                        ordered_by=authUser,
                        timestamp=datetime.now()
                    )
                    pizza.order_id = pizza.id
                    pizza.save()
                    order_ids.append(pizza.order_id)
    
        client = APIClient()
        client.force_authenticate(user=authUser)

        for order_id in order_ids:
            pizza = PizzaOrder.objects.get(order_id=order_id)
            url = reverse('pizza_detail', args=(order_id,))
            response = client.get(url)

            self.assertResponse200(response)
            responseData = self.loadJSONSafely(response)

            # Now we check the data, make sure it is accurate
            self.assertEqual(responseData['flavor'], pizza.flavor)
            self.assertEqual(responseData['size'], pizza.size)
            self.assertEqual(responseData['crust'], pizza.crust)
            self.assertEqual(responseData['Order_ID'], pizza.order_id)
            self.assertEqual(responseData['Table_No'], pizza.table_number)
            self.assertEqual(responseData['Timestamp'], pizza.timestamp.strftime(timeFormatStr))


class Test_Get_Many_Pizzas(MyTestCase):
    def test_get_no_pizzas(self):
        authUser = CustomUserFactory()

        client = APIClient()
        client.force_authenticate(user=authUser)
        response = client.get(reverse('pizza_create_list'))

        self.assertResponse200(response)
        responseData = self.loadJSONSafely(response)

        # Now we check the data, make sure it is accurate
        self.assertEqual(len(responseData), 0)


    def test_get_single_pizza(self):
        authUser = CustomUserFactory()
        pizza = PizzaOrder.objects.create(
            flavor=PizzaOrder.FLAVOR_HAWAII,
            crust=PizzaOrder.CRUST_THIN,
            size=PizzaOrder.SIZE_LARGE,
            table_number=30000,
            ordered_by=authUser,
            timestamp=datetime.now()
        )

        client = APIClient()
        client.force_authenticate(user=authUser)
        response = client.get(reverse('pizza_create_list'))

        self.assertResponse200(response)
        responseData = self.loadJSONSafely(response)

        # Now we check the data, make sure it is accurate
        self.assertEqual(len(responseData), 1)
        self.assertEqual(responseData[0]['flavor'], PizzaOrder.FLAVOR_HAWAII)
        self.assertEqual(responseData[0]['size'], PizzaOrder.SIZE_LARGE)
        self.assertEqual(responseData[0]['crust'], PizzaOrder.CRUST_THIN)
        self.assertEqual(responseData[0]['Order_ID'], pizza.order_id)
        self.assertEqual(responseData[0]['Table_No'], 30000)
        self.assertIn('Timestamp', responseData[0])

    def test_get_single_pizza_all_options(self):
        authUser = CustomUserFactory()

        for flavor in [x[0] for x in PizzaOrder.FLAVOR_CHOICES]:
            for size in [x[0] for x in PizzaOrder.SIZE_CHOICES]:
                for crust in [x[0] for x in PizzaOrder.CRUST_CHOICES]:
                    pizza = PizzaOrder.objects.create(
                        flavor=flavor,
                        crust=crust,
                        size=size,
                        table_number=30000,
                        ordered_by=authUser,
                        timestamp=datetime.now()
                    )
                    client = APIClient()
                    client.force_authenticate(user=authUser)
                    response = client.get(reverse('pizza_create_list'))

                    self.assertResponse200(response)
                    responseData = self.loadJSONSafely(response)

                    # Now we check the data, make sure it is accurate
                    self.assertEqual(len(responseData), 1)
                    self.assertEqual(responseData[0]['flavor'], flavor)
                    self.assertEqual(responseData[0]['size'], size)
                    self.assertEqual(responseData[0]['crust'], crust)
                    self.assertEqual(responseData[0]['Order_ID'], pizza.order_id)
                    self.assertEqual(responseData[0]['Table_No'], 30000)
                    self.assertIn('Timestamp', responseData[0])

                    # Now delete the queryset so it starts fresh every loop
                    PizzaOrder.objects.all().delete()

    def test_get_two_pizzas(self):
        authUser = CustomUserFactory()
        pizzaOne = PizzaOrder.objects.create(
            flavor=PizzaOrder.FLAVOR_HAWAII,
            crust=PizzaOrder.CRUST_THIN,
            size=PizzaOrder.SIZE_LARGE,
            table_number=30000,
            ordered_by=authUser,
            timestamp=datetime.now()
        )
        pizzaTwo = PizzaOrder.objects.create(
            flavor=PizzaOrder.FLAVOR_REGINA,
            crust=PizzaOrder.CRUST_THIN,
            size=PizzaOrder.SIZE_MEDIUM,
            table_number=30001,
            ordered_by=authUser,
            timestamp=datetime.now()
        )

        client = APIClient()
        client.force_authenticate(user=authUser)
        response = client.get(reverse('pizza_create_list'))

        self.assertResponse200(response)
        responseData = self.loadJSONSafely(response)

        # Now we check the data, make sure it is accurate
        self.assertEqual(len(responseData), 2)
        self.assertEqual(responseData[0]['flavor'], PizzaOrder.FLAVOR_HAWAII)
        self.assertEqual(responseData[0]['size'], PizzaOrder.SIZE_LARGE)
        self.assertEqual(responseData[0]['crust'], PizzaOrder.CRUST_THIN)
        self.assertEqual(responseData[0]['Order_ID'], pizzaOne.order_id)
        self.assertEqual(responseData[0]['Table_No'], 30000)
        self.assertIn('Timestamp', responseData[0])

        self.assertEqual(responseData[1]['flavor'], PizzaOrder.FLAVOR_REGINA)
        self.assertEqual(responseData[1]['size'], PizzaOrder.SIZE_MEDIUM)
        self.assertEqual(responseData[1]['crust'], PizzaOrder.CRUST_THIN)
        self.assertEqual(responseData[1]['Order_ID'], pizzaTwo.order_id)
        self.assertEqual(responseData[1]['Table_No'], 30001)
        self.assertIn('Timestamp', responseData[1])
