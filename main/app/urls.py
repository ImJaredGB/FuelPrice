from django.urls import path
from .views import fuel
urlpatterns = [
    path('fuel/', fuel, name='fuel'),
]