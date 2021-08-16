from rest_framework.generics import ListCreateAPIView

from .serializers import PizzaOrderSerializer


class PizzaCreateListView(ListCreateAPIView):
    """
    View for creating and getting pizza orders
    """
    serializer_class = PizzaOrderSerializer
