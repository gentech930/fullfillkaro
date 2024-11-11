from django.contrib import admin
from .models import Product, Category, ProductOption, Bundle,Cart
from .models import *

admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Cart)


class BundleInline(admin.TabularInline):
    model = Bundle
    extra = 0  # Shows 3 empty forms for adding bundles by default
    min_num = 0  # Minimum number of bundles
    max_num = 3  # Maximum number of bundles

class ProductAdmin(admin.ModelAdmin):
    inlines = [BundleInline]  # Adding the BundleInline here to manage bundles in the product admin

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(ProductOption)
admin.site.register(Bundle)
