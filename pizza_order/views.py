import requests
from rest_framework import authentication, status
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import PizzaOrder
from .serializers import PizzaOrderSerializer


class PizzaCreateListView(ListCreateAPIView):
    """
    View for creating and getting pizza orders
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = [authentication.TokenAuthentication]
    serializer_class = PizzaOrderSerializer
    queryset = PizzaOrder.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(ordered_by=self.request.user)

    def get_serializer_context(self):
        return {'ordered_by': self.request.user}


class PizzaDetailView(RetrieveDestroyAPIView):
    """
    View for deleting and getting single pizzas
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = [authentication.TokenAuthentication]
    serializer_class = PizzaOrderSerializer
    queryset = PizzaOrder.objects.all()
    lookup_field = 'order_id'

    def get_queryset(self):
        return super().get_queryset().filter(ordered_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        url = 'https://order-pizza-api.herokuapp.com/api/orders/' + str(instance.order_id)

        response = requests.delete(url=url)
        if response.status_code != 200:
            error = {'non_field_error': 'Could not cancel order with pizzeria.'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
