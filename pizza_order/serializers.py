import json

import requests
from rest_framework import serializers

from .models import PizzaOrder


class PizzaOrderSerializer(serializers.Serializer):
    class Meta:
        module = PizzaOrder

    flavor = serializers.ChoiceField([item[0] for item in PizzaOrder.FLAVOR_CHOICES])
    size = serializers.ChoiceField([item[0] for item in PizzaOrder.SIZE_CHOICES])
    crust = serializers.ChoiceField([item[0] for item in PizzaOrder.CRUST_CHOICES])

    def create(self, validated_data):
        tempPizzaOrder = PizzaOrder(
            flavor=validated_data.get('flavor'),
            size=validated_data.get('size'),
            crust=validated_data.get('crust')
        )
        tempPizzaOrder.save()
        tempPizzaOrder.table_number = tempPizzaOrder.id + 30000
        validated_data['Table_No'] = tempPizzaOrder.table_number

        # First we log in to the pizza place to get a fresh token
        url = 'https://order-pizza-api.herokuapp.com/api/auth'
        # Might make the login data env variables to keep them hidden
        data = {'username': 'test', 'password': 'test'}
        response = requests.post(url=url, json=data)
        if response.status_code != 200:
            raise serializers.ValidationError({'error': "Couldn't log in to pizzeria."})
        try:
            responseData = json.loads(response.content)
        except ValueError:
            raise serializers.ValidationError({'error': "Couldn't parse login return."})
        token = responseData['access_token']
        hed = {'Authorization': 'Bearer ' + token}
        url = 'https://order-pizza-api.herokuapp.com/api/orders'
        data = {
            'Crust': tempPizzaOrder.crust,
            'Flavor': tempPizzaOrder.flavor,
            'Size': tempPizzaOrder.size,
            'Table_No': tempPizzaOrder.table_number,
        }
        response = requests.post(url=url, json=data, headers=hed)
        if response.status_code != 201:
            raise serializers.ValidationError({'error': "Error sending order to pizzaria."})
        try:
            responseData = json.loads(response.content)
        except ValueError:
            raise serializers.ValidationError({'error': "Couldn't parse order return."})
        tempPizzaOrder.order_id = responseData.get('Order_ID')
        tempPizzaOrder.save()
        return tempPizzaOrder

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['Order_ID'] = instance.order_id
        rep['Table_No'] = instance.table_number
        return rep
