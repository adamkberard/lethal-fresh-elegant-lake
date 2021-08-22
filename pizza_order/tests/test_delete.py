from datetime import datetime

from django.urls import reverse
from httmock import HTTMock
from rest_framework.test import APIClient

from my_auth.tests.factories import CustomUserFactory

from ..models import PizzaOrder
from .MyPizzaTester import MyPizzaTester


# Maybe only create auth user once...
class Test_Delete_Single_Pizza(MyPizzaTester):
    def test_delete_one_pizza(self):
        authUser = CustomUserFactory()
        # I make up an order id that would normall be sent by the pizzeria
        pizza = PizzaOrder.objects.create(
            Flavor=PizzaOrder.FLAVOR_HAWAII,
            Crust=PizzaOrder.CRUST_THIN,
            Size=PizzaOrder.SIZE_LARGE,
            Table_No=30000,
            Ordered_By=authUser,
            Timestamp=datetime.now()
        )
        pizza.Order_ID = pizza.id
        pizza.save()

        client = APIClient()
        client.force_authenticate(user=authUser)
        url = reverse('pizza_detail', args=(pizza.Order_ID,))
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
                        Flavor=flavor,
                        Crust=crust,
                        Size=size,
                        Table_No=30000,
                        Ordered_By=authUser,
                        Timestamp=datetime.now()
                    )
                    pizza.Order_ID = pizza.id
                    pizza.save()
                    order_ids.append(pizza.Order_ID)

        client = APIClient()
        client.force_authenticate(user=authUser)
        totalOrders = len(order_ids)

        for order_id in order_ids:
            pizza = PizzaOrder.objects.get(Order_ID=order_id)
            url = reverse('pizza_detail', args=(order_id,))
            with HTTMock(self.pizza_delete_mock):
                response = client.delete(url)

            self.assertResponse204(response)
            totalOrders -= 1
            self.assertEqual(PizzaOrder.objects.all().count(), totalOrders)

        self.assertEqual(PizzaOrder.objects.all().count(), 0)
