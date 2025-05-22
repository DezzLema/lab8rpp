from django.urls import path
from . import views

urlpatterns = [
    path('', views.receipt_list, name='receipt_list'),
    path('<int:pk>/', views.receipt_detail, name='receipt_detail'),
    path('new/', views.receipt_create, name='receipt_create'),
    path('<int:pk>/edit/', views.receipt_update, name='receipt_update'),
    path('<int:pk>/delete/', views.receipt_delete, name='receipt_delete'),
]