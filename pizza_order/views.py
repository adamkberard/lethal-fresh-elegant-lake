from rest_framework.generics import ListCreateAPIView

from .serializers import PizzaOrderSerializer

from .models import PizzaOrder


class PizzaCreateListView(ListCreateAPIView):
    """
    View for creating and getting pizza orders
    """
    serializer_class = PizzaOrderSerializer
    queryset = PizzaOrder.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(ordered_by=self.request.user)
    
    def get_serializer_context(self):
        return {'ordered_by': self.request.user}
