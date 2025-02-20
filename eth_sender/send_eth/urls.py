from django.urls import path
from .views import send_eth

urlpatterns = [
    path('', send_eth, name='send_eth'),
]
