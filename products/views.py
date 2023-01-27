from django.shortcuts import render

from products.models import Product


def get_products(request,slug):
    product = Product.objects.get(slug=slug)
    context = {'product':product}
    if request.GET.get('size'):
        size = request.GET.get('size')
        price = product.get_price_by_size(size)
        context['selected_size'] = size
        context['updated_price'] = price
    return render(request, 'product/products.html',context)
