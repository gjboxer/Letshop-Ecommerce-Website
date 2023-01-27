from django.urls import path
from .views import login_page, register_page, activate_email
from . views import add_to_cart, cart, remove_coupon, remove_from_cart, apply_coupon, success

urlpatterns = [
    path('login/', login_page, name='login' ),
    path('register/', register_page, name='register' ),
    path('activate-email/<email_token>/', activate_email, name='activate-email' ),
    path('add_to_cart/<uid>',add_to_cart,name='add_to_cart'),
    path('remove_from_cart/<cart_item_uid>',remove_from_cart,name='remove_from_cart'),
    path('cart/',cart,name='cart'),
    path('apply_coupon/',apply_coupon,name='apply_coupon'),
    path('remove_coupon/',remove_coupon,name='remove_coupon'),
    path('success/',success,name='success'),
]

