from django.urls import path

from .views import PizzaCreateListView, PizzaDetailView

urlpatterns = [
    path('', PizzaCreateListView.as_view(), name='pizza_create_list'),
    path('<int:Order_ID>', PizzaDetailView.as_view(), name='pizza_detail'),
]
