from collections import OrderedDict

import requests
from drf_yasg import openapi
from rest_framework import authentication, status
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import PizzaOrder
from .serializers import PizzaOrderSerializer


class PizzaCreateListView(ListCreateAPIView):
    """
    View for creating and getting pizza orders.
    Must be authenticated
    **POSTS can also accept a LIST of pizza orders**
    **This will respond with a list of the finalized orders** 
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = [authentication.TokenAuthentication]
    serializer_class = PizzaOrderSerializer
    queryset = PizzaOrder.objects.all()

    # This makes sure users get a list of pizza orders only made by them
    def get_queryset(self):
        return super().get_queryset().filter(Ordered_By=self.request.user)

    # This passes information along to the serializer so it can add who ordered the pizza
    # to the order
    def get_serializer_context(self):
        return {'Ordered_By': self.request.user}

    # This changes the serializer to work with either single json objects passed in,
    # or lists of json objects so users can order a single pizza or multiple pizzas
    # in the same request
    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)


failedDeleteResponseSchema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties=OrderedDict((("non_field_error", openapi.Schema(type=openapi.TYPE_STRING)),)),
    required=[]
)


class PizzaDetailView(RetrieveDestroyAPIView):
    """
    View for deleting and getting single pizzas.
    Must be authenticated
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = [authentication.TokenAuthentication]
    serializer_class = PizzaOrderSerializer
    queryset = PizzaOrder.objects.all()
    lookup_field = 'Order_ID'

    # This ensure's users can only delete or view orders that belong to them
    def get_queryset(self):
        return super().get_queryset().filter(Ordered_By=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Here is where we delete the order with the pizzeria, if it fails we also
        # do not delete it within our database
        url = 'https://order-pizza-api.herokuapp.com/api/orders/' + str(kwargs['Order_ID'])
        response = requests.delete(url=url)
        if response.status_code != 200:
            error = {'non_field_error': 'Could not cancel order with pizzeria.'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
