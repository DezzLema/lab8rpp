from django.urls import path, include
from . import views
from django.contrib.auth.decorators import user_passes_test


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            from django.contrib.auth.views import redirect_to_login
            from django.urls import reverse
            return redirect_to_login(reverse('employee_list'))
        return view_func(request, *args, **kwargs)

    return wrapper


urlpatterns = [
    path('', views.receipt_list, name='receipt_list'),
    path('<int:pk>/', views.receipt_detail, name='receipt_detail'),
    path('new/', views.receipt_create, name='receipt_create'),
    path('<int:pk>/edit/', views.receipt_update, name='receipt_update'),
    path('<int:pk>/delete/', views.receipt_delete, name='receipt_delete'),

    # Новые URL для других сущностей
    path('employees/', admin_required(views.employee_list), name='employee_list'),
    path('stores/', views.store_list, name='store_list'),
    path('stores/new/', views.store_create, name='store_create'),
    path('stores/<int:pk>/edit/', views.store_update, name='store_update'),
    path('stores/<int:pk>/delete/', views.store_delete, name='store_delete'),
    path('stores/', views.store_list, name='store_list'),
    path('stores/new/', views.store_create, name='store_create'),
    path('stores/<int:pk>/edit/', views.store_update, name='store_update'),
    path('stores/<int:pk>/delete/', views.store_delete, name='store_delete'),

    path('customers/', views.customer_list, name='customer_list'),
    path('customers/new/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),

    path('products/', views.product_list, name='product_list'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    path('categories/', views.category_list, name='category_list'),
    path('categories/new/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Аутентификация
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name='register'),
]
