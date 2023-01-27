from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from .models import Profile
from accounts.models import Cart, CartItem
from .models import Coupon, Product, SizeVariant
from django.contrib import messages
from ecomm import settings
import razorpay
def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_obj = User.objects.filter(email = email)

        if not user_obj.exists():
            messages.warning(request, 'Account not found')
            return HttpResponseRedirect(request.path_info)
        user_obj = authenticate(username=email , password=password)

        if not user_obj.profile.is_email_verified:
            messages.warning(request,'Your account is not verified.')

        if user_obj:
            login(request, user_obj)
            return redirect('/')
        messages.warning(request, 'Invalid creadentials')
        return HttpResponseRedirect(request.path_info)
        

    return render(request,'accounts/login.html')

def register_page(request):

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_obj = User.objects.filter(email = email)

        if user_obj.exists():
            messages.warning(request, 'Email is already taken.')
            return HttpResponseRedirect(request.path_info)

        user_obj = User.objects.create(first_name=first_name, last_name=last_name, email=email, username=email)
        user_obj.set_password(password)
        user_obj.save()
        messages.success(request, 'An email has been sent on your mail.')
        return HttpResponseRedirect(request.path_info)
    return render(request,'accounts/register.html')


def activate_email(request, email_token):
    try:
        user = Profile.objects.get(email_token=email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/')
    except Exception as e:
         return HttpResponse('Invalid Email token')



def add_to_cart(request, uid):
     
    variant = request.GET.get('variant')
    product = Product.objects.get(uid=uid)
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)
    cart_item = CartItem.objects.create(cart=cart,product=product)

    if variant:
       variant = request.GET.get('variant')
       size_variant = SizeVariant.objects.get(size_name = variant)
       cart_item.size_variant = size_variant
       cart_item.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def remove_from_cart(request,cart_item_uid):
    cart_item = CartItem.objects.get(uid=cart_item_uid)
    cart_uid = cart_item.cart.uid
    cart_item.delete()
    cart = Cart.objects.get(pk=cart_uid)
    if cart.coupon:
        if cart.get_total_price() < cart.coupon.minimum_amount:
            cart.coupon = None
            cart.save()
    if cart.cart_items.all().count()==0:
        cart.delete()
    # if cart.coupon:
    return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 


def cart(request):
    cart =  Cart.objects.filter(is_paid=False, user=request.user)
    if cart:
        client = razorpay.Client(auth=(settings.razor_pay_key_id, settings.key_secret))
        data = { "amount": cart[0].get_discounted_price()*100, "currency": "INR", "receipt": "order_rcptid_11" }
        payment = client.order.create(data=data)
        contex = {'cart' : cart[0],'payment':payment,'key':settings.razor_pay_key_id}
        cart[0].razorpay_order_id = payment['id']
        cart[0].save()
        print(contex)
        return render(request, 'accounts/cart.html',contex)
    return render(request, 'accounts/cart.html')


def apply_coupon(request):
    if request.method == 'POST':
        cart = Cart.objects.get(user=request.user, is_paid=False)
        try:
            coupon = Coupon.objects.get(coupon_code=request.POST.get('coupon_code'))
        except:
            messages.warning(request,"Invalid Coupon")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 
        if cart.get_total_price() < coupon.minimum_amount:
            messages.warning(request,f"The Minimum Amount for Coupon is {coupon.minimum_amount}")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if cart.coupon:
             messages.warning(request,"Coupon Already In Use")
        else:
            if coupon:
                if coupon.is_expired:
                    messages.warning(request,"Coupon is Expired")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            cart.coupon = coupon
            cart.save()
            coupon.is_expired = True
            coupon.save()
            messages.success(request,"Coupon Aplied")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 

def remove_coupon(request):
    cart = Cart.objects.get(user=request.user, is_paid=False)
    cart.coupon = None
    cart.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def success(request):
    razorpay_order_id = request.GET.get('order_id')
    razorpay_payment_id = request.GET.get('razorpay_payment_id')
    razorpay_signature = request.GET.get('razorpay_signature')
    cart = Cart.objects.get(razorpay_order_id=razorpay_order_id)
    cart.razorpay_payment_id = razorpay_payment_id
    cart.razorpay_signature = razorpay_signature
    cart.is_paid = True
    if cart.coupon:
        cart.coupon.is_expired = True
    cart.save()
    return HttpResponse('Payment Success')