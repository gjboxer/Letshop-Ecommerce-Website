from django.contrib import admin
from .models import Cart, CartItem, Profile
# Register your models here.

admin.site.register(Profile)
admin.site.register(Cart)
admin.site.register(CartItem)
