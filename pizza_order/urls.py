from django.urls import path

from .views import PizzaCreateListView

urlpatterns = [
    path('', PizzaCreateListView.as_view(), name='pizza_create_list'),
]
