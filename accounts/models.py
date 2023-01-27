from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from base.emails import send_account_activation_email
from products.models import ColorVariant, Coupon, Product, SizeVariant
class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100, null=True, blank=True)
    profile_image = models.ImageField(upload_to="profile", null=True, blank=True)

    def get_cart_count(self):
        return CartItem.objects.filter(cart__is_paid=False, cart__user= self.user).count()

@receiver(post_save, sender=User)
def send_email_token(sender, instance, created, **kwargs):
    try:
        if created:
            email_token = str(uuid.uuid4())
            Profile.objects.create(user=instance, email_token=email_token)
            email = instance.email
            send_account_activation_email(email, email_token)

    except Exception as e:
        print(e)


class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=100, null=True, blank=True)
    def get_total_price(self):
        cart_items = self.cart_items.all()
        total_price = []
        for cart_item in cart_items:
            print(cart_item.product.price)
            total_price.append(cart_item.product.price)
            if cart_item.color_variant:
                total_price.append(cart_item.color_variant.price)
            if cart_item.size_variant:
                total_price.append(cart_item.size_variant.price)
        return sum(total_price)

    def get_discounted_price(self):
        if self.coupon:
            return self.get_total_price() - self.coupon.discount_price
        else:
            return self.get_total_price()

class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    color_variant = models.ForeignKey(ColorVariant, on_delete=models.SET_NULL, null=True, blank=True)
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.SET_NULL, null=True, blank=True)

    def get_product_price(self):
        price = [self.product.price]

        if self.size_variant:
            size_variant_price = self.size_variant.price
            price.append(size_variant_price)
            
        if self.color_variant:
            color_variant_price = self.color_variant.price
            price.append(color_variant_price)
            
        return sum(price)




