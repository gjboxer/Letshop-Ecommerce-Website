from django.contrib import admin
from .models import Category, Product, ProductImage, ColorVariant, SizeVariant, Coupon
# Register your models here.

admin.site.register(Category)

class ProductImageAdmin(admin.StackedInline):
    model = ProductImage

class ProductImageAdmin(admin.StackedInline):
    model = ProductImage

@admin.register(ColorVariant)
class ColorVariantAdmin(admin.ModelAdmin):
    list_display = ['color_name','price']
    model = ColorVariant

@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):
    list_display = ['size_name','price']
    model = SizeVariant
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name','price']
    inlines = [ProductImageAdmin]

admin.site.register(Product,ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Coupon)
