from django.urls import path

from .views import PizzaCreateListView, PizzaDetailView

# If the url has no order id, it is either creating a pizza or getting a list of orders
# If the url has an order id, it is either getting an individual order or deleting one
urlpatterns = [
    path('', PizzaCreateListView.as_view(), name='pizza_create_list'),
    path('<int:Order_ID>', PizzaDetailView.as_view(), name='pizza_detail'),
]
