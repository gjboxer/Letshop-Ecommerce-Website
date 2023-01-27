from django.urls import path
from .views import  get_products

urlpatterns = [
    path('<slug>/',get_products,name='get_products')
]

