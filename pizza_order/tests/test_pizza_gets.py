import json

from django.urls import reverse
from httmock import HTTMock, urlmatch
from rest_framework.test import APIClient

from core.MyTestCase import MyTestCase
from my_auth.tests.factories import CustomUserFactory

from ..models import PizzaOrder


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
                        ordered_by=authUser
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

                    # Now delete the queryset so it starts fresh every loop
                    PizzaOrder.objects.all().delete()
