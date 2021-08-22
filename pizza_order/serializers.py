import json
from json.decoder import JSONDecodeError
import random

import requests
from dateutil import parser
from rest_framework import serializers

from .models import PizzaOrder


class PizzaOrderSerializer(serializers.Serializer):
    class Meta:
        module = PizzaOrder

    Flavor = serializers.ChoiceField([item[0] for item in PizzaOrder.FLAVOR_CHOICES])
    Size = serializers.ChoiceField([item[0] for item in PizzaOrder.SIZE_CHOICES])
    Crust = serializers.ChoiceField([item[0] for item in PizzaOrder.CRUST_CHOICES])
    Order_ID = serializers.IntegerField(read_only=True)
    Table_No = serializers.IntegerField(read_only=True)
    Timestamp = serializers.DateTimeField(read_only=True)

    def pizzeriaLogin(self, pizzaOrder):
        # First we log in to the pizza place to get a fresh token
        # If the login fails, we delete the pizza in our db since the pizzeria
        # obviously won't recieve it
        url = 'https://order-pizza-api.herokuapp.com/api/auth'
        data = {'username': 'test', 'password': 'test'}
        response = requests.post(url=url, json=data)

        # First we make sure the request was successfull
        if response.status_code != 200:
            pizzaOrder.delete()
            raise serializers.ValidationError({'error': "Error logging in to pizzeria."})

        # Next we make sure we got a valid json
        try:
            responseData = json.loads(response.content)
        except JSONDecodeError:
            pizzaOrder.delete()
            raise serializers.ValidationError({'error': "Did not receive valid json from pizzeria."})

        if 'access_token' not in responseData:
            pizzaOrder.delete()
            raise serializers.ValidationError({'error': "Did not receive a token from pizzeria."})
        return responseData['access_token']

    # This function actually sends the order to the pizzeria
    def sendPizzaOrder(self, pizzaOrder, token):
        hed = {'Authorization': 'Bearer ' + token}
        url = 'https://order-pizza-api.herokuapp.com/api/orders'

        # If the pizza order number is not set yet, we set it to the 
        # unique id and add 30000, otherwise it is fine
        if pizzaOrder.Table_No == None:
            pizzaOrder.Table_No = pizzaOrder.id + 30000
        data = {
            'Crust': pizzaOrder.Crust,
            'Flavor': pizzaOrder.Flavor,
            'Size': pizzaOrder.Size,
            'Table_No': pizzaOrder.Table_No,
        }
        response = requests.post(url=url, json=data, headers=hed)

        # Make sure the order was created
        if response.status_code != 201:
            raise serializers.ValidationError()
        
        # Make sure we got a well formed json response
        try:
            responseData = json.loads(response.content)
        except ValueError:
            raise serializers.ValidationError({'error': "Couldn't parse login return."})

        return responseData

    # This function takes care of the different pizzeria order attempts.
    def attemptToSendPizzaOrder(self, pizzaOrder, token):
        # We try sending the pizza order to the pizzeria 3 times
        # If every attempt fails, we give up and return that it failed to the user
        attempts = 3
        for i in range(attempts):
            try:
                responseData = self.sendPizzaOrder(pizzaOrder, token)
                return responseData
            except serializers.ValidationError:
                # The only time sending an error fails is when the table_no already exists
                # This should never happen, but in the event it does we try three times, adding
                # a random number to the table number in the hopes that one won't be taken.
                pizzaOrder.Table_No += random.randint(1000, 10000)

                # The third time it fails just give up and deletes out entry for the pizza
                # order
                if(i == attempts - 1):
                    # Delete the pizza order on our end if the order doesn't go through
                    pizzaOrder.delete()
                    raise serializers.ValidationError(
                        {'error': "Error sending order to pizzeria."})

    def create(self, validated_data):
        # When it gets created it will auto-generate a unique ID, which I can use to make
        # a unique table_no later.
        tempPizzaOrder = PizzaOrder.objects.create(
            Flavor=validated_data.get('Flavor'),
            Size=validated_data.get('Size'),
            Crust=validated_data.get('Crust'),
            Ordered_By=self.context.get('Ordered_By')
        )

        token = self.pizzeriaLogin(tempPizzaOrder)
        responseData = self.attemptToSendPizzaOrder(tempPizzaOrder, token)

        # Need to update my model with the order_id, table_no, and timestamp
        # the pizzeria returns
        tempPizzaOrder.Order_ID = responseData['Order_ID']
        tempPizzaOrder.Table_No = responseData['Table_No']
        # Beautiful auto-timestamp parser makes the work easy
        tempPizzaOrder.Timestamp = parser.parse(responseData['Timestamp'])
        tempPizzaOrder.save()

        return tempPizzaOrder

    # The normal output is fine, but I like to customize the date output in the model and use that
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['Timestamp'] = instance.timeAsString()
        return rep
