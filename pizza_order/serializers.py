import json
import random

import requests
from rest_framework import serializers

from .models import PizzaOrder

from dateutil import parser


class PizzaOrderSerializer(serializers.Serializer):
    class Meta:
        module = PizzaOrder

    flavor = serializers.ChoiceField([item[0] for item in PizzaOrder.FLAVOR_CHOICES])
    size = serializers.ChoiceField([item[0] for item in PizzaOrder.SIZE_CHOICES])
    crust = serializers.ChoiceField([item[0] for item in PizzaOrder.CRUST_CHOICES])

    # Might want to check that I can parse the json response and that the token is there
    def pizzeriaLogin(self):
        # First we log in to the pizza place to get a fresh token
        url = 'https://order-pizza-api.herokuapp.com/api/auth'
        # Might make the login data env variables to keep them hidden
        data = {'username': 'test', 'password': 'test'}
        response = requests.post(url=url, json=data)
        if response.status_code != 200:
            raise serializers.ValidationError({'error': "Error logging in to pizzeria."})
        try:
            responseData = json.loads(response.content)
        except ValueError:
            raise serializers.ValidationError({'error': "Couldn't parse login return."})
        return responseData['access_token']

    # Might want to check that I can parse the json response and that the
    # two fields I want are in it
    def sendPizzaOrder(self, pizzaOrder, token):
        hed = {'Authorization': 'Bearer ' + token}
        url = 'https://order-pizza-api.herokuapp.com/api/orders'
        pizzaOrder.table_number = pizzaOrder.id + 30000
        data = {
            'Crust': pizzaOrder.crust,
            'Flavor': pizzaOrder.flavor,
            'Size': pizzaOrder.size,
            'Table_No': pizzaOrder.table_number,
        }
        response = requests.post(url=url, json=data, headers=hed)
        if response.status_code != 201:
            raise serializers.ValidationError()
        responseData = json.loads(response.content)
        return responseData['Table_No'], responseData['Order_ID'], responseData['Timestamp']

    def attemptToSendPizzaOrder(self, pizzaOrder, token):
        # We try sending the pizza order to the pizzeria 5 times
        # If all of that fails then we return to the user with that
        attempts = 3
        for i in range(attempts):
            try:
                table_number, order_id, timestamp = self.sendPizzaOrder(pizzaOrder, token)
                return table_number, order_id, timestamp
            except serializers.ValidationError:
                # It pretty much only fails because the table_no is taken, which
                # shouldn't happen since my table numbers are based on the id's
                # which have to be unique, but if it does come back with that error
                # i'll just randomly add some amount to the table number and try that
                pizzaOrder.table_number += random.randint(100, 10000)
                # The third time it fails just give up
                if(i == attempts - 1):
                    raise serializers.ValidationError(
                        {'error': "Error sending order to pizzeria."})

    def create(self, validated_data):
        # When it gets created it will gain a unique ID, which I can use to make
        # a unique table_no later. I know table_no's eventually become reusable,
        # so I should try to find a way to utilize that rather than just running
        # up the table_no forever
        tempPizzaOrder = PizzaOrder.objects.create(
            flavor=validated_data.get('flavor'),
            size=validated_data.get('size'),
            crust=validated_data.get('crust'),
            ordered_by=self.context.get('ordered_by'))

        token = self.pizzeriaLogin()
        table_number, order_number, timestamp = self.attemptToSendPizzaOrder(tempPizzaOrder, token)

        tempPizzaOrder.order_id = order_number
        tempPizzaOrder.table_number = table_number
        tempPizzaOrder.timestamp = parser.parse(timestamp)
        tempPizzaOrder.save()
        return tempPizzaOrder

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['Order_ID'] = instance.order_id
        rep['Table_No'] = instance.table_number
        rep['Timestamp'] = instance.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")
        return rep
