from datetime import datetime

from django.urls import reverse
from rest_framework.test import APIClient

from .MyPizzaTester import MyPizzaTester
from my_auth.tests.factories import CustomUserFactory
from httmock import HTTMock

from ..models import PizzaOrder

timeFormatStr = "%Y-%m-%dT%H:%M:%S.%f"


# Maybe only create auth user once...
class Test_Delete_Single_Pizza(MyPizzaTester):
    def test_delete_one_pizza(self):
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
        with HTTMock(self.pizza_delete_mock):
            response = client.delete(url)

        self.assertResponse204(response)
        self.assertEqual(PizzaOrder.objects.all().count(), 0)

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
        totalOrders = len(order_ids)

        for order_id in order_ids:
            pizza = PizzaOrder.objects.get(order_id=order_id)
            url = reverse('pizza_detail', args=(order_id,))
            with HTTMock(self.pizza_delete_mock):
                response = client.delete(url)

            self.assertResponse204(response)
            totalOrders -= 1
            self.assertEqual(PizzaOrder.objects.all().count(), totalOrders)
