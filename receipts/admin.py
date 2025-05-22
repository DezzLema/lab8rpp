from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Store, Customer, ProductCategory, Product, Receipt, ReceiptProduct

admin.site.register(Store)
admin.site.register(Customer)
admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(Receipt)
admin.site.register(ReceiptProduct)