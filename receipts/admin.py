from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.contrib import admin
from .models import Store, Customer, ProductCategory, Product, Receipt, ReceiptProduct


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Store)
admin.site.register(Customer)
admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(Receipt)
admin.site.register(ReceiptProduct)